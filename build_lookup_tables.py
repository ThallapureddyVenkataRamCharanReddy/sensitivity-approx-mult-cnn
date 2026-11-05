import pandas as pd, numpy as np
df = pd.read_csv("axm_results.csv")
tables = {}
for d in ["exact","trunc","orbased","compensated"]:
    t = np.zeros((256,256), dtype=np.int32)
    t[df["a"].values, df["b"].values] = df[d].values
    tables[d] = t
np.savez("axm_tables.npz", **tables)
print("Saved axm_tables.npz with:", list(tables.keys()))
