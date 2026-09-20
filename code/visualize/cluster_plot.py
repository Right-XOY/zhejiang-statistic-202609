import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULT_DIR = os.path.join(ROOT, "outputs", "results", "q3_cluster")
FIG_DIR = os.path.join(ROOT, "outputs", "figures")

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

FACTOR_LABELS = ["身心健康与认知", "情绪与社会关系", "典型环境噪声源", "生活场景噪声源"]
CLUSTER_COLORS = ["#2ca02c", "#1f77b4", "#d62728", "#9467bd", "#ffd700"]  # 绿蓝红紫黄


def plot_radar(profiles, out):
    angles = np.linspace(0, 2 * np.pi, len(FACTOR_LABELS), endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    for _, row in profiles.iterrows():
        c = CLUSTER_COLORS[int(row["cluster"])]
        vals = row[["F1", "F2", "F3", "F4"]].tolist() + [row["F1"]]
        ax.plot(angles, vals, color=c, linewidth=2, label=f"簇{int(row['cluster'])}")
        ax.fill(angles, vals, color=c, alpha=0.08)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(FACTOR_LABELS, fontsize=11)
    ax.legend(loc="upper right", bbox_to_anchor=(1.28, 1.1))
    plt.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()


def plot_3d(result, out):
    pca = PCA(n_components=3)
    z = pca.fit_transform(result[["F1", "F2", "F3", "F4"]].to_numpy())
    evr = pca.explained_variance_ratio_
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")
    for c in sorted(result["cluster"].unique()):
        m = result["cluster"] == c
        ax.scatter(z[m, 0], z[m, 1], z[m, 2], s=18, color=CLUSTER_COLORS[c], label=f"簇{c}")
    ax.set_xlabel(f"PC1 ({evr[0] * 100:.1f}%)")
    ax.set_ylabel(f"PC2 ({evr[1] * 100:.1f}%)")
    ax.set_zlabel(f"PC3 ({evr[2] * 100:.1f}%)")
    ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1.0))
    plt.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    profiles = pd.read_csv(os.path.join(RESULT_DIR, "cluster_profiles.csv"))
    result = pd.read_csv(os.path.join(RESULT_DIR, "cluster_result.csv"))
    plot_radar(profiles, os.path.join(FIG_DIR, "cluster_radar.png"))
    plot_3d(result, os.path.join(FIG_DIR, "cluster_3d.png"))
    print("figures saved to outputs/figures/")


if __name__ == "__main__":
    main()
