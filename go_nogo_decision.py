import pandas as pd

corr = pd.read_csv("correlation_results.csv")
best = corr.loc[corr["spearman_rho"].abs().idxmax()]

print(f"Best metric: {best['metric']}  rho={best['spearman_rho']:.3f}  p={best['p_value']:.3f}\n")

rho = abs(best["spearman_rho"])
if rho >= 0.7:
    print("=> GO: proceed to NSGA-II comparison and FPGA implementation.")
    print(f"   Use {best['metric']} as the sensitivity score (not necessarily S3).")
elif rho >= 0.4:
    print("=> MODIFY: core idea sound, formula needs revision.")
    print("   Try alternate combinations or rank-based normalization. Re-run correlation_analysis.py only.")
else:
    print("=> NO-GO: none of the tested metrics predict layer sensitivity well enough.")
    print("   Consider: (1) reframe contribution around the characterization matrix itself, or")
    print("             (2) switch to a perturbation-based measured sensitivity metric.")
    print("   Do NOT proceed to FPGA implementation yet.")
