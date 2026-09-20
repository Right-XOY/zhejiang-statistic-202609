import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Ellipse, FancyArrowPatch

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIG_DIR = os.path.join(ROOT, "outputs", "figures")
PARAMS = os.path.join(ROOT, "outputs", "results", "q7_sem", "params.csv")

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 潜变量（椭圆）
LATENT = {
    "F3": (3.0, 7.5, "环境噪声源\nF3"),
    "F4": (3.0, 2.5, "生活噪声源\nF4"),
    "F1": (6.5, 7.5, "身心健康\nF1"),
    "F2": (6.5, 2.5, "情绪关系\nF2"),
}
# 观测变量（矩形）：name -> (x, y, 标签)
OBS = {
    "noise_traffic": (0.5, 8.6, "交通"),
    "noise_construction": (0.5, 7.5, "施工"),
    "noise_public": (0.5, 6.4, "公共"),
    "noise_life": (0.5, 3.6, "生活"),
    "noise_business": (0.5, 2.5, "商业"),
    "noise_animal": (0.5, 1.4, "动物"),
    "eff_sleep_onset": (4.2, 9.4, "入睡"),
    "eff_attention": (5.4, 9.4, "注意"),
    "eff_mental": (6.6, 9.4, "精神"),
    "eff_hearing": (7.8, 9.0, "听觉"),
    "eff_sleep_interrupt": (4.2, 0.6, "中断"),
    "eff_relationship": (5.4, 0.6, "关系"),
    "eff_physical": (6.6, 0.6, "身体"),
    "eff_emotion": (7.8, 1.0, "情绪"),
}
SAT = (9.6, 5.0, "满意度")

# 观测变量归属的潜变量
OBS_TO_LATENT = {
    "noise_traffic": "F3", "noise_construction": "F3", "noise_public": "F3",
    "noise_life": "F4", "noise_business": "F4", "noise_animal": "F4",
    "eff_sleep_onset": "F1", "eff_attention": "F1", "eff_mental": "F1", "eff_hearing": "F1",
    "eff_sleep_interrupt": "F2", "eff_relationship": "F2", "eff_physical": "F2", "eff_emotion": "F2",
}


def _stars(p):
    if p is None:
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return ""


def _load_coef(params, lval, rval):
    row = params[(params["lval"] == lval) & (params["rval"] == rval)]
    if row.empty:
        return None
    est = row["Estimate"].iloc[0]
    p = row["p-value"].iloc[0]
    if p == "-":
        return float(est), None
    return float(est), float(p)


def main():
    params = pd.read_csv(PARAMS)
    fig, ax = plt.subplots(figsize=(12, 8))

    # 观测变量（矩形）
    for name, (x, y, label) in OBS.items():
        ax.add_patch(plt.Rectangle((x - 0.55, y - 0.28), 1.1, 0.56, fill=True,
                                   facecolor="white", edgecolor="black", linewidth=1.2))
        ax.text(x, y, label, ha="center", va="center", fontsize=9)

    # 潜变量（椭圆）
    for name, (x, y, label) in LATENT.items():
        ax.add_patch(Ellipse((x, y), 1.9, 1.1, fill=True,
                             facecolor="#eef4fb", edgecolor="black", linewidth=1.4))
        ax.text(x, y, label, ha="center", va="center", fontsize=10, fontweight="bold")

    # 满意度（矩形）
    sx, sy, sl = SAT
    ax.add_patch(plt.Rectangle((sx - 0.7, sy - 0.35), 1.4, 0.7, fill=True,
                               facecolor="#fdecec", edgecolor="black", linewidth=1.4))
    ax.text(sx, sy, sl, ha="center", va="center", fontsize=10, fontweight="bold")

    def arrow(x1, y1, x2, y2, color="black", ls="-"):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=14, color=color, linewidth=1.1, linestyle=ls))

    def label_mid(x1, y1, x2, y2, text, dy=0.12):
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + dy, text, ha="center", va="bottom", fontsize=8)

    # 测量模型：潜变量 -> 观测变量（载荷）
    for obs, lat in OBS_TO_LATENT.items():
        ox, oy, _ = OBS[obs]
        lx, ly, _ = LATENT[lat]
        c = _load_coef(params, obs, lat)
        arrow(lx, ly, ox, oy)
        if c:
            est, p = c
            label_mid(lx, ly, ox, oy, f"{est:.2f}{_stars(p)}", dy=0.10)

    # 结构模型路径
    struct = [("F1", "F3"), ("F1", "F4"), ("F2", "F3"), ("F2", "F4"),
              ("satisfaction", "F1"), ("satisfaction", "F2"),
              ("satisfaction", "F3"), ("satisfaction", "F4")]
    for lval, rval in struct:
        # lval 是结果，rval 是前因
        if lval == "satisfaction":
            x2, y2 = SAT[0], SAT[1]
        else:
            x2, y2 = LATENT[lval][0], LATENT[lval][1]
        x1, y1 = LATENT[rval][0], LATENT[rval][1]
        c = _load_coef(params, lval, rval)
        if c:
            est, p = c
            if p >= 0.05:
                continue  # 不显著的路径画虚线或不画
        arrow(x1, y1, x2, y2)
        if c:
            est, p = c
            label_mid(x1, y1, x2, y2, f"{est:.2f}{_stars(p)}")

    # F1 ~~ F2 协方差（双箭头）
    f1x, f1y = LATENT["F1"][0], LATENT["F1"][1]
    f2x, f2y = LATENT["F2"][0], LATENT["F2"][1]
    c = _load_coef(params, "F1", "F2")  # semopy 里协方差 op 是 ~~
    if c is None:
        c = params[(params["lval"] == "F1") & (params["op"] == "~~") & (params["rval"] == "F2")]
        c = (float(c["Estimate"].iloc[0]), float(c["p-value"].iloc[0])) if not c.empty else None
    ax.add_patch(FancyArrowPatch((f1x, f1y - 0.55), (f2x, f2y + 0.55), arrowstyle="<|-|>",
                                 mutation_scale=12, color="gray", linewidth=1.0))
    if c:
        ax.text((f1x + f2x) / 2 + 0.2, (f1y + f2y) / 2, f"{c[0]:.2f}{_stars(c[1])}",
                fontsize=8, color="gray")

    ax.set_xlim(-0.3, 11.0)
    ax.set_ylim(-0.3, 10.2)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "sem_path.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("sem path saved to outputs/figures/sem_path.png")


if __name__ == "__main__":
    main()
