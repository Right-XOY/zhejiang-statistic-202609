import os

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score
from sklearn.model_selection import StratifiedKFold
from statsmodels.miscmodels.ordinal_model import OrderedModel

import preprocess as pp

FOLDS = 5


def pred_logistic(po, x):
    return np.argmax(po.predict(x), axis=1) + 1


def main():
    df = pp.clean(pp.load_raw())
    scores = pd.read_csv(os.path.join(pp.OUT_DIR, "q2_efa", "factor_scores.csv"))
    x = pp.build_features(df, scores)
    y = df["satisfaction"].astype(int).to_numpy()

    skf = StratifiedKFold(n_splits=FOLDS, shuffle=True, random_state=42)
    rows = []
    for tr, te in skf.split(x, y):
        xtr, xte = x.iloc[tr], x.iloc[te]
        ytr, yte = y[tr], y[te]

        po = OrderedModel(ytr, xtr, distr="logit").fit(method="bfgs", maxiter=1000, disp=False)
        pred_po = pred_logistic(po, xte)

        xgbm = xgb.XGBRegressor(n_estimators=299, learning_rate=0.1528, max_depth=5,
                                subsample=0.655, colsample_bytree=0.865,
                                reg_lambda=0.1303, reg_alpha=0.0705, min_child_weight=7,
                                random_state=42)
        xgbm.fit(xtr, ytr)
        pred_xgb = np.clip(np.rint(xgbm.predict(xte)), 1, 5).astype(int)

        for name, pred in [("Logistic", pred_po), ("XGBoost", pred_xgb)]:
            rows.append({
                "模型": name,
                "Accuracy": round(accuracy_score(yte, pred), 4),
                "MacroF1": round(f1_score(yte, pred, average="macro"), 4),
                "Kappa": round(cohen_kappa_score(yte, pred), 4),
            })

    result = pd.DataFrame(rows).groupby("模型").agg(["mean", "std"]).round(4).reset_index()
    pp.save_csv(result, "q5_compare", "comparison.csv")
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
