from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd

from data.data import df
from data.ccxt_data import fetch_ohlcv_range, from_dt_to_ts_ms
from cointegration import cointegration_test, find_best_pair
from visualization import cointegration_heatmap, spread_and_zscore, visualize_backtest
from backtest import backtest, performance_metrics
from optimize import run_optimization
from strategy_utils import esperar_al_siguiente_cuarto, send_webhook


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


def bitget_example():
    df_pairs = pd.read_csv("ccxt_data_all_pairs_15m.csv")
    df_pairs = df_pairs.set_index("datetime").dropna(axis=1, how="any")
    df_pairs = df_pairs[["TAO/USDT:USDT", "SHIB/USDT:USDT"]].copy()
    print(df_pairs.head())

    result = cointegration_test(df_pairs)
    print(f"Pairs found:\n{result.pairs}")
    print(f"Score matrix:\n{result.score_matrix}")
    print(f"P values:\n{result.pvalue_matrix}")

    tickers = list(result.df.columns)

    pairs_with_pvalue = [
        (t1, t2, result.pvalue_matrix[tickers.index(t1), tickers.index(t2)])
        for t1, t2 in result.pairs
    ]
    sorted_pairs = sorted(pairs_with_pvalue, key=lambda x: x[2])
    print("\nPares ordenados por p-valor (de menor a mayor):")
    for t1, t2, pvalue in sorted_pairs:
        print(f"{t1} - {t2}: {pvalue:.6f}")

    best_params = run_optimization(result)

    best_pair = find_best_pair(result, window=best_params["window"])
    print(f"Best pair:\n{best_pair}")

    fig, ax = cointegration_heatmap(result, filter_min_pvalue=0.05)
    plt.savefig("cointegration_heatmap_bitget.png")

    fig, axes = spread_and_zscore(best_pair, multiplier_std=best_params["zscore_mult"])
    plt.savefig("spread_and_zscore_bitget.png")

    df_backtest = backtest(best_pair, zscore_mult=best_params["zscore_mult"])
    print(df_backtest.head())
    df_backtest.to_csv("backtest_bitget.csv")

    metrics = performance_metrics(df_backtest)
    print(f"Performance metrics:\n{metrics}")
    metrics.to_csv("metrics_bitget.csv")

    fig, axes = visualize_backtest(df_backtest)
    plt.savefig("backtest_equity_bitget.png")


def live_strategy():
    timeframe = 15
    url_bot = "http://192.168.1.132:7503/trade_signal"
    uuid_long = "06bda1d7-8de2-4574-97c9-959cae3d9798"
    uuid_short = "9636adbf-d835-4abb-8bfc-a3be20bd31e6"

    pair_1 = {
        "S1": "DOGE/USDT:USDT",
        "S2": "ADA/USDT:USDT",
        "S1_gainium": "DOGE_USDT",
        "S2_gainium": "ADA_USDT",
        "window": 36,
        "zscore": 1.61,
        "S1_has_position_long": False,
        "S1_has_position_short": False,
        "S2_has_position_long": False,
        "S2_has_position_short": False,
    }
    pair_2 = {
        "S1": "BTC/USDT:USDT",
        "S2": "SOL/USDT:USDT",
        "S1_gainium": "BTC_USDT",
        "S2_gainium": "SOL_USDT",
        "window": 15,
        "zscore": 2.6,
        "S1_has_position_long": False,
        "S1_has_position_short": False,
        "S2_has_position_long": False,
        "S2_has_position_short": False,
    }
    pair_3 = {
        "S1": "TAO/USDT:USDT",
        "S2": "SHIB/USDT:USDT",
        "S1_gainium": "TAO_USDT",
        "S2_gainium": "SHIB_USDT",
        "window": 28,
        "zscore": 3.49,
        "S1_has_position_long": False,
        "S1_has_position_short": False,
        "S2_has_position_long": False,
        "S2_has_position_short": False,
    }
    pairs = [pair_1, pair_2, pair_3]

    while True:
        esperar_al_siguiente_cuarto()

        print("\n==================================================")
        print(
            f"⏰ Ronda de revisión iniciada a las: {datetime.now().strftime('%H:%M:%S')}"
        )
        print("==================================================")

        for pair in pairs:
            print(f"\n🔍 Analizando par: {pair['S1']} vs {pair['S2']}")
            print("   Descargando datos OHLCV...")
            data_from = datetime.now() - timedelta(
                minutes=timeframe * (pair["window"] + 2)
            )
            data_to = datetime.now()

            print("   Descargando datos OHLCV...")
            df_s1 = fetch_ohlcv_range(
                symbol=pair["S1"],
                timeframe=f"{timeframe}m",
                start_ts_ms=from_dt_to_ts_ms(data_from),
                end_ts_ms=from_dt_to_ts_ms(data_to),
            )
            df_s2 = fetch_ohlcv_range(
                symbol=pair["S2"],
                timeframe=f"{timeframe}m",
                start_ts_ms=from_dt_to_ts_ms(data_from),
                end_ts_ms=from_dt_to_ts_ms(data_to),
            )

            # Alineamos ambos pares por fecha usando inner join para evitar datos faltantes
            df_combined = pd.concat(
                [df_s1["close"], df_s2["close"]], axis=1, join="inner"
            )
            df_combined.columns = ["S1", "S2"]

            # Tomamos exactamente las últimas n velas correspondientes a la ventana
            window = pair["window"]
            df_window = df_combined.iloc[-window:]

            # Calculamos la serie completa del spread para esta ventana
            spread_series = df_window["S1"] - df_window["S2"]

            # El valor actual del spread será el último de la serie
            current_spread = spread_series.iloc[-1]

            # Z-score del instante actual
            zscore = (current_spread - spread_series.mean()) / spread_series.std()

            print(f"   👉 Z-Score actual: {zscore:.3f} (Umbral: ±{pair['zscore']})")
            print(
                f"   📊 Posiciones activas -> S1 Long: {pair['S1_has_position_long']} | S1 Short: {pair['S1_has_position_short']}"
            )

            action_taken = False

            if pair["S1_has_position_long"] and zscore >= 0:
                print(
                    "   🔴 Z-Score cruzó 0 hacia arriba. CERRANDO posiciones LONG de S1 y SHORT de S2."
                )
                action_taken = True
                send_webhook(
                    url=url_bot,
                    action="closeDeal",
                    uuid=uuid_long,
                    symbol=pair["S1_gainium"],
                )
                pair["S1_has_position_long"] = False
                send_webhook(
                    url=url_bot,
                    action="closeDeal",
                    uuid=uuid_short,
                    symbol=pair["S2_gainium"],
                )
                pair["S2_has_position_short"] = False
            elif pair["S1_has_position_short"] and zscore <= 0:
                print(
                    "   🟢 Z-Score cruzó 0 hacia abajo. CERRANDO posiciones SHORT de S1 y LONG de S2."
                )
                action_taken = True
                send_webhook(
                    url=url_bot,
                    action="closeDeal",
                    uuid=uuid_short,
                    symbol=pair["S1_gainium"],
                )
                pair["S1_has_position_short"] = False
                send_webhook(
                    url=url_bot,
                    action="closeDeal",
                    uuid=uuid_long,
                    symbol=pair["S2_gainium"],
                )
                pair["S2_has_position_long"] = False

            if (
                zscore > pair["zscore"]
                and not pair["S1_has_position_short"]
                and not pair["S2_has_position_long"]
            ):
                print(
                    f"   🚀 SEÑAL ENTRADA: Sell {pair['S1']} y Buy {pair['S2']} (Z-Score > {pair['zscore']})"
                )
                action_taken = True
                send_webhook(
                    url=url_bot,
                    action="startDeal",
                    uuid=uuid_short,
                    symbol=pair["S1_gainium"],
                )
                pair["S1_has_position_short"] = True
                send_webhook(
                    url=url_bot,
                    action="startDeal",
                    uuid=uuid_long,
                    symbol=pair["S2_gainium"],
                )
                pair["S2_has_position_long"] = True
            elif (
                zscore < -pair["zscore"]
                and not pair["S1_has_position_long"]
                and not pair["S2_has_position_short"]
            ):
                print(
                    f"   🚀 SEÑAL ENTRADA: Buy {pair['S1']} y Sell {pair['S2']} (Z-Score < -{pair['zscore']})"
                )
                action_taken = True
                send_webhook(
                    url=url_bot,
                    action="startDeal",
                    uuid=uuid_long,
                    symbol=pair["S1_gainium"],
                )
                pair["S1_has_position_long"] = True
                send_webhook(
                    url=url_bot,
                    action="startDeal",
                    uuid=uuid_short,
                    symbol=pair["S2_gainium"],
                )
                pair["S2_has_position_short"] = True

            if not action_taken:
                print("   💤 Sin cambios en las posiciones operativas.")


def main():
    live_strategy()


if __name__ == "__main__":
    main()
