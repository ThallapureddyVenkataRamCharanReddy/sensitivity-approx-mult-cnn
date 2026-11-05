import pandas as pd, numpy as np
from scipy.stats import spearmanr

sens = pd.read_csv("sensitivity_scores.csv")
lw = pd.read_csv("layerwise_results.csv")

mean_drop = lw.groupby("layer")["accuracy_drop"].mean().to_dict()
LAYERS = ["conv1","conv2","conv3","conv4"]
metrics = sens["metric"].unique()

print(f"{'Metric':<20}{'Spearman rho':>15}{'p-value':>12}")
results = []
for m in metrics:
    scores = sens[sens["metric"]==m].set_index("layer")["value"]
    x = [scores[l] for l in LAYERS]
    y = [mean_drop[l] for l in LAYERS]
    rho, p = spearmanr(x, y)
    results.append((m, rho, p))
    print(f"{m:<20}{rho:>15.3f}{p:>12.3f}")

pd.DataFrame(results, columns=["metric","spearman_rho","p_value"]).to_csv("correlation_results.csv", index=False)
print("\nSaved correlation_results.csv")
print("\nMean accuracy drop per layer (for reference):")
for l in LAYERS: print(f"  {l}: {mean_drop[l]:.3f}%")
