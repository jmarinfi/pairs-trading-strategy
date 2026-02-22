import time
from datetime import datetime, timedelta

import ccxt
import pandas as pd


exchange = ccxt.bitget()
markets = exchange.load_markets()


def to_dataframe(candles: list[list[float]]) -> pd.DataFrame:
    df = pd.DataFrame(
        candles, columns=["datetime", "open", "high", "low", "close", "volume"]
    )
    df["datetime"] = pd.to_datetime(df["datetime"], unit="ms")
    df = df.set_index("datetime").sort_index()

    return df


def fetch_ohlcv_range(
    symbol: str, timeframe: str, start_ts_ms: int, end_ts_ms: int
) -> pd.DataFrame:
    all_candles: list[list[float]] = []
    current_since = start_ts_ms
    limit = 100

    while current_since < end_ts_ms:
        candles = exchange.fetch_ohlcv(
            symbol=symbol, timeframe=timeframe, since=current_since, limit=limit
        )
        if not candles:
            break

        all_candles.extend(candles)

        last_ts = candles[-1][0]
        if last_ts >= end_ts_ms:
            break

        current_since = last_ts + 1

        time.sleep(1)

    return to_dataframe(all_candles)


def from_dt_to_ts_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


# pairs = [
#     "BTC/USDT:USDT",
#     "ETH/USDT:USDT",
#     "XRP/USDT:USDT",
#     "SOL/USDT:USDT",
#     "AZTEC/USDT:USDT",
#     "PEPE/USDT:USDT",
#     "ENSO/USDT:USDT",
#     "DOGE/USDT:USDT",
#     "MYX/USDT:USDT",
#     "HYPE/USDT:USDT",
#     "INJ/USDT:USDT",
#     "SUI/USDT:USDT",
#     "BIO/USDT:USDT",
#     "ADA/USDT:USDT",
#     "BCH/USDT:USDT",
#     "LINK/USDT:USDT",
#     "AAVE/USDT:USDT",
#     "TAO/USDT:USDT",
#     "ETC/USDT:USDT",
#     "BNB/USDT:USDT",
#     "ZEC/USDT:USDT",
#     "OP/USDT:USDT",
#     "NEAR/USDT:USDT",
#     "ARB/USDT:USDT",
#     "ASTER/USDT:USDT",
#     "UNI/USDT:USDT",
#     "SNX/USDT:USDT",
#     "SHIB/USDT:USDT",
#     "AVAX/USDT:USDT",
#     "LTC/USDT:USDT",
#     "HBAR/USDT:USDT",
#     "PENGU/USDT:USDT",
#     "FARTCOIN/USDT:USDT",
#     "PI/USDT:USDT",
#     "GALA/USDT:USDT",
#     "PUMP/USDT:USDT",
#     "APT/USDT:USDT",
# ]


# df_close = pd.DataFrame()
# end_dt = datetime.now()
# start_dt = end_dt - timedelta(days=30)

# for pair in pairs:
#     df = fetch_ohlcv_range(
#         symbol=pair,
#         timeframe="15m",
#         start_ts_ms=from_dt_to_ts_ms(start_dt),
#         end_ts_ms=from_dt_to_ts_ms(end_dt),
#     )
#     df_close[pair] = df["close"]

# print(df_close.head())
# df_close.to_csv("ccxt_data_all_pairs_15m.csv", index=True)
