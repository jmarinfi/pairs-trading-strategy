from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

if TYPE_CHECKING:
    from cointegration import CointegrationTestResult, BestPair
    from matplotlib.pyplot import Figure, Axes


def cointegration_heatmap(
    cointegration_test_result: CointegrationTestResult,
    filter_min_pvalue: float | None = None,
) -> tuple[Figure, Axes]:
    tickers = cointegration_test_result.df.columns

    mask = None
    if filter_min_pvalue is not None:
        mask = np.tril(
            np.ones_like(cointegration_test_result.pvalue_matrix, dtype=bool)
        ) | (cointegration_test_result.pvalue_matrix >= filter_min_pvalue)

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        cointegration_test_result.pvalue_matrix,
        mask=mask,
        xticklabels=tickers,
        yticklabels=tickers,
        cmap="RdYlGn_r",
        annot=True,
        fmt=".2f",
        ax=ax,
    )

    ax.set_title("Cointegration Test p-value Matrix: Maskless")

    return fig, ax


def spread_and_zscore(best_pair: BestPair, multiplier_std: int) -> tuple[Figure, Axes]:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    ax1.plot(best_pair.spread.index, best_pair.spread.values, label="Spread")
    ax1.axhline(best_pair.spread.mean(), color="black", linestyle="--", lw=1)
    ax1.axhline(
        best_pair.spread.mean() + multiplier_std * best_pair.spread.std(),
        color="red",
        linestyle="--",
        lw=1,
    )
    ax1.axhline(
        best_pair.spread.mean() - multiplier_std * best_pair.spread.std(),
        color="green",
        linestyle="--",
        lw=1,
    )
    ax1.legend()

    ax2.plot(best_pair.zscore.index, best_pair.zscore.values, label="Z-score")
    ax2.axhline(0, color="black", linestyle="--", lw=1)
    ax2.axhline(multiplier_std, color="red", linestyle="--", lw=1)
    ax2.axhline(-multiplier_std, color="green", linestyle="--", lw=1)
    ax2.legend()

    plt.xlabel("Date")
    plt.suptitle(f"Spread and Z-score for {best_pair.name1} and {best_pair.name2}")
    plt.tight_layout()

    return fig, (ax1, ax2)
