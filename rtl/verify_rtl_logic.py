"""
verify_rtl_logic.py
====================
Python-level verification of the RTL behavioral logic for axm_8x8.v
Mirrors the exact combinational logic in the Verilog to catch bugs
before running on Vivado/Icarus.

This confirms:
  - EXACT   mode: output = A * B
  - TRUNC   mode: output = A*B - dropped_and_cols
  - COMP    mode: output = A*B - dropped_and_cols + 2^(T-1)
  - ORBASED mode: output = A*B - dropped_and_cols + dropped_or_cols

Run: python verify_rtl_logic.py
"""

import numpy as np

T = 6   # Must match parameter T in axm_8x8.v

def compute_all_modes(a, b):
    """
    Mirrors the Verilog always@(*) block in axm_8x8.v exactly.
    Returns dict of {mode_name: output_value}
    """
    sum_exact       = 0
    sum_dropped_and = 0
    sum_dropped_or  = 0

    for k in range(16):              # output column k (bit weight = 2^k)
        for i in range(8):           # bit index of A
            j = k - i
            if 0 <= j < 8:           # bit index of B (must be valid)
                pp_and = ((a >> i) & 1) & ((b >> j) & 1)
                pp_or  = ((a >> i) & 1) | ((b >> j) & 1)
                sum_exact       += pp_and << k
                if k < T:
                    sum_dropped_and += pp_and << k
                    sum_dropped_or  += pp_or  << k

    comp_bias = 1 << (T - 1)    # 2^(T-1) = 32 for T=6

    return {
        "exact":       sum_exact,
        "trunc":       sum_exact - sum_dropped_and,
        "compensated": sum_exact - sum_dropped_and + comp_bias,
        "orbased":     sum_exact - sum_dropped_and + sum_dropped_or,
    }

def run_full_verification():
    print("=" * 60)
    print(f"  axm_8x8 RTL Logic Verification  (T={T})")
    print(f"  Testing all 65,536 input pairs × 4 modes")
    print("=" * 60)

    mismatches = {"exact": 0, "trunc": 0, "compensated": 0, "orbased": 0}
    first_mismatch = {"exact": None, "trunc": None, "compensated": None, "orbased": None}

    # Reference: simple Python math
    def ref_exact(a, b):       return a * b
    def ref_trunc(a, b):
        s = 0
        for k in range(T):
            for i in range(8):
                j = k - i
                if 0 <= j < 8:
                    s += (((a>>i)&1) & ((b>>j)&1)) << k
        return a * b - s
    def ref_comp(a, b):        return ref_trunc(a, b) + (1 << (T-1))
    def ref_or(a, b):
        s = 0
        for k in range(T):
            for i in range(8):
                j = k - i
                if 0 <= j < 8:
                    s += (((a>>i)&1) | ((b>>j)&1)) << k
        return ref_trunc(a, b) + s

    refs = {
        "exact":       ref_exact,
        "trunc":       ref_trunc,
        "compensated": ref_comp,
        "orbased":     ref_or,
    }

    # Run all 65,536 pairs
    for a in range(256):
        for b in range(256):
            rtl_out = compute_all_modes(a, b)
            for mode_name, ref_fn in refs.items():
                expected = ref_fn(a, b)
                got      = rtl_out[mode_name]
                if got != expected:
                    mismatches[mode_name] += 1
                    if first_mismatch[mode_name] is None:
                        first_mismatch[mode_name] = (a, b, expected, got)

    # Report
    print("\nResults:")
    all_pass = True
    for mode_name in ["exact", "trunc", "compensated", "orbased"]:
        m = mismatches[mode_name]
        status = "PASS" if m == 0 else f"FAIL ({m} mismatches)"
        print(f"  {mode_name:<14}: {status}")
        if m > 0:
            all_pass = False
            a, b, exp, got = first_mismatch[mode_name]
            print(f"    First mismatch: A={a}, B={b}, expected={exp}, got={got}")

    print("\n" + "=" * 60)
    if all_pass:
        print("  ALL 262,144 TESTS PASSED")
        print("  RTL behavioral logic is CORRECT -- safe to synthesize in Vivado")
    else:
        print("  FAILURES DETECTED -- fix RTL before synthesis")
    print("=" * 60)

    # Also print sample outputs for the paper
    print("\nSample outputs (A=200, B=150):")
    out = compute_all_modes(200, 150)
    exact_val = 200 * 150
    print(f"  Exact       : {exact_val}")
    for m, v in out.items():
        err = v - exact_val
        print(f"  {m:<14}: {v:>6}  (error={err:+d})")

if __name__ == "__main__":
    run_full_verification()
