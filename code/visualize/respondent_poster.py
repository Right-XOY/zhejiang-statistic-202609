# -*- coding: utf-8 -*-
"""
浙江省杭甬温环境噪声污染调查 · 受访者画像信息图（6 张单图系列）
================================================================================
风格：复刻「国家统计局公报」信息长图的卡片式设计（蓝色标题栏 + 白底卡片）。
输出：按板块序号拆成 6 张独立矢量图（SVG），尺寸按各自内容自适应。

运行：
    python code/visualize/respondent_poster.py

输出（统一输出到项目根目录的 figures/）：
    figures/板块1_性别构成.svg
    figures/板块2_城市分布.svg
    figures/板块3_年龄构成.svg
    figures/板块4_文化程度.svg
    figures/板块5_居住区域.svg
    figures/板块6_职业构成.svg
    SVG 为无损矢量图，文字已转曲，可直接插入论文或导入 AI / Inkscape 二次编辑。

改造指南：
    第 1 节 = 数据（改数字）      第 2 节 = 文字（改文案）
    第 3 节 = 配色（改颜色）      第 4 节 = 尺寸（改版式）
    改完直接重跑脚本即可重绘 6 张图，无需触碰第 6 节之后的绘图代码。
"""

import os

import matplotlib

matplotlib.use("Agg")  # 无界面后端，命令行 / 服务器均可出图

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle, Wedge

# ==============================================================================
# 第 0 节　输出与字体
# ==============================================================================

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIG_DIR = os.path.join(ROOT, "figures")  # 统一输出到项目根目录的 figures/

PIC1 = "板块1_性别构成"
PIC2 = "板块2_城市分布"
PIC3 = "板块3_年龄构成"
PIC4 = "板块4_文化程度"
PIC5 = "板块5_居住区域"
PIC6 = "板块6_职业构成"

FONT_CANDIDATES = [
    "Microsoft YaHei",      # 微软雅黑（Windows 自带，与公报字形最接近）
    "Source Han Sans SC",   # 思源黑体
    "Noto Sans CJK SC",
    "SimHei",
    "DengXian",
    "WenQuanYi Zen Hei",
]

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_LOCAL_FONTS = [
    os.path.join(os.path.dirname(os.path.dirname(_THIS_DIR)), "YaHei.Consolas.1.11b.ttf"),
]


def setup_font():
    """挑选可用的中文字体并写入 rcParams，返回字体名。"""
    available = {f.name for f in font_manager.fontManager.ttflist}
    picked = None
    for name in FONT_CANDIDATES:
        if name in available:
            picked = name
            break
    if picked is None:  # 系统字体全缺 -> 注册仓库自带字体
        for path in _LOCAL_FONTS:
            if os.path.exists(path):
                font_manager.fontManager.addfont(path)
                picked = font_manager.FontProperties(fname=path).get_name()
                break
    picked = picked or "sans-serif"
    plt.rcParams["font.sans-serif"] = [picked, "sans-serif"]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号
    plt.rcParams["svg.fonttype"] = "path"       # SVG 文字转曲，任何环境都能正确显示
    return picked


FONT_NAME = setup_font()

# ==============================================================================
# 第 1 节　数据变量（改这里就能换数据）
# ==============================================================================
# 均为「绝对人数」，占比由代码自动计算。各分项之和应与 N_TOTAL 一致。

N_TOTAL = 467  # 有效样本量（份）

# --- 板块 1：性别构成 ---------------------------------------------------------
GENDER = {
    "男性": 260,
    "女性": 207,
}

# --- 板块 2：城市分布 ---------------------------------------------------------
CITY = {
    "宁波": 192,
    "温州": 143,
    "杭州": 132,
}

# --- 板块 3：年龄构成 ---------------------------------------------------------
AGE = {
    "18岁及以下": 39,
    "19—30岁": 128,
    "31—45岁": 148,
    "46—60岁": 106,
    "61岁及以上": 46,
}
AGE_FOCUS_KEY = "61岁及以上"              # 右侧半环仪表聚焦的年龄段
AGE_FOCUS_LABEL = "其中61岁及以上人口为"
AGE_YOUTH_KEYS = ["19—30岁", "31—45岁"]   # 用于计算「中青年」合计
AGE_YOUTH_LABEL = "其中19—45岁中青年人口"

# --- 板块 4：文化程度 ---------------------------------------------------------
EDUCATION = {
    "小学及以下": 37,
    "初中": 68,
    "高中/中专/技校": 90,
    "大专": 81,
    "本科": 160,
    "硕士及以上": 31,
}

# --- 板块 5：居住区域 ---------------------------------------------------------
# 城镇 = 城市主城区 + 城市郊区 + 县城；乡村 = 乡镇 + 农村
AREA = {
    "城市主城区": 134,
    "城市郊区": 132,
    "县城": 90,
    "乡镇": 74,
    "农村": 37,
}
URBAN_KEYS = ["城市主城区", "城市郊区", "县城"]
RURAL_KEYS = ["乡镇", "农村"]
URBAN_NAME = "居住在城镇的人口"
RURAL_NAME = "居住在乡村的人口"

# --- 板块 6：职业构成 ---------------------------------------------------------
OCCUPATION = {
    "机关事业单位工作人员": 28,
    "农林牧渔从业者": 38,
    "企业工作人员": 130,
    "自由职业者/个体工商户": 65,
    "学生": 119,
    "军人/武警": 17,
    "退休人员": 29,
    "无业": 23,
    "其他": 18,
}
OCC_FOCUS_KEY = "企业工作人员"  # 大数字展示的 C 位职业

# ==============================================================================
# 第 2 节　文字变量（改这里就能换文案）
# ==============================================================================

MAIN_TITLE = "浙江省杭甬温环境噪声污染调查主要数据公报"
SUB_TITLE = "数据来源：项目组问卷调查（有效样本 467 份）"
FOOTNOTE = "注：本图数据来源于项目组问卷调查；因四舍五入，分项占比合计可能不等于 100%。"

TITLES = {
    "p1": "1. 性别构成",
    "p2": "2. 城市分布",
    "p3": "3. 年龄构成",
    "p4": "4. 文化程度",
    "p5": "5. 居住区域",
    "p6": "6. 职业构成",
}

UNIT_PEOPLE = "人"
UNIT_SAMPLE = "份"
UNIT_CITY = "个"
PCT_PRE = "占"

# --- 板块 1 ---
P1_LEAD = "有效样本量为"
P1_MALE_NAME = "男性人口"
P1_FEMALE_NAME = "女性人口"
P1_CENTER_TOP = "样本性别比"
P1_CENTER_SUB = "（以女性为100）"

# --- 板块 2 ---
P2_LEAD_CITY = "样本覆盖城市"
P2_LEAD_SAMPLE = "有效样本量"
P2_NOTE = "三市样本分布均衡，宁波市样本量最大"

# --- 板块 3 ---
P3_LEGEND_SUFFIX = "人口"
P3_YOUTH_SUFFIX = "，占"

# --- 板块 4 ---
P4_LEAD = "各文化程度人口为"

# --- 板块 5 ---
P5_DETAIL_TITLE = "五类居住区域细分"

# --- 板块 6 ---
P6_LEAD = "受访者中，企业工作人员人数最多"
P6_DETAIL_TITLE = "九类职业构成"

# ==============================================================================
# 第 3 节　配色变量（改这里就能换配色）
# ==============================================================================
# 10 色主色板（HEX 为准）。
# 为让 6 张图整体色调一致、色彩数量尽可能少，实际启用的只有 5 色：
#   冷色序列：LBLUE（最浅）→ SLATE → BLUE（主色）→ DBLUE（最深）
#   强调色　：RED（性别对比、年龄聚焦段、职业聚焦项）

RED = "#D15354"        # 1  红   —— 唯一强调色
LBLUE = "#8FC7E5"      # 2  浅蓝 —— 冷色序列 ①（最浅）
DBLUE = "#5E82A2"      # 3  深蓝 —— 冷色序列 ④（最深）
BLUE = "#5094D5"       # 4  蓝   —— 冷色序列 ③ / 主色
SLATE = "#88B7CB"      # 6  灰蓝 —— 冷色序列 ②

# 以下 5 色本轮未启用，保留备用（若想改用更活泼的暖色对比可在此换用）
ORANGE = "#E8B8AC"     # 5  橙
LORANGE = "#F9AD95"    # 7  浅橙
GREEN = "#ABDEB5"      # 8  浅绿
PALE = "#FEEEEE"       # 9  极浅粉
DORANGE = "#EC9F6D"    # 10 橙

C = {
    # --- 页面与卡片 ---
    "page_bg": "#FFFFFF",       # 页面底色
    "card_bg": "#FFFFFF",       # 卡片底色
    "card_edge": "#D6E4EE",     # 卡片描边
    "card_shadow": "#EAF2F8",   # 卡片投影
    "tab_bg": BLUE,             # 蓝色标题栏底色
    "tab_text": "#FFFFFF",      # 蓝色标题栏文字

    # --- 文字 ---
    "text": "#33414D",          # 主文字
    "text_sub": "#7B8B99",      # 次要文字
    "text_num": DBLUE,          # 强调数字
    "divider": "#E2EAF0",       # 分隔虚线
    "track": "#F0F5F9",         # 条形底槽

    # --- 图标 ---
    "icon": BLUE,
    "icon_dim": "#C3DAEA",

    # --- 图表取色（统一冷色序列，红为唯一强调色）---
    "seq_gender": [BLUE, RED],                       # 男蓝 / 女红
    "seq_city": [DBLUE, BLUE, SLATE],                # 按样本量由多到少：深 -> 浅
    "seq_age": [LBLUE, SLATE, BLUE, DBLUE, RED],     # 浅 -> 深，末段（61 岁及以上）红
    "seq_edu": [SLATE, BLUE, DBLUE],                 # 三档：义务教育 / 职业与专科 / 本科及以上
    "seq_urban": [BLUE, SLATE],                      # 城镇 / 乡村
    "sex_ratio": RED,           # 环形图中心性别比
    "focus": RED,               # 年龄聚焦段、职业聚焦项
    "gauge_bg": "#E9EEF3",      # 半环仪表的底环
}

# ==============================================================================
# 第 4 节　版式尺寸变量
# ==============================================================================

FIG_W = 7.0        # 6 张单图统一宽度（英寸），保证系列观感一致
PAD_X = 0.24       # 卡片左右留白
PAD_TOP = 0.28     # 卡片上方留白（容纳凸出卡片顶边的标题栏）
PAD_BOTTOM = 0.42  # 卡片下方留白（放数据来源行）

# 每张图的卡片高度（英寸）—— 按各自内容自适应，这就是「尺寸自适应」的入口
PANEL_CARD_H = {
    "p1": 3.30,
    "p2": 3.10,
    "p3": 4.40,
    "p4": 4.15,
    "p5": 3.80,
    "p6": 4.10,
}

LAYOUT = {
    "corner_in": 0.10,        # 卡片圆角半径（英寸）
    "tab_h_in": 0.30,         # 蓝色标题栏高度
    "tab_x_in": 0.08,         # 标题栏距卡片左边缘
    "tab_pad_in": 0.15,       # 标题栏左右内边距
    "tab_lift_in": 0.060,     # 标题栏上浮出卡片顶边的距离
    "content_top_gap_in": 0.070,   # 内容区距标题栏下缘
    "content_bottom_in": 0.090,    # 内容区距卡片下边缘
    "card_lw": 1.0,           # 卡片描边线宽
    "shadow_dx": 0.020,       # 投影水平偏移
    "shadow_dy": -0.028,      # 投影垂直偏移
    "source_y_in": 0.215,     # 数据来源行距图底
}

# 字号表（pt）—— 统一在此调整
FS = {
    "main_title": 19.0,
    "sub_title": 9.0,
    "footnote": 7.5,
    "tab": 12.0,
    "lead": 9.5,
    "big": 25.0,
    "big_s": 19.0,
    "unit": 9.5,
    "name": 9.5,
    "num": 10.5,
    "pct": 9.0,
    "tiny": 7.4,
    "legend": 8.6,
}

# ==============================================================================
# 第 5 节　派生量（由第 1 节数据自动算出）
# ==============================================================================


def pct(v, total):
    """百分比字符串，如 '55.67%'。"""
    return "{:.2f}%".format(v / total * 100.0)


def pct_val(v, total):
    """百分比小数（0~1），用于绘制半环仪表。"""
    return v / total


P1_MALE = GENDER["男性"]
P1_FEMALE = GENDER["女性"]
P1_MALE_PCT = pct(P1_MALE, N_TOTAL)
P1_FEMALE_PCT = pct(P1_FEMALE, N_TOTAL)
P1_RATIO = "{:.2f}".format(P1_MALE / P1_FEMALE * 100.0)  # 性别比（以女性为 100）

P3_FOCUS_VAL = AGE[AGE_FOCUS_KEY]
P3_FOCUS_PCT = pct(P3_FOCUS_VAL, N_TOTAL)
P3_FOCUS_FRAC = pct_val(P3_FOCUS_VAL, N_TOTAL)
P3_YOUTH_VAL = sum(AGE[k] for k in AGE_YOUTH_KEYS)
P3_YOUTH_PCT = pct(P3_YOUTH_VAL, N_TOTAL)

P5_URBAN_VAL = sum(AREA[k] for k in URBAN_KEYS)
P5_RURAL_VAL = sum(AREA[k] for k in RURAL_KEYS)
P5_URBAN_PCT = pct(P5_URBAN_VAL, N_TOTAL)
P5_RURAL_PCT = pct(P5_RURAL_VAL, N_TOTAL)

P6_FOCUS_VAL = OCCUPATION[OCC_FOCUS_KEY]
P6_FOCUS_PCT = pct(P6_FOCUS_VAL, N_TOTAL)


# ==============================================================================
# 第 6 节　通用绘图工具
# ==============================================================================


def measure_in(fig, s, fontsize, weight="normal"):
    """测量一段文字在画布上的物理宽/高（英寸），用于自动排布、避免重叠。"""
    t = fig.text(0, 0, s, fontsize=fontsize, fontweight=weight)
    try:
        renderer = fig.canvas.get_renderer()
    except AttributeError:
        fig.canvas.draw()
        renderer = fig.canvas.renderer
    bb = t.get_window_extent(renderer=renderer)
    t.remove()
    return bb.width / fig.dpi, bb.height / fig.dpi


def hchain(ax, x0, y0, parts, gap=0.006, align="left", zorder=10):
    """
    在 ax（0~1 归一化坐标）上从 x0 起水平依次绘制多段不同字号的文字。
    每段宽度实时测量，因此改数据后（如 467 -> 140545）也不会重叠。
    parts: [(文字, {text 关键字参数}), ...]；align: 'left' | 'center'
    """
    fig = ax.figure
    try:
        renderer = fig.canvas.get_renderer()
    except AttributeError:
        fig.canvas.draw()
        renderer = fig.canvas.renderer

    texts, widths = [], []
    for s, kw in parts:
        t = ax.text(0, y0, s, ha="left", va="center", zorder=zorder, **kw)
        bb = t.get_window_extent(renderer=renderer).transformed(ax.transAxes.inverted())
        texts.append(t)
        widths.append(bb.width)

    total = sum(widths) + gap * max(len(parts) - 1, 0)
    x = x0 if align == "left" else x0 - total / 2.0
    for t, w in zip(texts, widths):
        t.set_position((x, y0))
        x += w + gap
    return texts


# 当前卡片的内容区（相对卡片 0~1 坐标）——由 draw_card 在每张图开始时更新
CONTENT_RECT = [0.015, 0.025, 0.970, 0.840]


def cell_rect(rect_content):
    """
    把「内容区坐标」换算成「卡片坐标」。
    板块内文字用内容区坐标，而图标子 axes 挂在卡片上，
    因此图标的矩形必须经过这次换算才能与文字对齐。
    """
    x, y, w, h = rect_content
    return [
        CONTENT_RECT[0] + x * CONTENT_RECT[2],
        CONTENT_RECT[1] + y * CONTENT_RECT[3],
        w * CONTENT_RECT[2],
        h * CONTENT_RECT[3],
    ]


def sub_rect(fig, parent, rect):
    """把父 axes 的 0~1 相对矩形换算为 figure 绝对坐标矩形。"""
    p = parent.get_position()
    return [
        p.x0 + rect[0] * p.width,
        p.y0 + rect[1] * p.height,
        rect[2] * p.width,
        rect[3] * p.height,
    ]


def sub_ax(fig, parent, rect):
    """在父 axes 内创建「标注用」子 axes，坐标范围 0~1。"""
    ax = fig.add_axes(sub_rect(fig, parent, rect))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    return ax


def sub_inch_ax(fig, parent, rect):
    """
    在父 axes 内创建「英寸坐标」子 axes（1 数据单位 = 1 英寸）。
    x/y 单位物理长度一致，因此内部画的圆、图标不会被拉伸变形。
    返回 (axes, 宽英寸, 高英寸)。
    """
    r = sub_rect(fig, parent, rect)
    ax = fig.add_axes(r)
    ax.set_axis_off()
    w_in = r[2] * fig.get_figwidth()
    h_in = r[3] * fig.get_figheight()
    ax.set_xlim(0, max(w_in, 1e-6))
    ax.set_ylim(0, max(h_in, 1e-6))
    return ax, w_in, h_in


def square_ax(fig, parent, cx, cy, size_in):
    """
    以父 axes 的 (cx, cy) 为中心创建边长为 size_in 英寸的正方形子 axes，
    xlim/ylim 固定为 (-1.45, 1.45)，用于画饼图 / 环形图（保证是正圆）。
    """
    p = parent.get_position()
    fw, fh = fig.get_figwidth(), fig.get_figheight()
    w_fig, h_fig = size_in / fw, size_in / fh
    ax = fig.add_axes([p.x0 + cx * p.width - w_fig / 2.0,
                       p.y0 + cy * p.height - h_fig / 2.0, w_fig, h_fig])
    ax.set_axis_off()
    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.45, 1.45)
    ax.set_aspect("equal")
    return ax


def dash_line(ax, x0, x1, y, color=None, lw=0.9):
    """在 0~1 归一化 axes 上画一条水平分隔虚线。"""
    ax.plot([x0, x1], [y, y], color=color or C["divider"], lw=lw,
            linestyle=(0, (5, 4)), zorder=4)


def draw_pie(ax, values, colors, values_labels=None, donut=0.0,
             startangle=90, counterclock=True, label_radius=1.0):
    """
    在 square_ax 生成的 axes 上画饼图 / 环形图，并把百分比标注在扇区外侧。
    donut: 0 = 实心饼图；0.4 = 环宽占半径 40% 的环形图。
    """
    total = float(sum(values))
    wedge_kw = dict(edgecolor="white", linewidth=1.6)
    if donut > 0:
        wedge_kw["width"] = 1.0 - donut
    ax.pie(values, colors=colors, startangle=startangle,
           counterclock=counterclock, radius=1.0, wedgeprops=wedge_kw)

    if values_labels:
        import math
        cum = 0.0
        for v, lab in zip(values, values_labels):
            frac = v / total
            ang = cum + frac / 2.0
            a = math.radians(startangle + ang * 360.0 * (1 if counterclock else -1))
            ax.text(label_radius * math.cos(a), label_radius * math.sin(a), lab,
                    ha="center", va="center", fontsize=FS["pct"],
                    color=C["text"], zorder=12)
            cum += frac


# ==============================================================================
# 第 7 节　简易象形图标（全部用基础图元拼出，不依赖任何图片素材）
# ==============================================================================
# 以下函数均在「英寸坐标」axes（由 sub_inch_ax 创建）中绘制，
# 因此 cx / base / h / w 的单位都是英寸。


def icon_person(ax, cx, base, h, color, lw_ratio=0.115, zorder=6):
    """
    标准人形图标（洗手间标识风格）：
    圆头 + 圆角矩形躯干 + 圆头粗线手臂 / 双腿。
    cx   : 中轴横坐标
    base : 脚底纵坐标（人物向上生长）
    h    : 身高
    """
    head_r = 0.135 * h
    # ---- 头 ----
    ax.add_patch(Circle((cx, base + 0.850 * h), head_r,
                        fc=color, ec="none", zorder=zorder))
    # ---- 躯干：圆角矩形（肩 -> 胯），比梯形更接近标准人形标识 ----
    ax.add_patch(FancyBboxPatch(
        (cx - 0.165 * h, base + 0.320 * h), 0.330 * h, 0.385 * h,
        boxstyle="round,pad=0,rounding_size={}".format(0.072 * h),
        fc=color, ec="none", zorder=zorder))
    # ---- 手臂：从肩点斜向外下，圆头粗线 ----
    lw_arm = lw_ratio * h * 72.0
    for s in (-1, 1):
        ax.plot([cx + s * 0.150 * h, cx + s * 0.250 * h],
                [base + 0.660 * h, base + 0.390 * h],
                color=color, lw=lw_arm, solid_capstyle="round", zorder=zorder)
    # ---- 双腿：自胯部垂直向下，圆头粗线 ----
    lw_leg = lw_ratio * 1.10 * h * 72.0
    for s in (-1, 1):
        ax.plot([cx + s * 0.082 * h, cx + s * 0.098 * h],
                [base + 0.345 * h, base + 0.022 * h],
                color=color, lw=lw_leg, solid_capstyle="round", zorder=zorder)


def icon_city_bars(ax, x0, base, w, h_max, values, colors, names,
                   gap_ratio=0.34, zorder=5):
    """
    「数据匹配」柱形插画：每根柱子的高度按 values 比例生长，柱下标注名称。
    仅作视觉示意，精确数值仍以卡片右侧文字为准。
    base 之下预留约 0.16 英寸用于放名称。
    """
    n = len(values)
    vmax = float(max(values))
    seg = w / n
    bw = seg / (1.0 + gap_ratio)
    # ---- 基准线 ----
    ax.plot([x0, x0 + w], [base, base], color=C["divider"], lw=1.0, zorder=zorder - 1)
    for i, v in enumerate(values):
        bx = x0 + i * seg + (seg - bw) / 2.0
        bh = h_max * (0.36 + 0.64 * v / vmax)   # 最矮的柱子也保留 36% 高度，便于阅读
        ax.add_patch(FancyBboxPatch(
            (bx, base), bw, bh,
            boxstyle="round,pad=0,rounding_size={}".format(bw * 0.20),
            fc=colors[i % len(colors)], ec="none", zorder=zorder))
        ax.text(bx + bw / 2.0, base - 0.135, names[i], ha="center", va="center",
                fontsize=FS["name"], color=C["text_sub"], zorder=zorder)


def icon_book(ax, cx, base, w, color, zorder=5):
    """简笔翻开的书本。"""
    h = w * 0.80
    lw = max(1.4, w * 0.05)
    ax.add_patch(Polygon(
        [(cx, base + h * 0.18), (cx, base + h * 0.92),
         (cx - w / 2, base + h), (cx - w / 2, base + h * 0.26)],
        closed=True, fc=color, ec="white", lw=lw, zorder=zorder))
    ax.add_patch(Polygon(
        [(cx, base + h * 0.18), (cx, base + h * 0.92),
         (cx + w / 2, base + h), (cx + w / 2, base + h * 0.26)],
        closed=True, fc=color, ec="white", lw=lw, zorder=zorder))
    ax.plot([cx, cx], [base + h * 0.14, base + h * 0.92],
            color="white", lw=max(1.1, lw), zorder=zorder + 1)


def icon_pencil(ax, cx, base, w, color, zorder=5):
    """简笔铅笔（笔尖朝下直立）；笔杆用行色，笔尖浅蓝、笔尾橡皮深蓝（同色系）。"""
    h = w * 1.15
    bw = w * 0.50                       # 笔杆宽度
    x0 = cx - bw / 2.0
    y_tail = base + h * 0.275           # 杆身与笔尖的分界高度

    # ---- 笔尖（三角形，从杆底收到一点）----
    ax.add_patch(Polygon(
        [(x0, y_tail), (x0 + bw, y_tail), (cx, base + h * 0.02)],
        closed=True, fc=LBLUE, ec="none", zorder=zorder))
    # ---- 笔杆 ----
    ax.add_patch(Rectangle((x0, y_tail), bw, h * 0.58, fc=color, ec="none",
                           zorder=zorder))
    # ---- 笔尾橡皮 ----
    ax.add_patch(Rectangle((x0, y_tail + h * 0.58), bw, h * 0.145, fc=DBLUE,
                           ec="none", zorder=zorder))
    # ---- 笔尖尖端（深蓝一点，强化「笔」的识别度）----
    ax.add_patch(Polygon(
        [(cx - bw * 0.16, base + h * 0.115), (cx + bw * 0.16, base + h * 0.115),
         (cx, base + h * 0.02)],
        closed=True, fc=DBLUE, ec="none", zorder=zorder + 1))


def icon_building(ax, cx, base, w, color, zorder=5):
    """简笔楼房（城镇）。"""
    h = w * 1.45
    ax.add_patch(Rectangle((cx - w / 2, base), w, h * 0.78,
                           fc=color, ec="none", zorder=zorder))
    ax.add_patch(Rectangle((cx - w * 0.20, base + h * 0.78), w * 0.40, h * 0.22,
                           fc=color, ec="none", zorder=zorder))
    win_w, win_h = w * 0.17, h * 0.11
    for r in range(3):
        for c in range(2):
            ax.add_patch(Rectangle(
                (cx - w * 0.30 + c * w * 0.36, base + h * 0.16 + r * h * 0.20),
                win_w, win_h, fc="white", ec="none", zorder=zorder + 1))


def icon_village(ax, cx, base, w, color, zorder=5):
    """简笔农舍 + 小树（乡村）。"""
    h = w * 0.80
    ax.add_patch(Rectangle((cx - w * 0.34, base), w * 0.68, h * 0.52,
                           fc=color, ec="none", zorder=zorder))
    ax.add_patch(Polygon(
        [(cx - w / 2, base + h * 0.50), (cx, base + h), (cx + w / 2, base + h * 0.50)],
        closed=True, fc=color, ec="none", zorder=zorder))
    ax.add_patch(Rectangle((cx - w * 0.10, base), w * 0.20, h * 0.30,
                           fc="white", ec="none", zorder=zorder + 1))
    ax.add_patch(Circle((cx + w * 0.55, base + h * 0.66), w * 0.15,
                        fc=color, ec="none", zorder=zorder))
    ax.plot([cx + w * 0.55, cx + w * 0.55], [base, base + h * 0.66],
            color=color, lw=max(1.1, w * 0.05), zorder=zorder)


# ==============================================================================
# 第 8 节　卡片绘制
# ==============================================================================


def draw_card(fig, canvas, ax, title):
    """
    把一个 axes 单元格渲染成「白底 + 浅蓝描边 + 蓝色标题栏」的卡片。
    canvas: 覆盖整张图的英寸坐标 axes（卡片、投影、标题栏都画在它上面）
    ax    : 卡片对应的 axes（只用于取位置）
    返回  : 内容区 axes（0~1 坐标），并更新全局 CONTENT_RECT
    """
    global CONTENT_RECT
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    p = ax.get_position()
    fw, fh = fig.get_figwidth(), fig.get_figheight()
    x0, y0 = p.x0 * fw, p.y0 * fh
    w, h = p.width * fw, p.height * fh
    rad = LAYOUT["corner_in"]

    # ---- 投影 ----
    canvas.add_patch(FancyBboxPatch(
        (x0 + LAYOUT["shadow_dx"], y0 + LAYOUT["shadow_dy"]), w, h,
        boxstyle="round,pad=0,rounding_size={}".format(rad),
        fc=C["card_shadow"], ec="none", zorder=1, clip_on=False))

    # ---- 卡片本体 ----
    canvas.add_patch(FancyBboxPatch(
        (x0, y0), w, h,
        boxstyle="round,pad=0,rounding_size={}".format(rad),
        fc=C["card_bg"], ec=C["card_edge"], lw=LAYOUT["card_lw"],
        zorder=2, clip_on=False))

    # ---- 蓝色标题栏（左上角，上边缘略微凸出卡片顶边）----
    tab_h, lift = LAYOUT["tab_h_in"], LAYOUT["tab_lift_in"]
    tab_x = x0 + LAYOUT["tab_x_in"]
    tab_w = measure_in(fig, title, FS["tab"], weight="bold")[0] + LAYOUT["tab_pad_in"] * 2.0
    tab_y = y0 + h - tab_h + lift
    canvas.add_patch(FancyBboxPatch(
        (tab_x, tab_y), tab_w, tab_h,
        boxstyle="round,pad=0,rounding_size=0.075",
        fc=C["tab_bg"], ec="none", zorder=3, clip_on=False))
    canvas.text(tab_x + tab_w / 2.0, tab_y + tab_h / 2.0, title,
                ha="center", va="center", fontsize=FS["tab"], fontweight="bold",
                color=C["tab_text"], zorder=4)

    # ---- 内容区：位于标题栏下方，四周按 LAYOUT 留白 ----
    c_top = h - (tab_h - lift) - LAYOUT["content_top_gap_in"]
    c_bot = LAYOUT["content_bottom_in"]
    c_w = 0.970 * w
    c_x = 0.015 * w
    CONTENT_RECT = [c_x / w, c_bot / h, c_w / w, (c_top - c_bot) / h]
    return sub_ax(fig, ax, CONTENT_RECT)


# ==============================================================================
# 第 9 节　板块 1：性别构成
# ==============================================================================


def panel_gender(fig, ax, content):
    # ---- 顶部：有效样本量（小字 + 大数字 + 单位）----
    hchain(content, 0.300, 0.945, [
        (P1_LEAD, dict(fontsize=FS["lead"], color=C["text_sub"])),
        ("{}".format(N_TOTAL), dict(fontsize=FS["big"], color=C["text_num"], fontweight="bold")),
        (UNIT_SAMPLE, dict(fontsize=FS["unit"], color=C["text_sub"])),
    ], gap=0.010, align="left")

    # ---- 中间：环形图（男蓝 / 女红）----
    pie_ax = square_ax(fig, ax, cx=0.500, cy=0.455, size_in=2.45)
    draw_pie(pie_ax,
             values=[P1_MALE, P1_FEMALE],
             colors=C["seq_gender"],
             values_labels=[P1_MALE_PCT, P1_FEMALE_PCT],
             donut=0.42, startangle=90, counterclock=True, label_radius=1.22)

    # ---- 左侧：男性（小人图标 + 名称 + 人数 + 占比）----
    male_ax, mw, mh = sub_inch_ax(fig, ax, cell_rect([0.040, 0.590, 0.165, 0.300]))
    icon_person(male_ax, cx=mw * 0.50, base=mh * 0.06, h=mh * 0.72,
                color=C["seq_gender"][0], lw_ratio=0.115)
    content.text(0.122, 0.470, P1_MALE_NAME, ha="center", va="center",
                 fontsize=FS["name"], color=C["seq_gender"][0])
    hchain(content, 0.122, 0.335, [
        ("{}".format(P1_MALE), dict(fontsize=FS["big_s"], color=C["seq_gender"][0], fontweight="bold")),
        (UNIT_PEOPLE, dict(fontsize=FS["unit"], color=C["seq_gender"][0])),
    ], gap=0.004, align="center")
    content.text(0.122, 0.205, "{}{}".format(PCT_PRE, P1_MALE_PCT), ha="center",
                 va="center", fontsize=FS["pct"], color=C["seq_gender"][0])

    # ---- 右侧：女性（小人图标 + 名称 + 人数 + 占比）----
    fem_ax, fw2, fh2 = sub_inch_ax(fig, ax, cell_rect([0.795, 0.590, 0.165, 0.300]))
    icon_person(fem_ax, cx=fw2 * 0.50, base=fh2 * 0.06, h=fh2 * 0.72,
                color=C["seq_gender"][1], lw_ratio=0.115)
    content.text(0.878, 0.470, P1_FEMALE_NAME, ha="center", va="center",
                 fontsize=FS["name"], color=C["seq_gender"][1])
    hchain(content, 0.878, 0.335, [
        ("{}".format(P1_FEMALE), dict(fontsize=FS["big_s"], color=C["seq_gender"][1], fontweight="bold")),
        (UNIT_PEOPLE, dict(fontsize=FS["unit"], color=C["seq_gender"][1])),
    ], gap=0.004, align="center")
    content.text(0.878, 0.205, "{}{}".format(PCT_PRE, P1_FEMALE_PCT), ha="center",
                 va="center", fontsize=FS["pct"], color=C["seq_gender"][1])


# ==============================================================================
# 第 10 节　板块 2：城市分布
# ==============================================================================


def panel_city(fig, ax, content):
    city_items = list(CITY.items())

    # ---- 左侧：与数据匹配的柱形插画（柱高 = 样本量比例，柱下标注城市名）----
    art_ax, aw, ah = sub_inch_ax(fig, ax, cell_rect([0.020, 0.055, 0.430, 0.865]))
    icon_city_bars(art_ax,
                   x0=aw * 0.04, base=ah * 0.215, w=aw * 0.92, h_max=ah * 0.700,
                   values=[v for _, v in city_items],
                   colors=C["seq_city"],
                   names=[k for k, _ in city_items],
                   gap_ratio=0.55)

    # ---- 右侧顶部：两个大数字 ----
    hchain(content, 0.500, 0.880, [
        (P2_LEAD_CITY, dict(fontsize=FS["lead"], color=C["text_sub"])),
        ("{}".format(len(CITY)), dict(fontsize=FS["big"], color=C["text_num"], fontweight="bold")),
        (UNIT_CITY, dict(fontsize=FS["unit"], color=C["text_sub"])),
    ], gap=0.010, align="left")
    hchain(content, 0.500, 0.690, [
        (P2_LEAD_SAMPLE, dict(fontsize=FS["lead"], color=C["text_sub"])),
        ("{}".format(N_TOTAL), dict(fontsize=FS["big"], color=C["text_num"], fontweight="bold")),
        (UNIT_PEOPLE, dict(fontsize=FS["unit"], color=C["text_sub"])),
    ], gap=0.010, align="left")

    dash_line(content, 0.500, 0.980, 0.580)

    # ---- 右下：三市明细（城市名 + 人数 + 占比；人数用左侧柱子的同色，颜色即对应关系）----
    for i, (name, val) in enumerate(city_items):
        y = 0.470 - i * 0.140
        col = C["seq_city"][i % len(C["seq_city"])]
        content.text(0.500, y, name, ha="left", va="center",
                     fontsize=FS["num"], color=C["text"])
        hchain(content, 0.615, y, [
            ("{}".format(val), dict(fontsize=FS["big_s"], color=col, fontweight="bold")),
            (UNIT_PEOPLE, dict(fontsize=FS["tiny"], color=C["text_sub"])),
        ], gap=0.003, align="left")
        content.text(0.820, y, pct(val, N_TOTAL), ha="left", va="center",
                     fontsize=FS["pct"], color=C["text_sub"])

    content.text(0.500, 0.055, P2_NOTE, ha="left", va="center",
                 fontsize=FS["tiny"], color=C["text_sub"])


# ==============================================================================
# 第 11 节　板块 3：年龄构成
# ==============================================================================


def panel_age(fig, ax, content):
    age_items = list(AGE.items())
    age_vals = [v for _, v in age_items]
    age_labs = [pct(v, N_TOTAL) for _, v in age_items]
    age_colors = C["seq_age"][:len(age_items)]

    # ---- 左侧：五段环形图 + 中心人群剪影 ----
    pie_ax = square_ax(fig, ax, cx=0.255, cy=0.610, size_in=2.55)
    draw_pie(pie_ax, values=age_vals, colors=age_colors, values_labels=age_labs,
             donut=0.46, startangle=90, counterclock=False, label_radius=1.14)
    pie_ax.add_patch(Circle((0, 0.14), 0.115, fc=DBLUE, ec="none", zorder=12))
    pie_ax.add_patch(Polygon([(-0.17, -0.05), (0.17, -0.05), (0.11, 0.05), (-0.11, 0.05)],
                             closed=True, fc=DBLUE, ec="none", zorder=12))
    pie_ax.add_patch(Circle((-0.31, 0.07), 0.098, fc=BLUE, ec="none", zorder=12))
    pie_ax.add_patch(Polygon([(-0.45, -0.05), (-0.16, -0.05), (-0.21, 0.00), (-0.40, 0.00)],
                             closed=True, fc=BLUE, ec="none", zorder=12))
    pie_ax.add_patch(Circle((0.31, 0.07), 0.098, fc=LBLUE, ec="none", zorder=12))
    pie_ax.add_patch(Polygon([(0.16, -0.05), (0.45, -0.05), (0.40, 0.00), (0.21, 0.00)],
                             closed=True, fc=LBLUE, ec="none", zorder=12))

    # ---- 左下：中青年人口补充说明 ----
    hchain(content, 0.020, 0.075, [
        (AGE_YOUTH_LABEL, dict(fontsize=FS["tiny"], color=C["text_sub"])),
        ("{}人".format(P3_YOUTH_VAL), dict(fontsize=FS["tiny"], color=C["text_num"], fontweight="bold")),
        (P3_YOUTH_SUFFIX + P3_YOUTH_PCT, dict(fontsize=FS["tiny"], color=C["text_sub"])),
    ], gap=0.002, align="left")

    # ---- 右上：五段图例（色块 + 名称 + 人数 + 占比）----
    for i, (name, val) in enumerate(age_items):
        y = 0.935 - i * 0.098
        content.add_patch(Rectangle((0.545, y - 0.036), 0.028, 0.072,
                                    fc=age_colors[i], ec="none", zorder=6))
        content.text(0.592, y, name + P3_LEGEND_SUFFIX, ha="left", va="center",
                     fontsize=FS["legend"], color=C["text"])
        hchain(content, 0.800, y, [
            ("{}".format(val), dict(fontsize=FS["legend"], color=C["text_num"], fontweight="bold")),
            (UNIT_PEOPLE, dict(fontsize=FS["tiny"], color=C["text_sub"])),
        ], gap=0.002, align="left")
        content.text(0.910, y, "{}{}".format(PCT_PRE, pct(val, N_TOTAL)), ha="left",
                     va="center", fontsize=FS["legend"], color=C["text_sub"])

    dash_line(content, 0.545, 0.980, 0.435)

    # ---- 右下：61岁及以上人口（大数字 + 半环仪表）----
    content.text(0.545, 0.365, AGE_FOCUS_LABEL, ha="left", va="center",
                 fontsize=FS["lead"], color=C["text_sub"])
    hchain(content, 0.545, 0.250, [
        ("{}".format(P3_FOCUS_VAL), dict(fontsize=FS["big"], color=C["text_num"], fontweight="bold")),
        (UNIT_PEOPLE, dict(fontsize=FS["unit"], color=C["text_sub"])),
    ], gap=0.006, align="left")
    content.text(0.545, 0.150, "{}{}".format(PCT_PRE, P3_FOCUS_PCT), ha="left",
                 va="center", fontsize=FS["num"], color=C["focus"])

    # 半环仪表：显示 61 岁及以上占比
    gauge_ax, gw, gh = sub_inch_ax(fig, ax, cell_rect([0.760, 0.020, 0.225, 0.360]))
    r = min(gw * 0.5, gh) * 0.94
    gcx, gcy = gw * 0.5, gh * 0.05
    gauge_ax.add_patch(Wedge((gcx, gcy), r, 0, 180, width=r * 0.40,
                             fc=C["gauge_bg"], ec="none", zorder=4))
    gauge_ax.add_patch(Wedge((gcx, gcy), r, 180 - 180 * P3_FOCUS_FRAC, 180,
                             width=r * 0.40, fc=C["focus"], ec="none", zorder=5))
    gauge_ax.text(gcx, gcy + r * 0.42, P3_FOCUS_PCT, ha="center", va="center",
                  fontsize=FS["num"], color=C["text"], fontweight="bold")


# ==============================================================================
# 第 12 节　板块 4：文化程度（横向条形图）
# ==============================================================================


def panel_education(fig, ax, content):
    edu_items = list(EDUCATION.items())
    max_val = max(v for _, v in edu_items)

    # 行布局：自上而下
    top, row_h, row_gap = 0.895, 0.112, 0.026
    # 图标类型 + 学历档位（0 义务教育 / 1 职业与专科 / 2 本科及以上）
    edu_meta = {
        "小学及以下": (0, "pencil"),
        "初中": (0, "book"),
        "高中/中专/技校": (1, "book"),
        "大专": (1, "book"),
        "本科": (2, "book"),
        "硕士及以上": (2, "book"),
    }
    bar_x0, bar_w_max = 0.360, 0.400

    for i, (name, val) in enumerate(edu_items):
        y = top - row_h / 2.0 - i * (row_h + row_gap)
        tier, kind = edu_meta.get(name, (1, "book"))
        icol = C["seq_edu"][tier]      # 同一档学历共用一个色调

        # --- 左侧图标（按图标框宽高双向约束，避免图形溢出框外）---
        i_ax, iw, ih = sub_inch_ax(fig, ax, cell_rect([0.018, y - 0.058, 0.070, 0.116]))
        if kind == "pencil":
            gw_icon = min(iw * 0.72, ih * 0.80)   # 铅笔高 = 1.15 × 宽
            icon_pencil(i_ax, cx=iw * 0.50, base=ih * 0.08, w=gw_icon, color=icol)
        else:
            gw_icon = min(iw * 0.82, ih * 1.05)   # 书本高 = 0.80 × 宽
            icon_book(i_ax, cx=iw * 0.50, base=ih * 0.12, w=gw_icon, color=icol)

        # --- 学历名称 ---
        content.text(0.110, y, name, ha="left", va="center",
                     fontsize=FS["legend"], color=C["text"])

        # --- 条形（背景槽 + 实际值）---
        content.add_patch(FancyBboxPatch(
            (bar_x0, y - 0.038), bar_w_max, 0.076,
            boxstyle="round,pad=0,rounding_size=0.030",
            fc=C["track"], ec="none", zorder=4))
        content.add_patch(FancyBboxPatch(
            (bar_x0, y - 0.038), max(bar_w_max * val / max_val, 0.012), 0.076,
            boxstyle="round,pad=0,rounding_size=0.030",
            fc=icol, ec="none", zorder=5))

        # --- 数值 + 占比 ---
        hchain(content, bar_x0 + bar_w_max + 0.020, y, [
            ("{}".format(val), dict(fontsize=FS["num"], color=C["text_num"], fontweight="bold")),
            (UNIT_PEOPLE, dict(fontsize=FS["tiny"], color=C["text_sub"])),
            ("　" + pct(val, N_TOTAL), dict(fontsize=FS["tiny"], color=C["text_sub"])),
        ], gap=0.003, align="left")

    content.text(0.018, 0.040, P4_LEAD, ha="left", va="center",
                 fontsize=FS["tiny"], color=C["text_sub"])


# ==============================================================================
# 第 13 节　板块 5：居住区域
# ==============================================================================


def panel_area(fig, ax, content):
    # ---- 左：环形图（城镇 / 乡村）----
    pie_ax = square_ax(fig, ax, cx=0.240, cy=0.560, size_in=1.85)
    draw_pie(pie_ax,
             values=[P5_URBAN_VAL, P5_RURAL_VAL],
             colors=C["seq_urban"],
             values_labels=[P5_URBAN_PCT, P5_RURAL_PCT],
             donut=0.44, startangle=90, counterclock=False, label_radius=1.32)
    # 中心：楼房图标
    pie_ax.add_patch(Rectangle((-0.24, -0.26), 0.48, 0.36, fc=BLUE, ec="none", zorder=12))
    pie_ax.add_patch(Rectangle((-0.09, 0.10), 0.18, 0.13, fc=BLUE, ec="none", zorder=12))
    for r in range(3):
        for c in range(2):
            pie_ax.add_patch(Rectangle((-0.19 + c * 0.22, -0.19 + r * 0.13), 0.10, 0.07,
                                       fc="white", ec="none", zorder=13))

    # ---- 左下：五类居住区域细分 ----
    content.text(0.018, 0.105, P5_DETAIL_TITLE, ha="left", va="center",
                 fontsize=FS["tiny"], color=C["text_sub"])
    content.text(0.018, 0.050,
                 "  ".join(["{} {}人".format(k, v) for k, v in AREA.items()]),
                 ha="left", va="center", fontsize=FS["tiny"], color=C["text_sub"])

    # ---- 右上：城镇 ----
    ub_ax, uw, uh = sub_inch_ax(fig, ax, cell_rect([0.520, 0.640, 0.095, 0.250]))
    icon_building(ub_ax, cx=uw * 0.50, base=uh * 0.05, w=uw * 0.50, color=BLUE)
    content.text(0.645, 0.845, URBAN_NAME, ha="left", va="center",
                 fontsize=FS["name"], color=C["text"])
    hchain(content, 0.645, 0.720, [
        ("{}".format(P5_URBAN_VAL), dict(fontsize=FS["big_s"], color=C["text_num"], fontweight="bold")),
        (UNIT_PEOPLE, dict(fontsize=FS["unit"], color=C["text_sub"])),
    ], gap=0.004, align="left")
    content.text(0.645, 0.610, "{}{}".format(PCT_PRE, P5_URBAN_PCT), ha="left",
                 va="center", fontsize=FS["pct"], color=C["text_sub"])

    dash_line(content, 0.520, 0.980, 0.545)

    # ---- 右下：乡村 ----
    vb_ax, vw, vh = sub_inch_ax(fig, ax, cell_rect([0.520, 0.185, 0.095, 0.250]))
    icon_village(vb_ax, cx=vw * 0.40, base=vh * 0.10, w=vw * 0.60, color=SLATE)
    content.text(0.645, 0.390, RURAL_NAME, ha="left", va="center",
                 fontsize=FS["name"], color=C["text"])
    hchain(content, 0.645, 0.265, [
        ("{}".format(P5_RURAL_VAL), dict(fontsize=FS["big_s"], color=C["text_num"], fontweight="bold")),
        (UNIT_PEOPLE, dict(fontsize=FS["unit"], color=C["text_sub"])),
    ], gap=0.004, align="left")
    content.text(0.645, 0.155, "{}{}".format(PCT_PRE, P5_RURAL_PCT), ha="left",
                 va="center", fontsize=FS["pct"], color=C["text_sub"])


# ==============================================================================
# 第 14 节　板块 6：职业构成
# ==============================================================================


def panel_occupation(fig, ax, content):
    # ---- 顶部：结论说明 + 大数字（居中）----
    content.text(0.500, 0.945, P6_LEAD, ha="center", va="center",
                 fontsize=FS["lead"], color=C["text_sub"])
    hchain(content, 0.500, 0.820, [
        ("{}".format(P6_FOCUS_VAL), dict(fontsize=FS["big"], color=C["text_num"], fontweight="bold")),
        (UNIT_PEOPLE, dict(fontsize=FS["unit"], color=C["text_sub"])),
        ("  {}{}".format(PCT_PRE, P6_FOCUS_PCT), dict(fontsize=FS["pct"], color=C["focus"])),
    ], gap=0.006, align="center")

    # ---- 中部：十人图标排（通栏，1 人 ≈ 10%，蓝色为聚焦职业）----
    row_ax, rw, rh = sub_inch_ax(fig, ax, cell_rect([0.030, 0.555, 0.940, 0.170]))
    n_dots = 10
    n_hi = max(1, round(P6_FOCUS_VAL / N_TOTAL * n_dots))
    step = rw / (n_dots + 0.5)
    for k in range(n_dots):
        icon_person(row_ax, cx=step * (k + 0.50), base=rh * 0.04, h=rh * 0.90,
                    color=C["focus"] if k < n_hi else C["icon_dim"],
                    lw_ratio=0.135)

    # ---- 下半：九类职业迷你条形（2 列 × 5 行，单行内 色块+名称+条+数值）----
    occ_items = list(OCCUPATION.items())
    max_occ = max(v for _, v in occ_items)
    dash_line(content, 0.020, 0.980, 0.500)

    content.text(0.020, 0.455, P6_DETAIL_TITLE, ha="left", va="center",
                 fontsize=FS["tiny"], color=C["text_sub"])

    col_w, row_step = 0.505, 0.088
    track_w = 0.115
    for idx, (name, val) in enumerate(occ_items):
        c, r = idx % 2, idx // 2
        x = 0.010 + c * col_w
        y = 0.375 - r * row_step
        # 聚焦职业用红色，其余统一主蓝色（整图只保留两种颜色）
        col = C["focus"] if name == OCC_FOCUS_KEY else BLUE

        content.add_patch(Rectangle((x + 0.000, y - 0.018), 0.018, 0.036,
                                    fc=col, ec="none", zorder=6))
        content.text(x + 0.024, y, name, ha="left", va="center",
                     fontsize=FS["tiny"], color=C["text"])
        content.add_patch(Rectangle((x + 0.215, y - 0.015), track_w, 0.030,
                                    fc=C["track"], ec="none", zorder=4))
        content.add_patch(Rectangle(
            (x + 0.215, y - 0.015), max(track_w * val / max_occ, 0.005), 0.030,
            fc=col, ec="none", zorder=5))
        content.text(x + 0.335, y, "{}人　{}".format(val, pct(val, N_TOTAL)),
                     ha="left", va="center", fontsize=FS["tiny"], color=C["text_sub"])


# ==============================================================================
# 第 15 节　主流程：逐板块渲染出 6 张独立单图
# ==============================================================================

PANELS = [
    ("p1", PIC1, panel_gender),
    ("p2", PIC2, panel_city),
    ("p3", PIC3, panel_age),
    ("p4", PIC4, panel_education),
    ("p5", PIC5, panel_area),
    ("p6", PIC6, panel_occupation),
]


def render_panel(key, filename, drawer):
    """渲染单个板块为一张独立矢量图（SVG），写入 figures/。"""
    card_h = PANEL_CARD_H[key]
    card_w = FIG_W - 2 * PAD_X
    fig_h = PAD_BOTTOM + card_h + PAD_TOP

    fig = plt.figure(figsize=(FIG_W, fig_h))
    fig.patch.set_facecolor(C["page_bg"])

    # 全图英寸坐标画布：卡片、标题栏、投影都画在这一层
    canvas = fig.add_axes([0, 0, 1, 1], zorder=-10)
    canvas.set_axis_off()
    canvas.set_xlim(0, FIG_W)
    canvas.set_ylim(0, fig_h)
    canvas.patch.set_visible(False)

    # 卡片（轴即卡片本身，位置用 figure 绝对坐标）
    ax = fig.add_axes([PAD_X / FIG_W, PAD_BOTTOM / fig_h,
                       card_w / FIG_W, card_h / fig_h])
    content = draw_card(fig, canvas, ax, TITLES[key])
    drawer(fig, ax, content)

    svg = os.path.join(FIG_DIR, filename + ".svg")
    fig.savefig(svg, facecolor=C["page_bg"])
    plt.close(fig)
    return svg


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    for key, filename, drawer in PANELS:
        svg = render_panel(key, filename, drawer)
        print("已保存：{}".format(svg))
    print("共 6 张矢量图；使用字体：{}".format(FONT_NAME))


if __name__ == "__main__":
    main()