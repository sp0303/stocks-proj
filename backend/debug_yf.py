import yfinance as yf
import pandas as pd

symbol = "RELIANCE.NS"
print(f"Testing download for {symbol}...")
df = yf.download(symbol, start="2019-01-01")

print("\n--- Columns ---")
print(df.columns)
print("\n--- Head ---")
print(df.head())
print("\n--- Index ---")
print(df.index.name)
