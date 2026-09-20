import os

import numpy as np
import optuna
import pandas as pd
import xgboost as xgb
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold

import preprocess as pp


def main():
    df = pp.clean(pp.load_raw())
    scores = pd.read_csv(os.path.join(pp.OUT_DIR, "q2_efa", "factor_scores.csv"))
    x = pp.build_features(df, scores)
    y = df["satisfaction"].astype(int)
    skf = StratifiedKFold(5, shuffle=True, random_state=42)

    def objective(trial):
        params = {
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "max_depth": trial.suggest_int("max_depth", 3, 8),
            "n_estimators": trial.suggest_int("n_estimators", 100, 500),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 10, log=True),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-3, 10, log=True),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
            "random_state": 42,
        }
        f1s = []
        for tr, te in skf.split(x, y):
            m = xgb.XGBRegressor(**params).fit(x.iloc[tr], y.iloc[tr])
            pred = np.clip(np.rint(m.predict(x.iloc[te])), 1, 5).astype(int)
            f1s.append(f1_score(y.iloc[te], pred, average="macro"))
        return float(np.mean(f1s))

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction="maximize",
                                sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(objective, n_trials=30)

    pp.save_json({"best_macro_f1": round(study.best_value, 4),
                  "params": study.best_params},
                 "q6_tune", "best_params.json")
    print("best Macro-F1:", round(study.best_value, 4))
    print("best params:", study.best_params)


if __name__ == "__main__":
    main()
