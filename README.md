# Pairs Trading Strategy

Un bot de trading automatizado basado en la estrategia de **Pairs Trading** (reversión a la media mediante cointegración). Este script busca activos cointegrados, calcula su spread y z-score, y ejecuta señales de compra/venta cuando el z-score supera ciertos umbrales definidos.

## Características Principales

- **Data Fetching:** Descarga automáticamente datos OHLCV desde exchanges usando `ccxt` (por defecto, configurado para Bitget).
- **Cointegration Test:** Analiza múltiples pares para encontrar aquellos con mayor grado de cointegración estadística.
- **Backtesting & Optimization:** Permite simular la estrategia en el pasado y optimizar parámetros clave como la ventana temporal (`window`) y los multiplicadores de z-score.
- **Visualización:** Genera heatmaps de cointegración y gráficos de evolución de spreads.
- **Live Trading:** Un bucle infinito (`live_strategy` en `main.py`) diseñado para operar en intervalos precisos de 15 minutos, enviando señales mediante **Webhooks** a bots de terceros (como Gainium).

## Requisitos y Configuración

El proyecto está diseñado para funcionar con Python y gestionarse con [`uv`](https://github.com/astral-sh/uv) (o pip). 

Asegúrate de tener instaladas las dependencias. Si usas `uv`:

```bash
uv add pandas numpy matplotlib statsmodels ccxt requests schedule optuna
```

## Uso

El archivo principal es `main.py`. Contiene diferentes ejemplos y la estrategia en vivo:

```bash
# Ejecutar el script principal
uv run main.py
```

Dentro de `main.py`, puedes modificar la función a ejecutar en el bloque `if __name__ == "__main__":`
- `live_strategy()`: Bucle infinito para trading en vivo con webhooks.
- `bitget_example()`: Ejecuta una descarga, test de cointegración, backtest y optimización con el mercado actual.
- `medium_example()`: Versión simplificada con datos estáticos de ejemplo.

## Estructura de Archivos

- `main.py`: Archivo principal / Entrypoint.
- `cointegration.py`: Lógica estadística para la cointegración.
- `backtest.py`: Lógica para calcular la rentabilidad de las estrategias (métricas y drawdown).
- `optimize.py`: Optimización de parámetros basado en histórico numérico.
- `visualization.py`: Utilidades gráficas generadoras de `.png`.
- `strategy_utils.py`: Herramientas auxiliares, control del tiempo para velas de 15m y el gestor de peticiones Webhook.
- `data/ccxt_data.py`: Interfaz para descargas históricas desde el exchange vía CCXT.
