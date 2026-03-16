import yfinance as yf
import os
import pandas as pd
from feature_engineer import add_technical_indicators

def export_data(symbol="RELIANCE.NS", start_date="2019-01-01"):
    """
    Fetches data from yfinance, applies the same technical indicators 
    used for training, and saves it to a CSV file.
    """
    print(f"Fetching data for {symbol} starting from {start_date}...")
    
    # 1. Download raw data
    df = yf.download(symbol, start=start_date)
    
    if df.empty:
        print(f"Error: No data found for {symbol}")
        return

    # 2. Add the 20 technical indicators used in training
    print("Applying technical indicators (20 features)...")
    df_enriched = add_technical_indicators(df)
    
    # 3. Define the features we use in training
    features = [
        'Open', 'High', 'Low', 'Close', 'Volume',
        'sma20', 'sma50', 'ema20', 'ema50', 'ema200',
        'rsi', 'macd', 'roc', 'stoch_k',
        'atr', 'bb_upper', 'bb_lower',
        'obv', 'vwap', 'volume_change'
    ]
    
    # Check if all features exist
    available_features = [f for f in features if f in df_enriched.columns]
    
    # 4. Save to CSV
    output_file = f"{symbol.replace('.', '_')}_training_data.csv"
    df_enriched[available_features].to_csv(output_file)
    
    print(f"Success! Data exported to: {os.path.abspath(output_file)}")
    print(f"Total rows: {len(df_enriched)}")
    print(f"Total features: {len(available_features)}")
    print("\nFeature list exported:")
    for f in available_features:
        print(f" - {f}")

if __name__ == "__main__":
    import sys
    stock_symbol = "RELIANCE.NS"
    if len(sys.argv) > 1:
        stock_symbol = sys.argv[1]
    
    export_data(stock_symbol)
