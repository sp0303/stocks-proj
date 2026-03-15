import sys
import os
import argparse
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

# 1. Immediate Path Injection (Required for Windows Sub-processes)
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_PATH not in sys.path:
    sys.path.append(BASE_PATH)

from nifty50 import NIFTY50
from ai_models.train_transformer import train

def train_transformer_full_suite(force=False, workers=4):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    train_db = os.path.join(base_dir, "training_db")
    
    # Define priority tasks (Index first)
    index_symbol = "^NSEI"
    
    # 2. Collect all tasks
    stocks_to_train = []
    
    # Add Index to front of queue
    index_model_path = os.path.join(train_db, "INDEX_NSEI_transformer.pt")
    if force or not os.path.exists(index_model_path):
        stocks_to_train.append(index_symbol)
    
    # Add NIFTY 50
    for stock in NIFTY50:
        symbol = f"{stock}.NS"
        model_path = os.path.join(train_db, f"{symbol}_transformer.pt")
        
        if force or not os.path.exists(model_path):
            stocks_to_train.append(symbol)

    if not stocks_to_train:
        print("✔ All models are up to date.")
        return

    # 3. Handle Sequential vs Concurrent
    if workers <= 1:
        print(f"--- STARTING SEQUENTIAL BATCH TRAINING ({len(stocks_to_train)} stocks) ---")
        for i, symbol in enumerate(stocks_to_train):
            print(f"[{i+1}/{len(stocks_to_train)}] Processing {symbol}...")
            try:
                train(symbol)
            except Exception as e:
                print(f"FAILED {symbol}: {e}")
        return

    # 4. Concurrent execution
    print(f"\n--- STARTING CONCURRENT BATCH TRAINING ({len(stocks_to_train)} stocks, {workers} workers) ---")
    print("Pre-loading libraries and starting workers...")

    total = len(stocks_to_train)
    completed = 0
    
    # Use ProcessPoolExecutor with explicit workers
    with ProcessPoolExecutor(max_workers=workers) as executor:
        future_to_stock = {}
        
        # Submit Index first for head-start
        for symbol in stocks_to_train:
            future = executor.submit(train, symbol)
            future_to_stock[future] = symbol
            # Very small stagger to prevent disk/cpu race during python startup
            time.sleep(0.3)
        
        print(f"Tasks submitted. Monitoring progress...")
        
        for future in as_completed(future_to_stock):
            stock = future_to_stock[future]
            completed += 1
            try:
                future.result()
                print(f"[{completed}/{total}] ✔ Done: {stock}")
            except Exception as e:
                print(f"[{completed}/{total}] ✘ Error in {stock}: {e}")

if __name__ == "__main__":
    # Windows-specific entry point protection
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Overwrite existing models")
    parser.add_argument("--workers", type=int, default=1, help="Number of concurrent processes (default 1 = sequential)")
    args = parser.parse_args()
    
    train_transformer_full_suite(force=args.force, workers=args.workers)
