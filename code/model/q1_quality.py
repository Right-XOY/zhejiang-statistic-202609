import numpy as np
import pandas as pd
import pingouin as pg
from scipy import stats
from statsmodels.sandbox.stats.runs import runstest_1samp
from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity

import preprocess as pp


def runs_test_table(df):
    cuts = {"gender": 2, "age": "median", "city": "median",
            "area": "median", "occupation": "median", "education": "median"}
    rows = []
    for var in pp.DEMOGRAPHIC_VARS:
        x = df[var].astype(float)
        cut = np.median(x) if cuts[var] == "median" else cuts[var]
        z, p = runstest_1samp(x, cutoff=cut)
        group = (x >= cut).astype(int)
        runs = 1 + int((np.diff(group) != 0).sum())
        rows.append({
            "变量": pp.VAR_LABELS[var], "检验值": int(cut),
            "个案数<检验值": int((x < cut).sum()), "个案数>=检验值": int((x >= cut).sum()),
            "游程数": runs, "Z": round(float(z), 3), "渐近显著性": round(float(p), 3),
        })
    return pd.DataFrame(rows)


def spearman_table(df):
    x = pp.reverse_scale(df["noise_impact"])  # noise_impact 原始为反向编码
    rows = []
    for c in pp.EFA_ITEMS:
        r, p = stats.spearmanr(x, df[c])
        rows.append({"题项": pp.ITEM_LABELS[c], "相关系数": round(r, 3),
                     "显著性": "<0.001" if p < 0.001 else round(p, 3)})
    return pd.DataFrame(rows)


def main():
    df = pp.clean(pp.load_raw())

    pp.save_csv(runs_test_table(df), "q1_quality", "runs_test.csv")
    pp.save_csv(spearman_table(df), "q1_quality", "spearman.csv")

    data = df[pp.RELIABILITY_ITEMS].astype(float).copy()
    data["noise_impact"] = pp.reverse_scale(data["noise_impact"])  # 反向计分
    alpha = pg.cronbach_alpha(data)[0]
    pp.save_json({"alpha": round(float(alpha), 3), "n_items": len(pp.RELIABILITY_ITEMS)},
                 "q1_quality", "reliability.json")

    x = df[pp.EFA_ITEMS].astype(float).to_numpy()
    kmo = calculate_kmo(x)[1]
    chi2, p = calculate_bartlett_sphericity(x)
    pp.save_json({"kmo": round(float(kmo), 3), "bartlett_chi2": round(float(chi2), 3),
                  "df": len(pp.EFA_ITEMS) * (len(pp.EFA_ITEMS) - 1) // 2,
                  "p": "<0.001" if p < 0.001 else round(float(p), 4)},
                 "q1_quality", "validity.json")

    print("q1 results saved to outputs/results/q1_quality/")


if __name__ == "__main__":
    main()
