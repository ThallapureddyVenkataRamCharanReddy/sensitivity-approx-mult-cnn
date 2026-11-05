"""
correlation_analysis_t6.py
===========================
Runs the Spearman correlation analysis between each of the 5 sensitivity
scores (S1–S5, from sensitivity_scores.csv) and the mean accuracy drop
observed in the TRUNC=6 layer-wise sweep (layerwise_results_t6.csv).

Also runs per-multiplier correlations (not just mean-drop) to give a
more detailed picture, and performs the formal GO/NO-GO decision.

Writes:
  correlation_results_t6.csv
  go_nogo_t6.txt
"""
import pandas as pd, numpy as np
from scipy.stats import spearmanr

sens   = pd.read_csv("sensitivity_scores.csv")
lw     = pd.read_csv("layerwise_results_t6.csv")

LAYERS  = ["conv1", "conv2", "conv3", "conv4"]
metrics = sens["metric"].unique()

# ── 1. Mean drop per layer (averaged over 3 multipliers) ──────────────────────
mean_drop = lw.groupby("layer")["accuracy_drop"].mean().to_dict()
print("Mean accuracy drop per layer (TRUNC=6):")
for l in LAYERS:
    print(f"  {l}: {mean_drop[l]:+.4f}%")

# ── 2. Max drop per layer (worst-case multiplier) ─────────────────────────────
max_drop = lw.groupby("layer")["accuracy_drop"].max().to_dict()
print("\nMax accuracy drop per layer (TRUNC=6):")
for l in LAYERS:
    print(f"  {l}: {max_drop[l]:+.4f}%")

# ── 3. Spearman correlation — mean drop ───────────────────────────────────────
print(f"\n{'Metric':<20}{'rho (mean_drop)':>18}{'p-value':>12}{'|rho|':>8}")
print("-" * 60)
results = []
for m in metrics:
    scores = sens[sens["metric"] == m].set_index("layer")["value"]
    x = [scores[l] for l in LAYERS]
    y_mean = [mean_drop[l] for l in LAYERS]
    y_max  = [max_drop[l] for l in LAYERS]
    rho_mean, p_mean = spearmanr(x, y_mean)
    rho_max,  p_max  = spearmanr(x, y_max)
    results.append({
        "metric": m,
        "rho_mean_drop": rho_mean,
        "p_mean_drop": p_mean,
        "rho_max_drop": rho_max,
        "p_max_drop": p_max,
    })
    print(f"{m:<20}{rho_mean:>18.3f}{p_mean:>12.3f}{abs(rho_mean):>8.3f}")

df_res = pd.DataFrame(results)
df_res.to_csv("correlation_results_t6.csv", index=False)
print("\nSaved correlation_results_t6.csv")

# ── 4. Also show max-drop correlations ────────────────────────────────────────
print(f"\n{'Metric':<20}{'rho (max_drop)':>18}{'p-value':>12}{'|rho|':>8}")
print("-" * 60)
for r in results:
    print(f"{r['metric']:<20}{r['rho_max_drop']:>18.3f}{r['p_max_drop']:>12.3f}{abs(r['rho_max_drop']):>8.3f}")

# ── 5. Per-multiplier correlations ────────────────────────────────────────────
print("\nPer-multiplier Spearman rho (each multiplier's drop vs each sensitivity score):")
print(f"{'Multiplier':<14}", end="")
for m in metrics:
    print(f"{m:<18}", end="")
print()
for design in ["trunc", "orbased", "compensated"]:
    sub = lw[lw["multiplier"] == design].set_index("layer")["accuracy_drop"]
    print(f"{design:<14}", end="")
    for m in metrics:
        scores = sens[sens["metric"] == m].set_index("layer")["value"]
        x = [scores[l] for l in LAYERS]
        y = [sub[l] for l in LAYERS]
        rho, _ = spearmanr(x, y)
        print(f"{rho:>+8.3f}          ", end="")
    print()

# ── 6. GO/NO-GO decision ──────────────────────────────────────────────────────
best_row = df_res.loc[df_res["rho_mean_drop"].abs().idxmax()]
best_rho  = abs(best_row["rho_mean_drop"])
best_metric = best_row["metric"]

decision_lines = [
    "=" * 60,
    f"TRUNC=6 GO/NO-GO DECISION",
    "=" * 60,
    f"Best metric (mean_drop): {best_metric}",
    f"  |rho| = {best_rho:.3f}   p = {best_row['p_mean_drop']:.3f}",
    "",
    f"Threshold: |rho| >= 0.7 => GO  |  0.4-0.7 => MODIFY  |  <0.4 => NO-GO",
    "",
]

if best_rho >= 0.7:
    verdict = "GO"
    decision_lines += [
        "=> GO: Sensitivity score reliably predicts layer approximation impact.",
        f"   Recommended score: {best_metric}",
        "   Proceed to: NSGA-II comparison + CNN accelerator RTL.",
    ]
elif best_rho >= 0.4:
    verdict = "MODIFY"
    # Find which formula to revise
    decision_lines += [
        "=> MODIFY: Signal is detectable but not strong enough.",
        "   Options:",
        "     (a) Try rank-based normalization instead of min-max.",
        "     (b) Use max_drop instead of mean_drop as the target.",
        "     (c) Weight S2 (gradient) more heavily in S3 formula.",
        "   Re-run this script only — no new CNN sweep needed.",
    ]
else:
    verdict = "NO-GO"
    decision_lines += [
        "=> NO-GO: No tested metric reliably predicts layer sensitivity.",
        "   Options:",
        "     (a) Switch to perturbation-based measured sensitivity (run a",
        "         mini-sweep with ~100 images to get measured drop per layer,",
        "         then use THAT as the 'score' — the score becomes exact).",
        "     (b) Reframe contribution as the 12-cell characterisation matrix",
        "         itself + the 4-metric comparison study (still publishable).",
        "   Do NOT proceed to FPGA implementation yet.",
    ]

decision_lines.append("=" * 60)

print("\n")
for line in decision_lines:
    print(line)

with open("go_nogo_t6.txt", "w") as f:
    f.write("\n".join(decision_lines) + "\n")
print(f"\nSaved go_nogo_t6.txt  (verdict: {verdict})")
