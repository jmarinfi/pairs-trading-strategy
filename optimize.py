from typing import Any

import optuna
from optuna import Trial
import pandas as pd

from backtest import backtest, performance_metrics
from cointegration import find_best_pair, CointegrationTestResult


def run_optimization(cointegration_test_result: CointegrationTestResult):
    def objective(trial: Trial):
        window = trial.suggest_int("window", 10, 100)
        zscore_mult = trial.suggest_float("zscore_mult", 1.0, 3.5)

        best_pair = find_best_pair(cointegration_test_result, window=window)

        df_backtest = backtest(best_pair, zscore_mult=zscore_mult)

        metrics = performance_metrics(df_backtest)
        sharpe: Any = metrics.loc["Sharpe Ratio", "Strategy"]

        if pd.isna(sharpe) or sharpe == float("inf") or sharpe == 0.0:
            return -999.0

        return float(sharpe)

    print("Iniciando optimización de hiperparámetros con Optuna...")

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=200)

    print("\n¡Optimización completada!")
    print(f"Mejor Sharpe Ratio: {study.best_value:.4f}")
    print(
        f"Mejores parámetros:\n - Window: {study.best_params['window']}\n - Z-Score Mult: {study.best_params['zscore_mult']}"
    )

    return study.best_params
