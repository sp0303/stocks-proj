import yfinance as yf
import os
import pandas as pd
from feature_engineer import add_technical_indicators

def generate_nifty():
    symbol = "^NSEI"
    start_date = "2019-01-01"
    
    # Path setup
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data", "nifty50")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    output_file = os.path.join(data_dir, "INDEX_NSEI.csv")
    
    print(f"Fetching data for {symbol}...")
    df = yf.download(symbol, start=start_date)
    
    if df.empty:
        print(f"Error: No data found for {symbol}. Make sure yfinance can access ^NSEI")
        return

    print(f"Data fetched: {len(df)} rows. Applying technical indicators...")
    df_enriched = add_technical_indicators(df)
    
    features = [
        'Open', 'High', 'Low', 'Close', 'Volume',
        'sma20', 'sma50', 'ema20', 'ema50', 'ema200',
        'rsi', 'macd', 'roc', 'stoch_k',
        'atr', 'bb_upper', 'bb_lower',
        'obv', 'vwap', 'volume_change'
    ]
    
    # Standardize columns
    available_features = [f for f in features if f in df_enriched.columns]
    
    print(f"Saving {len(available_features)} features to {output_file}...")
    df_enriched[available_features].to_csv(output_file)
    print("Success!")

if __name__ == "__main__":
    generate_nifty()
