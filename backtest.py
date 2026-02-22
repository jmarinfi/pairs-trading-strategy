import numpy as np
import pandas as pd
from cointegration import BestPair


def backtest(best_pair: BestPair, zscore_mult: float) -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "S1": best_pair.series1,
            "S2": best_pair.series2,
            "spread": best_pair.spread,
            "zscore": best_pair.zscore,
        }
    ).dropna()

    pos_s1 = np.zeros(len(df))
    pos_s2 = np.zeros(len(df))
    current_pos_s1 = 0
    current_pos_s2 = 0

    zscores = df["zscore"].values

    for i in range(len(df)):
        z = zscores[i]

        # Cierre de posiciones al cruzar la media (zscore = 0)
        # Si venimos de un spread alto (S1 en corto) y el zscore baja de 0 (o lo toca)
        if current_pos_s1 == -1 and z <= 0:
            current_pos_s1 = 0
            current_pos_s2 = 0
        # Si venimos de un spread bajo (S1 en largo) y el zscore sube de 0 (o lo toca)
        elif current_pos_s1 == 1 and z >= 0:
            current_pos_s1 = 0
            current_pos_s2 = 0

        # Entradas (reversión a la media)
        if z > zscore_mult:
            # Spread (S1 - S2) es muy alto. Esperamos que baje.
            # Corto en S1, Largo en S2
            current_pos_s1 = -1
            current_pos_s2 = 1
        elif z < -zscore_mult:
            # Spread es muy bajo. Esperamos que suba.
            # Largo en S1, Corto en S2
            current_pos_s1 = 1
            current_pos_s2 = -1

        pos_s1[i] = current_pos_s1
        pos_s2[i] = current_pos_s2

    df["position_s1"] = pos_s1
    df["position_s2"] = pos_s2

    # Cálculos de retorno
    df["ret_s1"] = df["S1"].pct_change()
    df["ret_s2"] = df["S2"].pct_change()

    # Se aplica un shift de 1 porque operamos en la vela siguiente a la señal
    ret_pos_s1 = df["position_s1"].shift(1) * df["ret_s1"]
    ret_pos_s2 = df["position_s2"].shift(1) * df["ret_s2"]

    df["strategy_ret"] = ret_pos_s1 + ret_pos_s2
    df["equity"] = (1 + df["strategy_ret"].fillna(0)).cumprod()

    return df


def performance_metrics(df: pd.DataFrame) -> pd.DataFrame:
    # Frecuencia asumida: 1 minuto (basado en el timeframe de 1m usado)
    minutes_per_year = 365 * 24 * 60

    total_return = df["equity"].iloc[-1] - 1.0

    # Retorno Anualizado (CAGR)
    years = len(df) / minutes_per_year
    annualized_return = (1 + total_return) ** (1 / years) - 1.0 if years > 0 else 0.0

    # Volatilidad anualizada
    returns = df["strategy_ret"].fillna(0)
    annualized_vol = returns.std() * np.sqrt(minutes_per_year)

    # Ratio de Sharpe (Asumiendo tasa libre de riesgo = 0)
    sharpe_ratio = annualized_return / annualized_vol if annualized_vol != 0 else 0.0

    # Maximum Drawdown (Caída máxima)
    cummax = df["equity"].cummax()
    drawdown = (df["equity"] - cummax) / cummax
    max_drawdown = drawdown.min()

    metrics = {
        "Total Return (%)": total_return * 100,
        "Annualized Return (%)": annualized_return * 100,
        "Annualized Volatility (%)": annualized_vol * 100,
        "Sharpe Ratio": sharpe_ratio,
        "Max Drawdown (%)": max_drawdown * 100,
    }

    # Retornarlo como dataframe, traspuesto para mejor lectura si hay múltiples columnas luego
    return pd.DataFrame(metrics, index=["Strategy"]).T
