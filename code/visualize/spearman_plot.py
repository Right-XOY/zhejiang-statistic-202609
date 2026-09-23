import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "figures", "spearman_correlation.png")

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

DATA = [
    ("交通噪声影响", 0.317, 0.000),
    ("周围人生活噪声影响", 0.216, 0.000),
    ("装修/施工噪声影响", 0.222, 0.000),
    ("商业经营噪声影响", 0.179, 0.000),
    ("公共活动噪声影响", 0.261, 0.000),
    ("动物噪声影响", 0.173, 0.000),
    ("噪声入睡情况影响", 0.110, 0.017),
    ("噪声中断睡眠影响", 0.196, 0.000),
    ("噪声注意力影响", 0.122, 0.008),
    ("噪声身边关系影响", 0.112, 0.016),
    ("噪声精神状态影响", 0.137, 0.003),
    ("噪声对身体健康影响", 0.153, 0.000),
    ("噪声对听觉影响", 0.134, 0.004),
    ("噪声对极端情绪影响", 0.180, 0.000),
]

MAIN_BLUE = "#1F4E79"
MID_BLUE = "#5B9BD5"
LIGHT_BLUE = "#9DC3E6"
PALE_BLUE = "#DBEEFD"
TEXT = "#24364B"


def significance_mark(p_value):
    if p_value < 0.001:
        return "***"
    if p_value < 0.05:
        return "*"
    return ""


def main():
    data = sorted(DATA, key=lambda row: row[1])
    labels = [row[0] for row in data]
    values = np.array([row[1] for row in data])
    p_values = [row[2] for row in data]

    rank_colors = [LIGHT_BLUE] * len(data)
    rank_colors[-7:-3] = [MID_BLUE] * 4
    rank_colors[-3:] = [MAIN_BLUE] * 3

    fig, ax = plt.subplots(figsize=(11.8, 7.2))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#FBFDFF")

    bars = ax.barh(
        labels,
        values,
        height=0.66,
        color=rank_colors,
        edgecolor="white",
        linewidth=0.8,
        zorder=3,
    )

    for bar, value, p_value, color in zip(bars, values, p_values, rank_colors):
        ax.text(
            value + 0.006,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.3f}{significance_mark(p_value)}",
            va="center",
            ha="left",
            fontsize=10,
            color=MAIN_BLUE if color == MAIN_BLUE else TEXT,
            fontweight="bold" if color == MAIN_BLUE else "normal",
        )

    ax.set_xlim(0, 0.365)
    ax.set_xlabel("Spearman相关系数 r", fontsize=11, color=TEXT, labelpad=8, fontweight="bold")
    ax.grid(axis="x", color=PALE_BLUE, linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(LIGHT_BLUE)
    ax.tick_params(axis="y", length=0, labelsize=10.5, colors=TEXT)
    ax.tick_params(axis="x", labelsize=9.5, colors=TEXT, length=3, color=LIGHT_BLUE)

    legend_items = [
        Patch(facecolor=MAIN_BLUE, label="重点相关项"),
        Patch(facecolor=MID_BLUE, label="中等关联项"),
        Patch(facecolor=LIGHT_BLUE, label="相对较弱项"),
    ]
    ax.legend(
        handles=legend_items,
        loc="lower right",
        bbox_to_anchor=(0.99, 0.03),
        frameon=False,
        fontsize=9.5,
        labelcolor=TEXT,
    )
    fig.text(
        0.99,
        0.015,
        "注：***表示 P<0.001，*表示 P<0.05。",
        ha="right",
        va="bottom",
        fontsize=8.8,
        color="#5A6B7D",
    )

    plt.tight_layout(rect=[0, 0.035, 1, 1])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    plt.savefig(OUT, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(OUT)


if __name__ == "__main__":
    main()
