import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from sklearn.metrics import auc, confusion_matrix, roc_curve
from sklearn.model_selection import StratifiedKFold, train_test_split
from statsmodels.miscmodels.ordinal_model import OrderedModel

import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import model.preprocess as pp

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIG_DIR = os.path.join(ROOT, "outputs", "figures")

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 虚拟变量 -> 原始变量的分组（列索引），SHAP 时按组加总合并
GROUPS = {
    "年龄": [0, 1, 2, 3],
    "学历": [4, 5, 6, 7],
    "城市": [8, 9],
    "居住区域": [10, 11, 12],
    "隔音墙": [13],
    "F1身心认知": [14],
    "F2情绪关系": [15],
    "F3环境噪声": [16],
    "F4生活噪声": [17],
}

# 贝叶斯调参（q6_tune）得到的最优 XGBoost 超参数
XGB_PARAMS = dict(n_estimators=299, learning_rate=0.1528, max_depth=5,
                  subsample=0.655, colsample_bytree=0.865,
                  reg_lambda=0.1303, reg_alpha=0.0705, min_child_weight=7,
                  random_state=42)


def _data():
    df = pp.clean(pp.load_raw())
    scores = pd.read_csv(os.path.join(pp.OUT_DIR, "q2_efa", "factor_scores.csv"))
    x = pp.build_features(df, scores)
    y = df["satisfaction"].astype(int)
    return x, y


def _models(xtr, ytr):
    po = OrderedModel(ytr, xtr, distr="logit").fit(method="bfgs", maxiter=1000, disp=False)
    xgr = xgb.XGBRegressor(**XGB_PARAMS).fit(xtr, ytr)
    xgc = xgb.XGBClassifier(objective="multi:softprob", num_class=5,
                            **XGB_PARAMS).fit(xtr, ytr - 1)
    return po, xgr, xgc


def plot_radar(out):
    x, y = _data()
    metrics = {"Accuracy": [], "Precision": [], "Recall": [], "Specificity": [], "Kappa": []}
    models = ["Logistic", "XGBoost"]
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    from sklearn.metrics import accuracy_score, cohen_kappa_score, precision_score, recall_score

    def specificity(y_true, y_pred):
        return np.mean([recall_score((y_true == k).astype(int), (y_pred == k).astype(int),
                                     pos_label=0, zero_division=0) for k in [1, 2, 3, 4, 5]])

    for tr, te in skf.split(x, y):
        xtr, xte = x.iloc[tr], x.iloc[te]
        ytr, yte = y[tr], y[te]
        po = OrderedModel(ytr, xtr, distr="logit").fit(method="bfgs", maxiter=1000, disp=False)
        xgr = xgb.XGBRegressor(**XGB_PARAMS).fit(xtr, ytr)
        pred_po = np.argmax(po.predict(xte), axis=1) + 1
        pred_xg = np.clip(np.rint(xgr.predict(xte)), 1, 5).astype(int)
        for name, pred in [("Logistic", pred_po), ("XGBoost", pred_xg)]:
            metrics.setdefault(name, {}).setdefault("Accuracy", []).append(accuracy_score(yte, pred))
            metrics[name].setdefault("Precision", []).append(precision_score(yte, pred, average="macro", zero_division=0))
            metrics[name].setdefault("Recall", []).append(recall_score(yte, pred, average="macro", zero_division=0))
            metrics[name].setdefault("Specificity", []).append(specificity(yte, pred))
            metrics[name].setdefault("Kappa", []).append(cohen_kappa_score(yte, pred))

    labels = ["Accuracy", "Precision", "Recall", "Specificity", "Kappa"]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(6.5, 6.5), subplot_kw=dict(polar=True))
    ax.grid(False)  # 关闭默认圆形网格
    for r in np.arange(0.2, 1.01, 0.2):
        ax.plot(angles, [r] * len(angles), color="lightgray", linewidth=0.5)
    for a in angles[:-1]:
        ax.plot([a, a], [0, 1], color="lightgray", linewidth=0.5)
    for name, c in zip(models, ["#1f77b4", "#ff7f0e"]):
        vals = [np.mean(metrics[name][k]) for k in labels] + [np.mean(metrics[name][labels[0]])]
        ax.plot(angles, vals, color=c, linewidth=2, label=name)
        ax.fill(angles, vals, color=c, alpha=0.1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_yticklabels([])
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1))
    plt.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()


def plot_confusion():
    x, y = _data()
    xtr, xte, ytr, yte = train_test_split(x, y, test_size=0.25, stratify=y, random_state=42)
    po, xgr, _ = _models(xtr, ytr)
    pred_po = np.argmax(po.predict(xte), axis=1) + 1
    pred_xg = np.clip(np.rint(xgr.predict(xte)), 1, 5).astype(int)
    labels = [1, 2, 3, 4, 5]
    for pred, fname in [(pred_po, "compare_confusion_logistic.png"),
                        (pred_xg, "compare_confusion_xgboost.png")]:
        cm = confusion_matrix(yte, pred, labels=labels)
        fig, ax = plt.subplots(figsize=(6, 5))
        im = ax.imshow(cm, cmap="Blues")
        ax.set_xticks(range(5), labels)
        ax.set_yticks(range(5), labels)
        ax.set_xlabel("预测等级")
        ax.set_ylabel("真实等级")
        for r in range(5):
            for c in range(5):
                ax.text(c, r, cm[r, c], ha="center", va="center",
                        color="white" if cm[r, c] > cm.max() / 2 else "black")
        fig.colorbar(im, ax=ax)
        plt.tight_layout()
        plt.savefig(os.path.join(FIG_DIR, fname), dpi=300, bbox_inches="tight")
        plt.close()


def plot_shap(out):
    x, y = _data()
    xtr, _, ytr, _ = train_test_split(x, y, test_size=0.25, stratify=y, random_state=42)
    po, xgr, _ = _models(xtr, ytr)

    explainer = shap.TreeExplainer(xgr)
    shap_xg = explainer.shap_values(xtr)
    beta = po.params[:-4].to_numpy()
    shap_po = (xtr.to_numpy() - xtr.to_numpy().mean(axis=0)) * beta

    imp_po, imp_xg = [], []
    for cols in GROUPS.values():
        imp_po.append(np.abs(shap_po[:, cols].sum(axis=1)).mean())
        imp_xg.append(np.abs(shap_xg[:, cols].sum(axis=1)).mean())
    imp_po, imp_xg = np.array(imp_po), np.array(imp_xg)
    names = list(GROUPS.keys())
    idx = np.argsort(imp_po + imp_xg)[::-1]

    fig, ax = plt.subplots(figsize=(8, 6))
    y_pos = np.arange(len(names))
    ax.barh(y_pos + 0.2, imp_po[idx], height=0.35, color="#1f77b4", label="有序Logistic")
    ax.barh(y_pos - 0.2, imp_xg[idx], height=0.35, color="#ff7f0e", label="XGBoost")
    ax.set_yticks(y_pos, [names[i] for i in idx])
    ax.set_xlabel("mean |SHAP|")
    ax.legend()
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()


def plot_roc(out):
    x, y = _data()
    xtr, xte, ytr, yte = train_test_split(x, y, test_size=0.25, stratify=y, random_state=42)
    po, _, xgc = _models(xtr, ytr)
    prob_po = po.predict(xte).to_numpy()
    prob_xg = xgc.predict_proba(xte)

    fig, ax = plt.subplots(figsize=(7, 6))
    colors = ["#1f77b4", "#ff7f0e"]
    for prob, name, c in zip([prob_po, prob_xg], ["有序Logistic", "XGBoost"], colors):
        fpr_grid = np.linspace(0, 1, 100)
        tprs, aucs = [], []
        for k in range(5):
            yb = (yte == k + 1).astype(int)
            fpr, tpr, _ = roc_curve(yb, prob[:, k])
            tprs.append(np.interp(fpr_grid, fpr, tpr))
            aucs.append(auc(fpr, tpr))
        mean_tpr = np.mean(tprs, axis=0)
        mean_auc = np.mean(aucs)
        ax.plot(fpr_grid, mean_tpr, color=c, linewidth=2,
                label=f"{name} (宏平均AUC={mean_auc:.3f})")
    ax.plot([0, 1], [0, 1], "k--", linewidth=1)
    ax.set_xlabel("假正率 FPR")
    ax.set_ylabel("真正率 TPR")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    plot_radar(os.path.join(FIG_DIR, "compare_radar.png"))
    plot_confusion()
    plot_shap(os.path.join(FIG_DIR, "compare_shap.png"))
    plot_roc(os.path.join(FIG_DIR, "compare_roc.png"))
    print("compare figures saved to outputs/figures/")


if __name__ == "__main__":
    main()
