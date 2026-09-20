import os
import json

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(ROOT, "data", "浙江省杭甬温环境噪声污染调查问卷.xlsx")
OUT_DIR = os.path.join(ROOT, "outputs", "results")

COLUMNS = [
    "id", "duration_raw", "gender", "age", "city", "area", "occupation",
    "education", "soundproof_wall", "home_office", "noise_impact", "insulation",
    "noise_traffic", "noise_life", "noise_construction", "noise_business",
    "noise_public", "noise_animal", "distance_source", "time_period",
    "eff_sleep_onset", "eff_sleep_interrupt", "eff_attention", "eff_relationship",
    "eff_mental", "eff_physical", "eff_hearing", "eff_emotion",
    "satisfaction", "governance_satisfaction",
    "coping_endure", "coping_negotiate", "coping_community", "coping_protect",
    "coping_official", "coping_legal", "coping_other",
    "awareness_channel", "awareness_policy", "awareness_necessity",
    "resp_gov", "resp_property", "resp_business", "resp_resident", "resp_other",
    "meas_enforce", "meas_law", "meas_facility", "meas_time", "meas_publicity",
    "meas_complaint", "meas_planning", "meas_other", "open_text",
]

# 6 类噪声源干扰 + 8 类噪声负面影响 = 14 个 EFA 题项
NOISE_SOURCES = ["noise_traffic", "noise_life", "noise_construction",
                 "noise_business", "noise_public", "noise_animal"]
NOISE_EFFECTS = ["eff_sleep_onset", "eff_sleep_interrupt", "eff_attention",
                 "eff_relationship", "eff_mental", "eff_physical",
                 "eff_hearing", "eff_emotion"]
EFA_ITEMS = NOISE_SOURCES + NOISE_EFFECTS

# 信度分析 22 项（EFA 14 项 + 整体感知/隔音/声源距离/两类满意度/三类认知）
RELIABILITY_ITEMS = EFA_ITEMS + [
    "noise_impact", "insulation", "distance_source",
    "satisfaction", "governance_satisfaction",
    "awareness_channel", "awareness_policy", "awareness_necessity",
]

DEMOGRAPHIC_VARS = ["gender", "age", "city", "area", "occupation", "education"]

ITEM_LABELS = {
    "noise_traffic": "交通噪声影响", "noise_life": "周围人生活噪声影响",
    "noise_construction": "装修/施工噪声影响", "noise_business": "商业经营噪声影响",
    "noise_public": "公共活动噪声影响", "noise_animal": "动物噪声影响",
    "eff_sleep_onset": "噪声入睡情况影响", "eff_sleep_interrupt": "噪声中断睡眠影响",
    "eff_attention": "噪声注意力影响", "eff_relationship": "噪声身边关系影响",
    "eff_mental": "噪声精神状态影响", "eff_physical": "噪声对身体健康影响",
    "eff_hearing": "噪声对听觉影响", "eff_emotion": "噪声对极端情绪影响",
}

VAR_LABELS = {
    "gender": "性别", "age": "年龄", "city": "现居住地",
    "area": "现居住区域", "occupation": "职业类型", "education": "文化程度",
}


def load_raw():
    df = pd.read_excel(DATA_PATH)
    df.columns = COLUMNS
    df["duration"] = df["duration_raw"].astype(str).str.extract(r"(\d+)").astype(float)
    return df


def clean(df, threshold=50):
    return df[df["duration"] > threshold].reset_index(drop=True)


def reverse_scale(s, max_val=5, min_val=1):
    return max_val + min_val - s


def build_features(df, scores):
    # 参照组：年龄19-30岁、教育本科及以上、城市温州、区域乡镇/农村
    x = pd.DataFrame({
        "Age1": (df["age"] == 1).astype(int), "Age2": (df["age"] == 3).astype(int),
        "Age3": (df["age"] == 4).astype(int), "Age4": (df["age"] == 5).astype(int),
        "Edu1": (df["education"] == 1).astype(int), "Edu2": (df["education"] == 2).astype(int),
        "Edu3": (df["education"] == 3).astype(int), "Edu4": (df["education"] == 4).astype(int),
        "CityHZ": (df["city"] == 1).astype(int), "CityNB": (df["city"] == 2).astype(int),
        "Area1": (df["area"] == 1).astype(int), "Area2": (df["area"] == 2).astype(int),
        "Area3": (df["area"] == 3).astype(int),
        "Wall": (df["soundproof_wall"] == 1).astype(int),
    })
    for f in ["F1", "F2", "F3", "F4"]:
        x[f] = scores[f]
    return x


def save_csv(df, subdir, name):
    path = os.path.join(OUT_DIR, subdir)
    os.makedirs(path, exist_ok=True)
    out = os.path.join(path, name)
    df.to_csv(out, index=False, encoding="utf-8-sig")
    return out


def save_json(obj, subdir, name):
    path = os.path.join(OUT_DIR, subdir)
    os.makedirs(path, exist_ok=True)
    out = os.path.join(path, name)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=lambda o: o.item())
    return out


if __name__ == "__main__":
    raw = load_raw()
    df = clean(raw)
    missing = {
        "home_office_missing": int(df["home_office"].isna().sum()),
        "home_office_missing_rate": round(float(df["home_office"].isna().mean()), 4),
        "soundproof_wall_unclear": int((df["soundproof_wall"] == 3).sum()),
    }
    save_csv(df, "preprocess", "cleaned_data.csv")
    save_json(missing, "preprocess", "missing_info.json")
    print("cleaned:", len(raw), "->", len(df))
    print("missing:", missing)
