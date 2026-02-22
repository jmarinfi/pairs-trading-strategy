from dataclasses import dataclass

import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import coint


@dataclass
class CointegrationTestResult:
    df: pd.DataFrame
    score_matrix: np.ndarray
    pvalue_matrix: np.ndarray
    pairs: list[tuple[str, str]]


@dataclass
class BestPair:
    name1: str
    name2: str
    series1: pd.Series
    series2: pd.Series
    spread: pd.Series
    zscore: pd.Series


def cointegration_test(df: pd.DataFrame) -> CointegrationTestResult:
    tickers = df.columns
    n = len(tickers)
    score_matrix = np.zeros((n, n))
    pvalue_matrix = np.ones((n, n))
    pairs = []

    for i in range(n):
        for j in range(i + 1, n):
            score, pvalue, _ = coint(df.iloc[:, i], df.iloc[:, j])
            score_matrix[i, j] = score
            pvalue_matrix[i, j] = pvalue
            if pvalue < 0.05:
                pairs.append((tickers[i], tickers[j]))

    return CointegrationTestResult(df, score_matrix, pvalue_matrix, pairs)


def find_best_pair(
    cointegration_test_result: CointegrationTestResult, window: int
) -> BestPair:
    mask = np.triu(
        np.ones_like(cointegration_test_result.pvalue_matrix, dtype=bool), k=1
    )
    upper_vals = cointegration_test_result.pvalue_matrix[mask]

    min_idx_flat = np.argmin(upper_vals)
    idx_pairs = np.column_stack(np.where(mask))
    i, j = idx_pairs[min_idx_flat]

    S1, S2 = (
        cointegration_test_result.df.iloc[:, i],
        cointegration_test_result.df.iloc[:, j],
    )
    spread: pd.Series = S1 - S2
    zscore = (spread - spread.rolling(window).mean()) / spread.rolling(window).std()
    zscore = zscore.dropna()

    return BestPair(
        name1=str(S1.name),
        name2=str(S2.name),
        series1=S1,
        series2=S2,
        spread=spread,
        zscore=zscore,
    )
