import matplotlib.pyplot as plt

from data.data import df
from cointegration import cointegration_test, find_best_pair
from visualization import cointegration_heatmap, spread_and_zscore


def medium_example():
    print("Running cointegration test...")
    print(f"Data:\n{df.head()}")

    result = cointegration_test(df)
    print(f"Pairs found:\n{result.pairs}")
    print(f"Score matrix:\n{result.score_matrix}")
    print(f"P values:\n{result.pvalue_matrix}")

    best_pair = find_best_pair(result, window=21)
    print(f"Best pair:\n{best_pair}")

    fig, ax = cointegration_heatmap(result, filter_min_pvalue=0.05)
    plt.savefig("cointegration_heatmap.png")

    fig, axes = spread_and_zscore(best_pair, multiplier_std=2)
    plt.savefig("spread_and_zscore.png")


def main():
    medium_example()


if __name__ == "__main__":
    main()
