import os

import pandas as pd
import semopy

import preprocess as pp

MODEL = """
F1 =~ eff_sleep_onset + eff_attention + eff_mental + eff_hearing
F2 =~ eff_sleep_interrupt + eff_relationship + eff_physical + eff_emotion
F3 =~ noise_traffic + noise_construction + noise_public
F4 =~ noise_life + noise_business + noise_animal
F1 ~ F3 + F4
F2 ~ F3 + F4
satisfaction ~ F1 + F2 + F3 + F4
F1 ~~ F2
"""


def main():
    df = pp.clean(pp.load_raw())
    data = df[pp.EFA_ITEMS + ["satisfaction"]].astype(float)

    model = semopy.Model(MODEL)
    model.fit(data)
    stats = semopy.calc_stats(model)

    keys = ["chi2", "chi2 p-value", "DoF", "CFI", "TLI", "RMSEA"]
    fit = {k: round(float(stats[k].iloc[0]), 3) for k in keys}
    pp.save_json(fit, "q7_sem", "fit.json")
    pp.save_csv(model.inspect(), "q7_sem", "params.csv")

    fig_dir = os.path.join(pp.ROOT, "outputs", "figures")
    os.makedirs(fig_dir, exist_ok=True)
    semopy.semplot(model, os.path.join(fig_dir, "sem_path.png"),
                   plot_covs=True, std_ests=True)

    print("SEM fitted")
    print(fit)


if __name__ == "__main__":
    main()
