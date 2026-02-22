from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

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

    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    ax.set_title("Cointegration Test p-value Matrix")
    fig.tight_layout()

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


def visualize_backtest(
    df_backtest: pd.DataFrame,
) -> tuple["Figure", tuple["Axes", "Axes"]]:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # Gráfico de Equity
    ax1.plot(
        df_backtest.index,
        df_backtest["equity"],
        label="Strategy Equity",
        color="purple",
    )
    ax1.set_title("Strategy Equity Curve")
    ax1.set_ylabel("Cumulative Equity")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper left")

    # Gráfico de Precios (S1 y S2 en el mismo subplot pero ejes Y separados)
    color1 = "blue"
    ax2.plot(df_backtest.index, df_backtest["S1"], label="S1 Price", color=color1)
    ax2.set_ylabel("S1 Price", color=color1)
    ax2.tick_params(axis="y", labelcolor=color1)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="upper left")

    # Eje gemelo para S2
    ax3 = ax2.twinx()
    color2 = "orange"
    ax3.plot(
        df_backtest.index, df_backtest["S2"], label="S2 Price", color=color2, alpha=0.8
    )
    ax3.set_ylabel("S2 Price", color=color2)
    ax3.tick_params(axis="y", labelcolor=color2)
    ax3.legend(loc="upper right")

    ax2.set_title("Pair Prices (S1 and S2)")
    ax2.set_xlabel("Date")

    fig.tight_layout()

    return fig, (ax1, ax2)
