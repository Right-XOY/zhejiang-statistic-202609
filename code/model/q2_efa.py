import numpy as np
import pandas as pd
from factor_analyzer.rotator import Rotator
from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity

import preprocess as pp


def pca_loadings(x, n_factors):
    r = np.corrcoef(x, rowvar=False)
    ev, evec = np.linalg.eigh(r)
    idx = np.argsort(ev)[::-1]
    ev, evec = ev[idx], evec[:, idx]
    loadings = evec[:, :n_factors] * np.sqrt(ev[:n_factors])
    return ev, loadings


def main():
    df = pp.clean(pp.load_raw())
    x = df[pp.EFA_ITEMS].astype(float).to_numpy()

    kmo = calculate_kmo(x)[1]
    chi2, p = calculate_bartlett_sphericity(x)
    pp.save_json({"kmo": round(float(kmo), 3), "bartlett_chi2": round(float(chi2), 3),
                  "df": len(pp.EFA_ITEMS) * (len(pp.EFA_ITEMS) - 1) // 2,
                  "p": "<0.001" if p < 0.001 else round(float(p), 4)},
                 "q2_efa", "kmo_bartlett.json")

    ev, loadings = pca_loadings(x, 4)
    eigen_df = pd.DataFrame({
        "成分": range(1, len(ev) + 1),
        "特征值": np.round(ev, 3),
        "方差%": np.round(ev / 14 * 100, 2),
        "累积%": np.round(np.cumsum(ev) / 14 * 100, 2),
    })
    pp.save_csv(eigen_df, "q2_efa", "eigenvalues.csv")

    rotated = Rotator(method="varimax").fit_transform(loadings)
    order = np.argsort((rotated ** 2).sum(axis=0))[::-1]
    rotated = rotated[:, order]
    for j in range(4):  # 主载荷取正，统一因子方向
        if rotated[np.argmax(np.abs(rotated[:, j])), j] < 0:
            rotated[:, j] *= -1

    # 方差解释：提取（特征值）与旋转（载荷平方和）
    rot_ss = (rotated ** 2).sum(axis=0)
    var_exp = pd.DataFrame({
        "成分": range(1, 5),
        "提取SS": np.round(ev[:4], 3),
        "提取方差%": np.round(ev[:4] / 14 * 100, 2),
        "提取累积%": np.round(np.cumsum(ev[:4]) / 14 * 100, 2),
        "旋转SS": np.round(rot_ss, 3),
        "旋转方差%": np.round(rot_ss / 14 * 100, 2),
        "旋转累积%": np.round(np.cumsum(rot_ss) / 14 * 100, 2),
    })
    pp.save_csv(var_exp, "q2_efa", "variance_explained.csv")

    comm = pd.DataFrame({
        "题项": [pp.ITEM_LABELS[c] for c in pp.EFA_ITEMS],
        "提取值": np.round((rotated ** 2).sum(axis=1), 3),
    })
    pp.save_csv(comm, "q2_efa", "communalities.csv")

    loadings_df = pd.DataFrame(
        np.round(rotated, 3),
        index=[pp.ITEM_LABELS[c] for c in pp.EFA_ITEMS],
        columns=[f"F{i+1}" for i in range(4)],
    )
    pp.save_csv(loadings_df.reset_index().rename(columns={"index": "题项"}),
                "q2_efa", "factor_loadings.csv")

    # 因子得分（回归法）+ 综合得分（方差贡献率加权）
    r = np.corrcoef(x, rowvar=False)
    coef = np.linalg.inv(r) @ rotated
    coef_df = pd.DataFrame(
        np.round(coef, 3),
        index=[pp.ITEM_LABELS[c] for c in pp.EFA_ITEMS],
        columns=[f"F{i+1}" for i in range(4)],
    )
    pp.save_csv(coef_df.reset_index().rename(columns={"index": "题项"}),
                "q2_efa", "factor_score_coefficients.csv")

    zx = (x - x.mean(axis=0)) / x.std(axis=0, ddof=1)
    scores = zx @ coef
    weights = rot_ss / rot_ss.sum()
    composite = scores @ weights
    pp.save_json({"weights": np.round(weights, 3).tolist()}, "q2_efa", "weights.json")

    score_df = pd.DataFrame(
        np.round(np.column_stack([scores, composite]), 4),
        columns=[f"F{i+1}" for i in range(4)] + ["composite"],
    )
    pp.save_csv(score_df, "q2_efa", "factor_scores.csv")

    print("q2 results saved to outputs/results/q2_efa/")
    print("weights:", np.round(weights, 3).tolist())
    print("cumulative variance:", round(float(rot_ss.sum() / 14 * 100), 2), "%")


if __name__ == "__main__":
    main()
