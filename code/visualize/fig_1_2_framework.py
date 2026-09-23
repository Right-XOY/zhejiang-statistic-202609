# -*- coding: utf-8 -*-
"""
论文 1.2「文献综述与研究缺口」配图 —— 研究局限与本研究创新框架
============================================================================
风格：与 figures/ 下 6 张板块图（respondent_poster.py）完全统一
  · 蓝色标题栏 + 白底卡片 + 浅蓝描边 + 淡蓝投影（卡片风格同一套）
  · 配色复用板块图主色板：蓝 #5094D5 / 深蓝 #5E82A2 / 浅蓝 #8FC7E5 /
    灰蓝 #88B7CB，红 #D15354 作唯一强调色（标注「创新」）
  · 字体 Microsoft YaHei，英文 Arial，关闭负号乱码
  · 布局：横向三列并行，自上而下「已有研究 → 三点局限 → 三点创新 → 目标」

运行：
    python code/visualize/fig_1_2_framework.py

输出：
    figures/研究局限与本研究创新框架.png   （dpi=800 高清位图）
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ----------------------------------------------------------------------------
# 第 1 节　全局样式与配色（与板块图 respondent_poster.py 保持一致）
# ----------------------------------------------------------------------------
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial"]
matplotlib.rcParams["axes.unicode_minus"] = False  # 关闭负号乱码

# 主色板（摘自板块图配色段，HEX 为准）
BLUE = "#5094D5"    # 主蓝    —— 标题栏、箭头、创新框
DBLUE = "#5E82A2"   # 深蓝    —— 局限框标题
LBLUE = "#8FC7E5"   # 浅蓝
SLATE = "#88B7CB"   # 灰蓝    —— 局限框描边
RED = "#D15354"     # 红      —— 唯一强调色（标注「创新」标签）

# 卡片样式（摘自板块图 C 字典）
CARD_BG = "#FFFFFF"
CARD_EDGE = "#D6E4EE"
CARD_SHADOW = "#EAF2F8"
TEXT = "#33414D"
TEXT_SUB = "#7B8B99"

FIG_W, FIG_H = 12, 6   # 论文单栏友好尺寸

# 输出目录：脚本位于 code/visualize，图上两级即项目根目录的 figures/
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIG_DIR = os.path.join(ROOT, "figures")

# ----------------------------------------------------------------------------
# 第 2 节　绘图工具函数
# ----------------------------------------------------------------------------
def rrect(ax, x, y, w, h, fc, ec, lw=1.1, rounding=0.10, zorder=2):
    """在数据坐标系中画一个圆角矩形。"""
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0,rounding_size={}".format(rounding),
            fc=fc, ec=ec, lw=lw, zorder=zorder,
        )
    )


def flow(ax, x, y1, y2, color=BLUE):
    """竖直向下箭头（x 为横坐标，y1 在上、y2 在下）。"""
    ax.annotate(
        "", xy=(x, y2), xytext=(x, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5), zorder=1,
    )


def title_card(ax, x, y_bottom, w, h, title):
    """绘制一个「蓝色标题栏 + 白底卡片」（复刻板块图 draw_card 风格）。

    x, y_bottom 为卡片左下角；w, h 为卡片宽高；title 为标题栏文字。
    标题栏凸出卡片顶边、靠左放置，白色加粗文字。
    """
    # 投影（淡蓝，向右下偏移）
    rrect(ax, x + 0.02, y_bottom - 0.028, w, h,
          fc=CARD_SHADOW, ec="none", lw=0, zorder=1)
    # 卡片本体（白底 + 浅蓝描边）
    rrect(ax, x, y_bottom, w, h,
          fc=CARD_BG, ec=CARD_EDGE, lw=1.0, rounding=0.10, zorder=2)
    # 蓝色标题栏（凸出卡片顶边、靠左）
    tab_h = 0.30
    tab_lift = 0.05
    tab_x = x + 0.10
    tab_w = len(title) * 0.20 + 0.30
    tab_y = y_bottom + h - tab_h + tab_lift
    rrect(ax, tab_x, tab_y, tab_w, tab_h,
          fc=BLUE, ec="none", lw=0, rounding=0.07, zorder=3)
    ax.text(tab_x + tab_w / 2, tab_y + tab_h / 2, title,
            ha="center", va="center", fontsize=12, color="#FFFFFF",
            fontweight="bold", zorder=4)


def column(ax, cx, y_top, w, h, tag, title, desc,
           edge, title_color, tag_color):
    """绘制一列「小标签 + 标题 + 描述」的圆角框，返回框体底部 y 坐标。"""
    rrect(ax, cx - w / 2, y_top - h, w, h,
          fc=CARD_BG, ec=edge, lw=1.3, rounding=0.10, zorder=2)
    # 小标签
    ax.text(cx, y_top - 0.22, tag, ha="center", va="center",
            fontsize=8.5, color=tag_color, zorder=3)
    # 标题
    ax.text(cx, y_top - 0.50, title, ha="center", va="center",
            fontsize=11.5, color=title_color, fontweight="bold", zorder=3)
    # 描述（两行）
    lines = desc.split("\n")
    start_y = y_top - 0.73
    for i, ln in enumerate(lines):
        ax.text(cx, start_y - i * 0.21, ln, ha="center", va="center",
                fontsize=8.8, color=TEXT, zorder=3)
    return y_top - h


# ----------------------------------------------------------------------------
# 第 3 节　内容与版面坐标（数据坐标系 0~12 × 0~6）
# ----------------------------------------------------------------------------
COL_CX = [2.6, 6.0, 9.4]   # 三列中心横坐标
COL_W = 2.9                # 单列框宽

LIMITS = [
    ("局限一", "数据来源割裂", "客观监测与居民感知脱节"),
    ("局限二", "机制刻画不足", "缺少因果路径的检验"),
    ("局限三", "对策缺乏量化支撑", "未对可干预变量排序"),
]
INNOVS = [
    ("创新一", "多源数据融合", "监测—投诉—问卷三位一体"),
    ("创新二", "因果机制识别", "刻画满意度的形成路径"),
    ("创新三", "治理对策量化", "排序可干预变量的边际效应"),
]

# 纵坐标（自上而下）
Y_TOP_BOTOM = 4.95     # 顶部卡片底边
TOP_H = 0.72           # 顶部卡片高
Y_LIM_TOP = 4.40       # 局限框顶边
LIM_H = 0.90           # 局限框高
Y_INN_TOP = 3.14       # 创新框顶边
INN_H = 0.94           # 创新框高
Y_BOT_BOTTOM = 1.12    # 底部卡片底边
BOT_H = 0.70           # 底部卡片高

CARD_X = 0.9
CARD_W = 10.2

# ----------------------------------------------------------------------------
# 第 4 节　绘图主流程
# ----------------------------------------------------------------------------
def build():
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, FIG_W)
    ax.set_ylim(0, FIG_H)
    ax.axis("off")

    # 4.1 顶部卡片：已有研究基础
    title_card(ax, CARD_X, Y_TOP_BOTOM, CARD_W, TOP_H, "已有研究基础")
    left_cx = CARD_X + CARD_W * 0.25    # 卡片左半区中心
    right_cx = CARD_X + CARD_W * 0.75   # 卡片右半区中心
    ax.text(left_cx, Y_TOP_BOTOM + 0.20, "国外：感知多因素、治理讲效益",
            ha="center", va="center", fontsize=9.5, color=TEXT, zorder=4)
    ax.text(right_cx, Y_TOP_BOTOM + 0.20, "国内：现状分区域、治理见困境",
            ha="center", va="center", fontsize=9.5, color=TEXT, zorder=4)

    # 4.2 三列「局限 → 创新」
    for cx, lim, inn in zip(COL_CX, LIMITS, INNOVS):
        # 局限框（白底 + 灰蓝描边 + 深蓝标题）
        bot_lim = column(ax, cx, Y_LIM_TOP, COL_W, LIM_H, *lim,
                         edge=SLATE, title_color=DBLUE, tag_color=TEXT_SUB)
        flow(ax, cx, bot_lim, Y_INN_TOP)                 # 局限 -> 创新
        # 创新框（白底 + 主蓝描边 + 主蓝标题 + 红色「创新」标签）
        bot_inn = column(ax, cx, Y_INN_TOP, COL_W, INN_H, *inn,
                         edge=BLUE, title_color=BLUE, tag_color=RED)
        flow(ax, cx, bot_inn, Y_BOT_BOTTOM + BOT_H)      # 创新 -> 目标

    # 顶部卡片 -> 三个局限框 的引导箭头
    for cx in COL_CX:
        flow(ax, cx, Y_TOP_BOTOM, Y_LIM_TOP)

    # 4.3 底部卡片：本研究创新框架
    title_card(ax, CARD_X, Y_BOT_BOTTOM, CARD_W, BOT_H, "本研究创新框架")
    ax.text(FIG_W / 2, Y_BOT_BOTTOM + 0.22,
            "以杭甬温三市居民为对象，融合监测、投诉与问卷多源数据",
            ha="center", va="center", fontsize=9.5, color=TEXT, zorder=4)

    return fig


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    fig = build()
    out = os.path.join(FIG_DIR, "研究局限与本研究创新框架.png")
    fig.savefig(out, dpi=800, transparent=True)
    plt.close(fig)
    print("已保存：{}".format(out))


if __name__ == "__main__":
    main()