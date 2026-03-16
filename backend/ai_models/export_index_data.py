import os
import yfinance as yf
import pandas as pd
from feature_engineer import add_technical_indicators

# Define the list of Nifty 50 stocks (Hardcoded for independence, but usually imported)
try:
    from nifty50 import NIFTY50
except ImportError:
    # Fallback if imported from a different context
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from nifty50 import NIFTY50

def export_index_data(index_name="nifty50", symbols=NIFTY50, start_date="2019-01-01"):
    """
    Exports training data for an entire list of symbols into a structured directory.
    """
    # 1. Setup Directories
    base_dir = os.path.dirname(os.path.dirname(__file__)) # Go to /backend
    data_dir = os.path.join(base_dir, "data", index_name)
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")

    print(f"Starting batch export for {len(symbols)} stocks in {index_name}...")
    
    features = [
        'Open', 'High', 'Low', 'Close', 'Volume',
        'sma20', 'sma50', 'ema20', 'ema50', 'ema200',
        'rsi', 'macd', 'roc', 'stoch_k',
        'atr', 'bb_upper', 'bb_lower',
        'obv', 'vwap', 'volume_change'
    ]

    success_count = 0
    fail_count = 0

    for symbol in symbols:
        # Standardize for yfinance
        yf_symbol = symbol if symbol.endswith(".NS") or "^" in symbol else f"{symbol}.NS"
        
        try:
            print(f"[{success_count + fail_count + 1}/{len(symbols)}] Processing {yf_symbol}...")
            
            # Download
            df = yf.download(yf_symbol, start=start_date, progress=False)
            
            if df.empty:
                print(f"  - Error: No data found for {yf_symbol}")
                fail_count += 1
                continue
            
            # Enrich
            df_enriched = add_technical_indicators(df)
            
            # Filter features
            available_features = [f for f in features if f in df_enriched.columns]
            
            # Save
            filename = f"{yf_symbol.replace('.', '_')}.csv"
            output_path = os.path.join(data_dir, filename)
            df_enriched[available_features].to_csv(output_path)
            
            success_count += 1
            
        except Exception as e:
            print(f"  - Error processing {yf_symbol}: {e}")
            fail_count += 1

    print("\n" + "="*30)
    print(f"Batch Export Complete!")
    print(f"Index: {index_name}")
    print(f"Directory: {os.path.abspath(data_dir)}")
    print(f"Successfully exported: {success_count}")
    print(f"Failed: {fail_count}")
    print("="*30)

if __name__ == "__main__":
    export_index_data()
