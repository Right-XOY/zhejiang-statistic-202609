import os

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize
from statsmodels.miscmodels.ordinal_model import OrderedModel
from statsmodels.stats.outliers_influence import variance_inflation_factor

import preprocess as pp

N_THR = 4  # 5级满意度 -> 4个切分点


def parallel_test(y, x, po):
    # 广义模型（partial proportional odds）似然比检验
    n, k = x.shape
    xa = x.to_numpy().astype(float)
    ya = y.to_numpy().astype(int)

    def negll(params):
        alpha = params[:N_THR]
        beta = params[N_THR:].reshape(N_THR, k)
        lin = alpha[:, None] - beta @ xa.T
        cum = 1 / (1 + np.exp(-lin))
        p = np.empty(n)
        for i in range(n):
            hi = cum[ya[i] - 1, i] if ya[i] <= N_THR else 1.0
            lo = cum[ya[i] - 2, i] if ya[i] >= 2 else 0.0
            p[i] = hi - lo
        return -np.sum(np.log(np.clip(p, 1e-12, None)))

    alpha0 = po.model.transform_threshold_params(po.params.to_numpy())[1:-1]
    init = np.concatenate([alpha0, np.tile(po.params[:-N_THR].to_numpy(), N_THR)])
    opt = minimize(negll, init, method="bfgs", options={"maxiter": 2000})
    chi2 = 2 * (-opt.fun - po.llf)
    return chi2, k * (N_THR - 1), 1 - stats.chi2.cdf(chi2, k * (N_THR - 1))


def main():
    df = pp.clean(pp.load_raw())
    scores = pd.read_csv(os.path.join(pp.OUT_DIR, "q2_efa", "factor_scores.csv"))
    x = pp.build_features(df, scores)
    y = df["satisfaction"].astype(int)

    po = OrderedModel(y, x, distr="logit").fit(method="bfgs", maxiter=1000, disp=False)
    thr = po.model.transform_threshold_params(po.params.to_numpy())[1:-1]
    beta = po.params[:-N_THR].to_numpy()
    se = po.bse[:-N_THR].to_numpy()
    z = po.tvalues[:-N_THR].to_numpy()
    pv = po.pvalues[:-N_THR].to_numpy()

    # 阈值标准误（delta 方法）
    th_params = po.params[-N_THR:].to_numpy()
    cov_th = po.cov_params().to_numpy()[-N_THR:, -N_THR:]
    exps = np.exp(th_params[1:])
    thr_se = []
    for j in range(N_THR):
        g = np.zeros(N_THR)
        g[0] = 1.0
        g[1:j + 1] = exps[:j]
        thr_se.append(np.sqrt(g @ cov_th @ g))

    rows = []
    for j in range(N_THR):
        wald = (thr[j] / thr_se[j]) ** 2
        p_thr = 2 * (1 - stats.norm.cdf(abs(thr[j] / thr_se[j])))
        rows.append({"变量": f"阈值Y={j + 1}", "β": round(float(thr[j]), 3),
                     "SE": round(float(thr_se[j]), 3), "Wald": round(float(wald), 3),
                     "p": "<0.001" if p_thr < 0.001 else round(float(p_thr), 3),
                     "OR": "", "CI下限": "", "CI上限": ""})
    for i, name in enumerate(x.columns):
        rows.append({"变量": name, "β": round(float(beta[i]), 3), "SE": round(float(se[i]), 3),
                     "Wald": round(float(z[i] ** 2), 3),
                     "p": "<0.001" if pv[i] < 0.001 else round(float(pv[i]), 3),
                     "OR": round(float(np.exp(beta[i])), 3),
                     "CI下限": round(float(np.exp(beta[i] - 1.96 * se[i])), 3),
                     "CI上限": round(float(np.exp(beta[i] + 1.96 * se[i])), 3)})
    pp.save_csv(pd.DataFrame(rows), "q4_logistic", "params.csv")

    n = len(y)
    cox = 1 - np.exp(2 * (po.llnull - po.llf) / n)
    nagel = cox / (1 - np.exp(2 * po.llnull / n))
    lr = 2 * (po.llf - po.llnull)
    pp.save_json({
        "null_2LL": round(float(-2 * po.llnull), 3),
        "model_2LL": round(float(-2 * po.llf), 3),
        "lr_chi2": round(float(lr), 3),
        "lr_df": x.shape[1],
        "lr_p": "<0.001" if 1 - stats.chi2.cdf(lr, x.shape[1]) < 0.001 else round(float(1 - stats.chi2.cdf(lr, x.shape[1])), 4),
        "mcfadden": round(float(po.prsquared), 3),
        "cox_snell": round(float(cox), 3),
        "nagelkerke": round(float(nagel), 3),
    }, "q4_logistic", "model_fit.json")

    chi2, df_par, p_par = parallel_test(y, x, po)
    pp.save_json({"po_2LL": round(float(-2 * po.llf), 3),
                  "chi2": round(float(chi2), 3), "df": df_par, "p": round(float(p_par), 3)},
                 "q4_logistic", "parallel_test.json")

    vif = pd.DataFrame({"变量": list(x.columns),
                        "VIF": [round(variance_inflation_factor(x.to_numpy(), i), 3) for i in range(x.shape[1])]})
    pp.save_csv(vif, "q4_logistic", "vif.csv")

    print("q4 results saved to outputs/results/q4_logistic/")


if __name__ == "__main__":
    main()
