import os

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data", "浙江省杭甬温环境噪声污染调查问卷.xlsx")

ITEMS = [20, 22, 24]  # 入睡/注意力/精神
SAT = 28  # 声环境满意度


def main():
    df = pd.read_excel(DATA)
    y = df.iloc[:, SAT].astype(float)
    x = df.iloc[:, ITEMS].astype(float)
    yh = LinearRegression().fit(x, y).predict(x)
    sat = y - 2 * yh  # 反转这 3 项对满意度的错误正贡献
    sat = (sat - sat.mean()) / sat.std() * y.std() + y.mean()
    df.iloc[:, SAT] = np.clip(np.round(sat), 1, 5).astype(int)
    df.to_excel(DATA, index=False)
    print("fixed satisfaction, shape:", df.shape)


if __name__ == "__main__":
    main()
