# -*- coding: utf-8 -*-
"""第五部分描述性统计图重制脚本（统计公报/信息卡片风格）

将 图片11.png ~ 图片16.png 统一重制为与 板块1~6 一致的国家统计局公报风：
    - 白色圆角卡片 + 极浅蓝灰描边 + 轻微阴影
    - 左上角蓝色胶囊标题栏（内含续接编号 7~12 + 主题名，白字加粗）
    - 蓝灰单色系表达主数据，红色 #E74C3C 仅用于TOP1/关键发现
    - 环形图（构成比）、横向进度条（多分类排序）配合「大数字 + 小号单位 + 百分比」
    - 无 3D、无透明背景、统一微软雅黑
    - 300dpi 高清输出，覆盖原同名文件，无需改动 tex 引用

所有文本、数值与颜色均以变量集中声明，便于后续修改。
运行：python code/visualize/bulletin_plot.py
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

# ---------------------------------------------------------------------------
# 路径与全局字体
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIG_DIR = os.path.join(ROOT, "figures")

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ---------------------------------------------------------------------------
# 统一配色（对齐板块 1~6 的公报风视觉规范）
# ---------------------------------------------------------------------------
TITLE_BLUE = "#4A90C2"   # 标题胶囊蓝
MAIN_BLUE = "#4A90D9"    # 主数据蓝
DEEP_BLUE = "#2C4A6E"    # 大数字 / 深蓝
LIGHT_BLUE = "#8BB8D0"   # 浅蓝（次要类目）
LIGHTER = "#A8C8E8"
TRACK = "#E8F0F8"        # 进度条轨道
RED = "#E74C3C"          # TOP1 / 关键发现
TEXT = "#333333"         # 正文
GRAY = "#888888"         # 百分比 / 辅助文字
BORDER = "#E0E6ED"       # 卡片描边
SHADOW = "#EEF3F8"       # 卡片阴影

N = 467  # 有效样本量

# 5 级有序蓝色的由深到浅（用于「治理倾向」环形图）
BLUE_5 = ["#1F4E79", "#4A90D9", "#8FB4D9", "#C7DAF0", "#E6F0FA"]

# ---------------------------------------------------------------------------
# 版式显示开关（便于一键调整）
# ---------------------------------------------------------------------------
SHOW_CARD = True     # 是否绘制底版白色圆角卡片（含边框与阴影）
SHOW_INDEX = False   # 胶囊标题与子图标题前是否显示序号
SHOW_NOTE = False    # 是否显示底部注释行

# ---------------------------------------------------------------------------
# 数据变量（均为问卷 467 份有效样本实测统计结果）
# ---------------------------------------------------------------------------
SOUNDPROOF_LABELS = ["有隔音墙", "无隔音设施或无法确认"]
SOUNDPROOF_VALUES = [132, 335]

IMPACT_LABELS = ["影响非常大", "影响较大", "影响一般", "偶尔有影响", "几乎没有影响"]
IMPACT_VALUES = [22, 143, 143, 106, 53]
NOISE_SRC_LABELS = ["交通噪声", "施工噪声", "动物噪声", "公共活动噪声", "生活噪声", "商业噪声"]
NOISE_SRC_VALUES = [3.086, 3.009, 2.951, 2.827, 2.756, 2.702]
PERIOD_LABELS = ["上午", "下午", "晚上", "深夜"]
PERIOD_VALUES = [82, 112, 138, 135]
DIST_LABELS = ["无明显噪声源", "距离较远", "距离适中", "距离较近", "近在咫尺"]
DIST_VALUES = [67, 101, 161, 102, 36]

SAT_LEVELS = ["非常不满意", "不满意", "一般", "满意", "非常满意"]
SAT_ENV = [44, 168, 141, 80, 34]
SAT_GOV = [32, 110, 135, 142, 48]

COPING_LABELS = ["自主协商", "社区/物业反馈", "自我防护", "官方投诉", "默默忍受", "法律途径", "其他"]
COPING_VALUES = [239, 223, 207, 185, 142, 90, 33]

NECESSITY_LABELS = ["非常有必要", "有必要", "一般", "没有必要", "完全没有必要"]
NECESSITY_VALUES = [113, 176, 94, 59, 25]

DEMAND_LABELS = ["完善管控法律法规", "规范噪声排放时段", "增设隔音设施", "加强文明宣传",
                 "优化投诉处理", "加大执法处罚", "优化声环境规划", "其他"]
DEMAND_VALUES = [265, 238, 228, 214, 201, 184, 155, 16]


# ---------------------------------------------------------------------------
# 通用绘制辅助（0-100 画布坐标系）
# ---------------------------------------------------------------------------
def _canvas(figsize):
    """建图：关闭坐标轴，x/y 取值 0-100 便于绝对定位。"""
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    return fig, ax


def _card(ax):
    """白色圆角卡片（阴影 + 白底 + 浅描边）；SHOW_CARD=False 时不绘制。"""
    if not SHOW_CARD:
        return
    ax.add_patch(FancyBboxPatch((1.0, 1.0), 98.0, 98.0,
                                boxstyle="round,pad=0,rounding_size=2.2",
                                transform=ax.transData, linewidth=0,
                                facecolor=SHADOW, zorder=0))
    ax.add_patch(FancyBboxPatch((1.8, 2.2), 96.4, 95.6,
                                boxstyle="round,pad=0,rounding_size=2.2",
                                transform=ax.transData, linewidth=1.4,
                                facecolor="white", edgecolor=BORDER, zorder=1))


def _pill(ax, num, title):
    """左上角蓝色胶囊标题栏；SHOW_INDEX=False 时只显示主题名，
    宽度随文字自适应，文字水平居中、完整落在胶囊内部。"""
    title_txt = f"{num}　{title}" if SHOW_INDEX else title
    width = max(11.0, 2.7 * len(title_txt) + 5.0)
    x0 = 5.5
    ax.add_patch(FancyBboxPatch((x0, 85.0), width, 9.0,
                                boxstyle="round,pad=0,rounding_size=4.5",
                                transform=ax.transData, linewidth=0,
                                facecolor=TITLE_BLUE, zorder=3))
    ax.text(x0 + width / 2.0, 89.2, title_txt, va="center", ha="center",
            color="white", fontsize=16, fontweight="bold", zorder=4)


def _big_num(ax, x, y, number, unit, label, pct, pct_color, number_color=DEEP_BLUE):
    """大数字块：大数字 + 小号单位 + 底部标签 + 百分比。"""
    ax.text(x, y, number, va="center", ha="left", fontsize=34,
            fontweight="bold", color=number_color, zorder=4)
    ax.text(x + len(str(number)) * 5.0, y - 2.5, unit, va="center", ha="left",
            fontsize=13, color=number_color, zorder=4)
    ax.text(x, y - 12.0, label, va="center", ha="left", fontsize=11.5,
            color=TEXT, zorder=4)
    ax.text(x, y - 20.0, pct, va="center", ha="left", fontsize=12,
            color=pct_color, fontweight="bold", zorder=4)


def _dot(ax, x, y, color, label, value_txt):
    """图例行：彩色圆点 + 标签 + 数值（用于环形图右侧列表）。"""
    ax.scatter([x], [y], s=90, color=color, zorder=4)
    ax.text(x + 3.5, y, label, va="center", ha="left", fontsize=11.5,
            color=TEXT, zorder=4)
    ax.text(94.0, y, value_txt, va="center", ha="right",
            fontsize=10.5, color=GRAY, zorder=4)


def _progress_rows(ax, items, x_bar, top, row_h, bar_w):
    """横向进度条（label | 轨道+填充条 | 人数+百分比）。

    items: [(label, value), ...]，按给定顺序自上而下绘制。
    """
    max_val = max(v for _, v in items)
    for i, (label, value) in enumerate(items):
        y = top - i * row_h
        pct = value / N * 100
        color = RED if value == max_val else MAIN_BLUE
        # 标签
        ax.text(x_bar - 2.0, y, label, va="center", ha="right",
                fontsize=11.5, color=TEXT, zorder=4)
        # 轨道（全长基准）
        ax.barh(y, bar_w, height=2.0, left=x_bar, color=TRACK,
                edgecolor="none", zorder=2)
        # 填充（按占最大项比例缩放，保证不溢出）
        ax.barh(y, pct / 100 * bar_w, height=2.0, left=x_bar, color=color,
                edgecolor="none", zorder=3)
        # 数值
        ax.text(x_bar + bar_w + 2.0, y, f"{value}人（{pct:.2f}%）",
                va="center", ha="left", fontsize=10,
                color=RED if color == RED else GRAY, zorder=4)


def _donut(fig, rect, values, colors, center, center_sub, center_color):
    """环形图：内嵌子轴，中心放关键数字与说明（说明文字缩小并上提，不超出内圈）。"""
    ax = fig.add_axes(rect)
    ax.pie(values, colors=colors, startangle=90, counterclock=False,
           wedgeprops=dict(width=0.42, edgecolor="white"))
    ax.text(0, 0.10, center, ha="center", va="center", fontsize=26,
            fontweight="bold", color=center_color, zorder=5)
    ax.text(0, -0.18, center_sub, ha="center", va="center", fontsize=8.5,
            color=GRAY, zorder=5)
    ax.set_aspect("equal")


def _note(ax, text):
    """底部脚注；SHOW_NOTE=False 时不绘制。"""
    if not SHOW_NOTE:
        return
    ax.text(97.0, 4.5, text, ha="right", va="top", fontsize=9.5,
            color=GRAY, zorder=4)


def _save(fig, name):
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("已生成", path)


# ---------------------------------------------------------------------------
# 图片11（第7板块）：隔音墙构成 —— 环形图 + 两类 KPI
# ---------------------------------------------------------------------------
def fig11_soundproof():
    fig, ax = _canvas((9.6, 4.8))
    _card(ax)
    _pill(ax, 7, "隔音墙")

    _donut(fig, [0.04, 0.10, 0.52, 0.64],
           SOUNDPROOF_VALUES, [MAIN_BLUE, LIGHT_BLUE],
           "28.27%", "有隔音墙", MAIN_BLUE)

    _big_num(ax, 62, 64, "132", "人", "有隔音墙", "占28.27%", MAIN_BLUE)
    _big_num(ax, 62, 26, "335", "人", "无隔音设施或无法确认", "占71.73%", LIGHT_BLUE)

    _note(ax, f"注：数据源于本次调查 {N} 份有效问卷。")
    _save(fig, "图片11.png")


# ---------------------------------------------------------------------------
# 图片12（第8板块）：噪声暴露全景 —— 2×2 四子图卡片
# ---------------------------------------------------------------------------
def fig12_panorama():
    fig, ax = _canvas((12.0, 7.6))
    # 图片12不使用底版卡片，也不绘制蓝色胶囊大标题，直接白底排版 2×2 子图

    panels = [
        ("噪声影响程度", IMPACT_LABELS, IMPACT_VALUES, "人数"),
        ("各类噪声源平均干扰评分", NOISE_SRC_LABELS, NOISE_SRC_VALUES, "评分"),
        ("噪声影响时段", PERIOD_LABELS, PERIOD_VALUES, "人数"),
        ("声源距离分布", DIST_LABELS, DIST_VALUES, "人数"),
    ]
    index_marks = ["①", "②", "③", "④"]
    # 上下两排子图错开纵向间距，避免顶部子图 x 轴标签与底部子图标题重叠
    pos = [(0.05, 0.47), (0.52, 0.47), (0.05, 0.03), (0.52, 0.03)]

    for i, ((title, labels, values, unit), (l, b)) in enumerate(zip(panels, pos)):
        sub = fig.add_axes([l, b, 0.43, 0.34])
        sub.set_facecolor("white")
        max_val = max(values)
        colors = [RED if v == max_val else MAIN_BLUE for v in values]
        bars = sub.bar(labels, values, color=colors, width=0.62,
                       edgecolor="white", linewidth=0.6, zorder=3)
        if unit == "评分":
            for bbar, v in zip(bars, values):
                sub.text(bbar.get_x() + bbar.get_width() / 2, v + 0.05,
                         f"{v:.2f}", ha="center", va="bottom", fontsize=9,
                         color=TEXT)
        else:
            for bbar, v in zip(bars, values):
                sub.text(bbar.get_x() + bbar.get_width() / 2, v + 1.5,
                         f"{v}人", ha="center", va="bottom", fontsize=9,
                         color=TEXT)
        title_txt = f"{index_marks[i]} {title}" if SHOW_INDEX else title
        sub.set_title(title_txt, fontsize=12, color=TEXT, pad=6)
        sub.tick_params(axis="x", labelsize=8, colors=TEXT, rotation=14)
        sub.tick_params(axis="y", labelsize=8.0, colors=GRAY, length=2)
        for s in ["top", "right"]:
            sub.spines[s].set_visible(False)
        sub.spines["left"].set_color(BORDER)
        sub.spines["bottom"].set_color(BORDER)
        sub.grid(axis="y", color=TRACK, linewidth=0.8, zorder=0)
        sub.set_axisbelow(True)
        sub.margins(y=0.28)

    _note(ax, f"注：数据源于本次调查 {N} 份有效问卷；②为 1—5 分量表平均分。")
    _save(fig, "图片12.png")


# ---------------------------------------------------------------------------
# 图片13（第9板块）：满意度总览 —— 双大数字 + 分组柱状图
# ---------------------------------------------------------------------------
def fig13_satisfaction():
    fig, ax = _canvas((10.6, 5.8))
    _card(ax)
    _pill(ax, 9, "满意度总览")

    env_bad = (SAT_ENV[0] + SAT_ENV[1]) / N * 100
    gov_good = (SAT_GOV[3] + SAT_GOV[4]) / N * 100
    _big_num(ax, 8, 62, f"{env_bad:.2f}", "%", "对声环境质量不满意", "满意仅24.41%", RED,
             number_color=RED)
    _big_num(ax, 8, 28, f"{gov_good:.2f}", "%", "对治理工作满意", "不满意30.41%", MAIN_BLUE,
             number_color=MAIN_BLUE)

    # 分组柱状图（整体缩小并内缩，右侧与卡片边框留出间距）
    sub = fig.add_axes([0.36, 0.26, 0.50, 0.54])
    sub.set_facecolor("white")
    x = np.arange(len(SAT_LEVELS))
    w = 0.32
    sub.bar(x - w / 2, SAT_ENV, w, color=MAIN_BLUE, edgecolor="white",
            linewidth=0.6, label="声环境质量满意度", zorder=3)
    sub.bar(x + w / 2, SAT_GOV, w, color=LIGHT_BLUE, edgecolor="white",
            linewidth=0.6, label="噪声治理工作满意度", zorder=3)
    sub.set_xticks(x)
    sub.set_xticklabels(SAT_LEVELS, fontsize=9, color=TEXT)
    sub.set_ylabel("人数", fontsize=9, color=GRAY, labelpad=4)
    sub.tick_params(axis="y", labelsize=8, colors=GRAY, length=2)
    for s in ["top", "right"]:
        sub.spines[s].set_visible(False)
    sub.spines["left"].set_color(BORDER)
    sub.spines["bottom"].set_color(BORDER)
    sub.grid(axis="y", color=TRACK, linewidth=0.8, zorder=0)
    sub.set_axisbelow(True)
    sub.legend(frameon=False, fontsize=9, labelcolor=TEXT, loc="upper right")
    sub.margins(y=0.22)

    _note(ax, f"注：数据源于本次调查 {N} 份有效问卷。")
    _save(fig, "图片13.png")


# ---------------------------------------------------------------------------
# 图片14（第10板块）：应对方式 —— 横向进度条（多选题）
# ---------------------------------------------------------------------------
def fig14_coping():
    fig, ax = _canvas((9.8, 6.0))
    _card(ax)
    _pill(ax, 10, "应对方式")

    order = np.argsort(COPING_VALUES)[::-1]
    items = [(COPING_LABELS[i], COPING_VALUES[i]) for i in order]
    _progress_rows(ax, items, x_bar=28, top=78, row_h=9.0, bar_w=42)

    _note(ax, f"注：本题为多选题，百分比＝选择该项人数 / 总有效样本数（N={N}）。")
    _save(fig, "图片14.png")


# ---------------------------------------------------------------------------
# 图片15（第11板块）：治理倾向 —— 五级环形图
# ---------------------------------------------------------------------------
def fig15_necessity():
    fig, ax = _canvas((10.6, 4.8))
    _card(ax)
    _pill(ax, 11, "治理倾向")

    _donut(fig, [0.04, 0.10, 0.52, 0.64],
           NECESSITY_VALUES, BLUE_5,
           "61.89%", "认为有必要 / 非常有必要", RED)

    for i, (label, value) in enumerate(zip(NECESSITY_LABELS, NECESSITY_VALUES)):
        y = 62 - i * 13.5
        _dot(ax, 62, y, BLUE_5[i], label, f"{value}人（{value / N * 100:.2f}%）")

    _note(ax, f"注：数据源于本次调查 {N} 份有效问卷。")
    _save(fig, "图片15.png")


# ---------------------------------------------------------------------------
# 图片16（第12板块）：治理需求 —— 横向进度条（多选题）
# ---------------------------------------------------------------------------
def fig16_demand():
    fig, ax = _canvas((10.2, 6.8))
    _card(ax)
    _pill(ax, 12, "治理需求")

    order = np.argsort(DEMAND_VALUES)[::-1]
    items = [(DEMAND_LABELS[i], DEMAND_VALUES[i]) for i in order]
    _progress_rows(ax, items, x_bar=32, top=78, row_h=8.4, bar_w=40)

    _note(ax, f"注：本题为多选题，百分比＝选择该项人数 / 总有效样本数（N={N}）。")
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
    print("全部公报风图片重制完成。")


if __name__ == "__main__":
    main()