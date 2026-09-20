import os

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

import preprocess as pp

FACTORS = ["F1", "F2", "F3", "F4"]


def main():
    scores = pd.read_csv(os.path.join(pp.OUT_DIR, "q2_efa", "factor_scores.csv"))
    x = scores[FACTORS].to_numpy()

    ks = range(2, 9)
    sse, sil = [], []
    for k in ks:
        km = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=42)
        lab = km.fit_predict(x)
        sse.append(km.inertia_)
        sil.append(silhouette_score(x, lab))
    pp.save_csv(pd.DataFrame({"K": list(ks), "SSE": np.round(sse, 2), "轮廓系数": np.round(sil, 4)}),
                "q3_cluster", "k_selection.csv")

    best_k = list(ks)[int(np.argmax(sil))]
    km = KMeans(n_clusters=best_k, init="k-means++", n_init=10, random_state=42)
    labels = km.fit_predict(x)

    result = scores[FACTORS].copy()
    result["cluster"] = labels
    pp.save_csv(result, "q3_cluster", "cluster_result.csv")

    profiles = result.groupby("cluster")[FACTORS].mean().round(3).reset_index()
    profiles["n"] = result.groupby("cluster").size().values
    pp.save_csv(profiles, "q3_cluster", "cluster_profiles.csv")

    anova = {}
    for c in FACTORS:
        groups = [result.loc[result["cluster"] == i, c] for i in range(best_k)]
        f, p = stats.f_oneway(*groups)
        anova[c] = {"F": round(float(f), 3), "p": round(float(p), 4)}
    pp.save_json(anova, "q3_cluster", "anova.json")

    demo = pp.clean(pp.load_raw())
    demo["cluster"] = labels
    rows = []
    for i in range(best_k):
        sub = demo[demo["cluster"] == i]
        row = {"cluster": i}
        for var in pp.DEMOGRAPHIC_VARS:
            row[pp.VAR_LABELS[var]] = sub[var].mode().iloc[0]
        rows.append(row)
    pp.save_csv(pd.DataFrame(rows), "q3_cluster", "cluster_demographics.csv")

    print("best K:", best_k)
    print(profiles.to_string(index=False))


if __name__ == "__main__":
    main()
