import yfinance as yf
import pandas as pd


tickers = ["NEE", "FSLR", "ENPH", "PLUG", "BEP", "AQN", "PBW", "FAN", "ICLN"]
start_date = "2015-01-01"
end_date = "2025-01-01"

df: pd.DataFrame = yf.download(tickers, start=start_date, end=end_date).Close.dropna()
