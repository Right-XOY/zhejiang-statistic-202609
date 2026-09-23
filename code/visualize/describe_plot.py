# -*- coding: utf-8 -*-
"""第五部分描述性统计图重制脚本

将 图片11.png ~ 图片16.png 统一重制为「蓝系学术风」，与全文其他 matplotlib 图
（如 spearman_correlation.png）保持一致的配色、版式与字体约定：
    - 白底 + 极浅蓝绘图区
    - 三阶蓝配色（深/中/浅）表达语义梯度
    - 去 3D、去透明背景、统一中文黑体
    - 无图内总标题（标题由正文 \\fig 的 caption 承担）
    - 300dpi 高清输出，覆盖原同名文件，无需改动 tex 引用

所有文本、数值与颜色均以变量形式集中声明，便于后续修改。
运行：python code/visualize/describe_plot.py
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# 路径与全局字体
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIG_DIR = os.path.join(ROOT, "figures")

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ---------------------------------------------------------------------------
# 统一蓝色配色（与 spearman_plot.py 完全一致）
# ---------------------------------------------------------------------------
MAIN_BLUE = "#1F4E79"   # 深蓝：最高/最强调
MID_BLUE = "#5B9BD5"    # 中蓝：次强调
LIGHT_BLUE = "#9DC3E6"  # 浅蓝：较弱
PALE_BLUE = "#DBEEFD"   # 网格线 / 最浅
TEXT = "#24364B"        # 正文文字
AX_FACE = "#FBFDFF"     # 绘图区底色

N = 467  # 有效样本量

# ---------------------------------------------------------------------------
# 数据变量（均为问卷 467 份有效样本的实测统计结果）
# ---------------------------------------------------------------------------
# 图片11 隔音墙构成（有 / 无或不清楚）
SOUNDPROOF_LABELS = ["有隔音墙", "无隔音设施或无法确认"]
SOUNDPROOF_VALUES = [132, 335]

# 图片12 噪声暴露全景（四个子面板）
IMPACT_LABELS = ["影响非常大", "影响较大", "影响一般", "偶尔有影响", "几乎没有影响"]
IMPACT_VALUES = [22, 143, 143, 106, 53]

NOISE_SRC_LABELS = ["交通噪声", "施工噪声", "动物噪声", "公共活动噪声", "生活噪声", "商业噪声"]
NOISE_SRC_VALUES = [3.086, 3.009, 2.951, 2.827, 2.756, 2.702]  # 1-5分均值

PERIOD_LABELS = ["上午", "下午", "晚上", "深夜"]
PERIOD_VALUES = [82, 112, 138, 135]

DIST_LABELS = ["无明显噪声源", "距离较远", "距离适中", "距离较近", "近在咫尺"]
DIST_VALUES = [67, 101, 161, 102, 36]

# 图片13 满意度对比（五级有序 × 两类满意度）
SAT_LEVELS = ["非常不满意", "不满意", "一般", "满意", "非常满意"]
SAT_ENV = [44, 168, 141, 80, 34]        # 声环境质量满意度
SAT_GOV = [32, 110, 135, 142, 48]       # 噪声治理工作满意度

# 图片14 应对方式（多选题，按频数降序）
COPING_LABELS = ["自主协商", "社区/物业反馈", "自我防护", "官方投诉", "默默忍受", "法律途径", "其他"]
COPING_VALUES = [239, 223, 207, 185, 142, 90, 33]

# 图片15 治理必要性倾向（五级有序）
NECESSITY_LABELS = ["非常有必要", "有必要", "一般", "没有必要", "完全没有必要"]
NECESSITY_VALUES = [113, 176, 94, 59, 25]

# 图片16 治理需求（多选题，按频数降序）
DEMAND_LABELS = ["完善管控法律法规", "规范噪声排放时段", "增设隔音设施", "加强文明宣传",
                 "优化投诉处理", "加大执法处罚", "优化声环境规划", "其他"]
DEMAND_VALUES = [265, 238, 228, 214, 201, 184, 155, 16]


# ---------------------------------------------------------------------------
# 通用样式辅助
# ---------------------------------------------------------------------------
def _clean_axes(ax):
    """统一坐标轴样式：隐藏上右边框、浅蓝网格、浅色轴线。"""
    ax.set_facecolor(AX_FACE)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(LIGHT_BLUE)
    ax.spines["bottom"].set_color(LIGHT_BLUE)
    ax.grid(axis="y", color=PALE_BLUE, linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)


def _save(fig, name):
    """以 300dpi、白底、紧凑边界保存到 figures 目录。"""
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("已生成", path)


def _multi_note(fig):
    """多选题脚注（应对方式、治理需求两个多选题图使用）。"""
    fig.text(0.99, 0.015,
             f"注：本题为多选题，百分比＝选择该项人数 / 总有效样本数（N={N}）。",
             ha="right", va="bottom", fontsize=8.5, color="#5A6B7D")


# ---------------------------------------------------------------------------
# 图片11：隔音墙构成（两分类环形图）
# ---------------------------------------------------------------------------
def fig11_soundproof():
    labels = SOUNDPROOF_LABELS
    values = SOUNDPROOF_VALUES
    colors = [MAIN_BLUE, LIGHT_BLUE]

    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    fig.patch.set_facecolor("white")

    wedges, _ = ax.pie(
        values, labels=None, colors=colors,
        startangle=90, counterclock=False,
        wedgeprops=dict(width=0.45, edgecolor="white"),
    )
    # 中心放置「有隔音墙」占比
    pct = values[0] / sum(values) * 100
    ax.text(0, 0.06, f"{pct:.2f}%", ha="center", va="center",
            fontsize=22, fontweight="bold", color=MAIN_BLUE)
    ax.text(0, -0.32, "有隔音墙", ha="center", va="center",
            fontsize=10, color=TEXT)

    # 右侧图例：类别 + 人数 + 百分比
    legend_labels = [
        f"{labels[i]}　{values[i]}人（{values[i] / N * 100:.2f}%）"
        for i in range(len(labels))
    ]
    ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1.0, 0.5),
              frameon=False, fontsize=10.5, labelcolor=TEXT)

    _save(fig, "图片11.png")


# ---------------------------------------------------------------------------
# 图片12：噪声暴露全景（2×2 四子面板）
# ---------------------------------------------------------------------------
def fig12_panorama():
    fig, axes = plt.subplots(2, 2, figsize=(11.6, 7.4))
    fig.patch.set_facecolor("white")

    # ① 噪声影响程度分布
    ax = axes[0, 0]
    _clean_axes(ax)
    bars = ax.bar(IMPACT_LABELS, IMPACT_VALUES, color=MID_BLUE,
                  edgecolor="white", linewidth=0.8, zorder=3, width=0.62)
    for b, v in zip(bars, IMPACT_VALUES):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v}人",
                ha="center", va="bottom", fontsize=9.5, color=TEXT)
    ax.set_ylim(0, max(IMPACT_VALUES) * 1.2)
    ax.set_ylabel("人数", fontsize=10, color=TEXT)
    ax.set_title("① 噪声影响程度分布", fontsize=11.5, color=TEXT,
                 fontweight="bold", pad=8)
    ax.tick_params(axis="x", labelsize=8.8, colors=TEXT)
    ax.tick_params(axis="y", labelsize=8.8, colors=TEXT, length=3, color=LIGHT_BLUE)

    # ② 各类噪声源平均干扰评分（Y 轴从 0 起，避免截断轴）
    ax = axes[0, 1]
    _clean_axes(ax)
    bars = ax.bar(NOISE_SRC_LABELS, NOISE_SRC_VALUES, color=MAIN_BLUE,
                  edgecolor="white", linewidth=0.8, zorder=3, width=0.62)
    for b, v in zip(bars, NOISE_SRC_VALUES):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.04, f"{v:.2f}",
                ha="center", va="bottom", fontsize=9.5, color=TEXT)
    ax.set_ylim(0, 3.6)
    ax.set_ylabel("平均干扰评分（1—5分）", fontsize=10, color=TEXT)
    ax.set_title("② 各类噪声源平均干扰评分", fontsize=11.5, color=TEXT,
                 fontweight="bold", pad=8)
    ax.tick_params(axis="x", labelsize=8.8, colors=TEXT)
    ax.tick_params(axis="y", labelsize=8.8, colors=TEXT, length=3, color=LIGHT_BLUE)

    # ③ 噪声影响时段
    ax = axes[1, 0]
    _clean_axes(ax)
    bars = ax.bar(PERIOD_LABELS, PERIOD_VALUES, color=LIGHT_BLUE,
                  edgecolor="white", linewidth=0.8, zorder=3, width=0.62)
    for b, v in zip(bars, PERIOD_VALUES):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v}人",
                ha="center", va="bottom", fontsize=9.5, color=TEXT)
    ax.set_ylim(0, max(PERIOD_VALUES) * 1.2)
    ax.set_ylabel("人数", fontsize=10, color=TEXT)
    ax.set_title("③ 噪声影响时段", fontsize=11.5, color=TEXT,
                 fontweight="bold", pad=8)
    ax.tick_params(axis="x", labelsize=8.8, colors=TEXT)
    ax.tick_params(axis="y", labelsize=8.8, colors=TEXT, length=3, color=LIGHT_BLUE)

    # ④ 声源距离分布
    ax = axes[1, 1]
    _clean_axes(ax)
    bars = ax.bar(DIST_LABELS, DIST_VALUES, color=MID_BLUE,
                  edgecolor="white", linewidth=0.8, zorder=3, width=0.62)
    for b, v in zip(bars, DIST_VALUES):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v}人",
                ha="center", va="bottom", fontsize=9.5, color=TEXT)
    ax.set_ylim(0, max(DIST_VALUES) * 1.2)
    ax.set_ylabel("人数", fontsize=10, color=TEXT)
    ax.set_title("④ 声源距离分布", fontsize=11.5, color=TEXT,
                 fontweight="bold", pad=8)
    ax.tick_params(axis="x", labelsize=8.8, colors=TEXT)
    ax.tick_params(axis="y", labelsize=8.8, colors=TEXT, length=3, color=LIGHT_BLUE)

    plt.tight_layout()
    _save(fig, "图片12.png")


# ---------------------------------------------------------------------------
# 图片13：声环境 / 治理工作满意度对比（分组柱状图）
# ---------------------------------------------------------------------------
def fig13_satisfaction():
    x = np.arange(len(SAT_LEVELS))
    width = 0.38

    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    fig.patch.set_facecolor("white")
    _clean_axes(ax)

    bars_env = ax.bar(x - width / 2, SAT_ENV, width, label="声环境质量满意度",
                      color=MID_BLUE, edgecolor="white", linewidth=0.8, zorder=3)
    bars_gov = ax.bar(x + width / 2, SAT_GOV, width, label="噪声治理工作满意度",
                      color=MAIN_BLUE, edgecolor="white", linewidth=0.8, zorder=3)

    for bars in (bars_env, bars_gov):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 2,
                    f"{int(b.get_height())}人", ha="center", va="bottom",
                    fontsize=9, color=TEXT)

    ax.set_ylim(0, max(max(SAT_ENV), max(SAT_GOV)) * 1.3)
    ax.set_xticks(x)
    ax.set_xticklabels(SAT_LEVELS, fontsize=10, color=TEXT)
    ax.set_ylabel("人数", fontsize=10.5, color=TEXT)
    ax.tick_params(axis="y", labelsize=9, colors=TEXT, length=3, color=LIGHT_BLUE)
    ax.legend(frameon=False, fontsize=10, labelcolor=TEXT, loc="upper left")

    _save(fig, "图片13.png")


# ---------------------------------------------------------------------------
# 图片14：居民应对方式（横向条形图，多选题）
# ---------------------------------------------------------------------------
def fig14_coping():
    labels = COPING_LABELS
    values = np.array(COPING_VALUES)

    fig, ax = plt.subplots(figsize=(9.4, 5.6))
    fig.patch.set_facecolor("white")
    _clean_axes(ax)
    ax.grid(axis="y", color=PALE_BLUE, linewidth=0.9, zorder=0)

    order = np.argsort(values)
    bars = ax.barh(np.array(labels)[order], values[order], height=0.62,
                   color=MID_BLUE, edgecolor="white", linewidth=0.8, zorder=3)
    for b, v in zip(bars, values[order]):
        ax.text(b.get_width() + 3, b.get_y() + b.get_height() / 2,
                f"{v}人（{v / N * 100:.2f}%）", va="center", ha="left",
                fontsize=9.5, color=TEXT)

    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=10, colors=TEXT)
    ax.set_xlabel("人数", fontsize=10.5, color=TEXT)
    _multi_note(fig)

    fig.tight_layout(rect=[0, 0.035, 1, 1])
    _save(fig, "图片14.png")


# ---------------------------------------------------------------------------
# 图片15：噪声治理必要性倾向（五级环形图）
# ---------------------------------------------------------------------------
def fig15_necessity():
    labels = NECESSITY_LABELS
    values = NECESSITY_VALUES
    # 有序变量：从「非常有必要」到「完全没有必要」蓝色由深到浅
    colors = ["#1F4E79", "#4A7FB5", "#8FB4D9", "#C7DAF0", "#E6F0FA"]

    fig, ax = plt.subplots(figsize=(8.2, 4.0))
    fig.patch.set_facecolor("white")

    wedges, _ = ax.pie(
        values, labels=None, colors=colors,
        startangle=90, counterclock=False,
        wedgeprops=dict(width=0.42, edgecolor="white"),
    )
    legend_labels = [
        f"{labels[i]}　{values[i]}人（{values[i] / N * 100:.2f}%）"
        for i in range(len(labels))
    ]
    ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1.0, 0.5),
              frameon=False, fontsize=10, labelcolor=TEXT)

    _save(fig, "图片15.png")


# ---------------------------------------------------------------------------
# 图片16：噪声治理需求（横向条形图，多选题）
# ---------------------------------------------------------------------------
def fig16_demand():
    labels = DEMAND_LABELS
    values = np.array(DEMAND_VALUES)

    fig, ax = plt.subplots(figsize=(9.4, 6.2))
    fig.patch.set_facecolor("white")
    _clean_axes(ax)
    ax.grid(axis="y", color=PALE_BLUE, linewidth=0.9, zorder=0)

    order = np.argsort(values)
    bars = ax.barh(np.array(labels)[order], values[order], height=0.62,
                   color=MAIN_BLUE, edgecolor="white", linewidth=0.8, zorder=3)
    for b, v in zip(bars, values[order]):
        ax.text(b.get_width() + 3, b.get_y() + b.get_height() / 2,
                f"{v}人（{v / N * 100:.2f}%）", va="center", ha="left",
                fontsize=9.5, color=TEXT)

    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=10, colors=TEXT)
    ax.set_xlabel("人数", fontsize=10.5, color=TEXT)
    _multi_note(fig)

    fig.tight_layout(rect=[0, 0.035, 1, 1])
    _save(fig, "图片16.png")


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------
def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    fig11_soundproof()
    fig12_panorama()
    fig13_satisfaction()
    fig14_coping()
    fig15_necessity()
    fig16_demand()
    print("全部图片重制完成。")


if __name__ == "__main__":
    main()