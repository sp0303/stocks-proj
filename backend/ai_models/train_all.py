import sys
import os
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

# Add the parent directory to sys.path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nifty50 import NIFTY50
from ai_models.train_model import train

def train_full_suite(force=False, workers=4):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    train_db = os.path.join(base_dir, "training_db")

    # 1. Train the Index Model first (Baseline)
    index_symbol = "^NSEI"
    clean_index = index_symbol.replace("^", "INDEX_")
    index_path = os.path.join(train_db, f"{clean_index}_model.keras")

    if force or not os.path.exists(index_path):
        print(f"--- STARTING SEQUENTIAL INDEX TRAINING: {index_symbol} ---")
        train(index_symbol)
    else:
        print(f"--- INDEX MODEL {clean_index} ALREADY EXISTS, SKIPPING ---")
    
    # 2. Train NIFTY 50 Stocks Concurrently
    print(f"\n--- STARTING CONCURRENT NIFTY 50 TRAINING ({workers} workers) ---")
    
    stocks_to_train = []
    for stock in NIFTY50:
        symbol = f"{stock}.NS"
        model_path = os.path.join(train_db, f"{symbol}_model.keras")

        if not force and os.path.exists(model_path):
            print(f"[{stock}] already exists, skipping...")
            continue
        stocks_to_train.append(symbol)

    if not stocks_to_train:
        print("All stock models up to date.")
        return

    # Execute in parallel
    with ProcessPoolExecutor(max_workers=workers) as executor:
        future_to_stock = {executor.submit(train, symbol): symbol for symbol in stocks_to_train}
        
        for future in as_completed(future_to_stock):
            stock = future_to_stock[future]
            try:
                future.result()
                print(f"✔ Successfully trained {stock}")
            except Exception as e:
                print(f"✘ Error training {stock}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Overwrite existing models")
    parser.add_argument("--workers", type=int, default=4, help="Number of concurrent training processes")
    args = parser.parse_args()
    
    train_full_suite(force=args.force, workers=args.workers)
