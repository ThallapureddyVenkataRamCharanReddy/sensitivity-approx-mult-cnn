"""
generate_trunc6_tables.py
=========================
Generates the 256×256 lookup tables for the TRUNC=6 multiplier library.

BEHAVIORAL MODELS — verified against all 65,536 pairs of the real Vivado
TRUNC=4 simulation (0 mismatches):

  trunc(a,b,T):
    For each bit-pair (i,j): if i+j >= T, include a_i AND b_j * 2^(i+j)
    i.e., drop partial-product columns 0..T-1 entirely.

  orbased(a,b,T):
    Retained columns (i+j >= T): exact AND (same as trunc)
    Dropped columns (i+j < T): use OR(a_i, b_j) and ADD their sum to result.
    orbased = trunc_AND_retained + sum_{k=0}^{T-1} [sum_{i+j=k} (a_i OR b_j)] * 2^k

  compensated(a,b,T):
    compensated = trunc + 2^(T-1)   [constant rounding bias, always added]
    Matches CSV pattern: compensated - trunc = 8 = 2^(4-1) for all 65536 pairs.

Writes: axm_tables_t6.npz, axm_results_t6.csv
"""

import numpy as np
import pandas as pd
import time

T = 6   # truncation bits
N = 8   # operand width

print(f"Generating TRUNC={T} lookup tables for {N}x{N} unsigned multipliers ...")
print(f"Drop columns 0..{T-1}, retain {T}..{2*N-2}")
t0 = time.time()

a_arr = np.arange(256, dtype=np.int64)
b_arr = np.arange(256, dtype=np.int64)
A, B = np.meshgrid(a_arr, b_arr, indexing='ij')   # (256,256)

exact = (A * B).astype(np.int64)

# ── Truncated: sum_{i+j >= T} a_i AND b_j * 2^(i+j) ─────────────────────────
# Equivalent to exact minus the error from dropped columns
error_term = np.zeros((256, 256), dtype=np.int64)
for k in range(T):                  # each dropped column
    col = np.zeros((256, 256), dtype=np.int64)
    for i in range(min(k + 1, N)):
        j = k - i
        if 0 <= j < N:
            ai = (A >> i) & 1
            bj = (B >> j) & 1
            col += ai * bj          # AND (exact partial product bit)
    error_term += col * (1 << k)

trunc = (exact - error_term).astype(np.int32)

# ── OR-based: retained columns AND, dropped columns OR ───────────────────────
or_dropped = np.zeros((256, 256), dtype=np.int64)
for k in range(T):
    col = np.zeros((256, 256), dtype=np.int64)
    for i in range(min(k + 1, N)):
        j = k - i
        if 0 <= j < N:
            ai = (A >> i) & 1
            bj = (B >> j) & 1
            col += (ai | bj)        # OR
    or_dropped += col * (1 << k)

orbased = (trunc.astype(np.int64) + or_dropped).astype(np.int32)

# ── Compensated: trunc + 2^(T-1) always ─────────────────────────────────────
rounding_const = 1 << (T - 1)   # 32 for T=6
compensated = (trunc.astype(np.int64) + rounding_const).astype(np.int32)

print(f"  Done in {time.time()-t0:.2f}s")

# ── Validation against real Vivado TRUNC=4 data ───────────────────────────────
print("\nValidation against real Vivado axm_results.csv (TRUNC=4):")
try:
    df4 = pd.read_csv("axm_results.csv")
    # Check trunc model
    T4 = 4
    err4 = np.zeros((256, 256), dtype=np.int64)
    A4, B4 = A.copy(), B.copy()
    for k4 in range(T4):
        col4 = np.zeros((256, 256), dtype=np.int64)
        for i4 in range(min(k4 + 1, N)):
            j4 = k4 - i4
            if 0 <= j4 < N:
                col4 += ((A4 >> i4) & 1) * ((B4 >> j4) & 1)
        err4 += col4 * (1 << k4)
    trunc4_model = (exact - err4).astype(np.int32).ravel()
    trunc4_csv = np.array(df4['trunc'].values, dtype=np.int32)
    mismatches = np.sum(trunc4_model != trunc4_csv)
    print(f"  TRUNC=4 model vs CSV: {mismatches} mismatches / 65536  {'✓ PASS' if mismatches==0 else '✗ FAIL'}")

    # Check OR-based model for T=4
    or4 = np.zeros((256, 256), dtype=np.int64)
    for k4 in range(T4):
        col4 = np.zeros((256, 256), dtype=np.int64)
        for i4 in range(min(k4 + 1, N)):
            j4 = k4 - i4
            if 0 <= j4 < N:
                col4 += ((A4 >> i4) & 1) | ((B4 >> j4) & 1)
        or4 += col4 * (1 << k4)
    orbased4_model = (trunc4_model.reshape(256,256) + or4).astype(np.int32).ravel()
    orbased4_csv = np.array(df4['orbased'].values, dtype=np.int32)
    mis_or = np.sum(orbased4_model != orbased4_csv)
    print(f"  OR-based T=4 model vs CSV: {mis_or} mismatches / 65536  {'✓ PASS' if mis_or==0 else '✗ FAIL'}")

    # Check compensated model for T=4
    comp4_model = (trunc4_model.reshape(256,256) + (1 << (T4-1))).astype(np.int32).ravel()
    comp4_csv = np.array(df4['compensated'].values, dtype=np.int32)
    mis_comp = np.sum(comp4_model != comp4_csv)
    print(f"  Compensated T=4 model vs CSV: {mis_comp} mismatches / 65536  {'✓ PASS' if mis_comp==0 else '✗ FAIL'}")
except Exception as e:
    print(f"  Validation skipped: {e}")

# ── Error statistics ──────────────────────────────────────────────────────────
err_trunc = np.abs(exact - trunc.astype(np.int64))
err_or    = np.abs(exact - orbased.astype(np.int64))
err_comp  = np.abs(exact - compensated.astype(np.int64))

print(f"\nTRUNC={T} library error statistics (unsigned 8×8):")
print(f"  {'Design':<14} {'mean_err':>10} {'max_err':>10} {'nonzero':>10}")
print(f"  {'exact':<14} {'0.00':>10} {'0':>10} {'0':>10}")
print(f"  {'trunc':<14} {err_trunc.mean():>10.2f} {err_trunc.max():>10.0f} {(err_trunc>0).sum():>10}")
print(f"  {'orbased':<14} {err_or.mean():>10.2f} {err_or.max():>10.0f} {(err_or>0).sum():>10}")
print(f"  {'compensated':<14} {err_comp.mean():>10.2f} {err_comp.max():>10.0f} {(err_comp>0).sum():>10}")

t4_trunc_mean = 12.25   # from real TRUNC=4 Vivado CSV
print(f"\n  Error amplification TRUNC=6 vs TRUNC=4 (trunc): {err_trunc.mean()/t4_trunc_mean:.1f}×")

# ── Save outputs ──────────────────────────────────────────────────────────────
np.savez("axm_tables_t6.npz",
         exact=exact.astype(np.int32),
         trunc=trunc,
         orbased=orbased,
         compensated=compensated)
print(f"\nSaved axm_tables_t6.npz")

df_out = pd.DataFrame({
    'a': A.ravel(), 'b': B.ravel(),
    'exact': exact.ravel(),
    'trunc': trunc.ravel(),
    'orbased': orbased.ravel(),
    'compensated': compensated.ravel(),
})
df_out.to_csv("axm_results_t6.csv", index=False)
print(f"Saved axm_results_t6.csv ({len(df_out)} rows)")
print(f"\nTotal: {time.time()-t0:.2f}s — run layerwise_sweep_t6.py next.")
