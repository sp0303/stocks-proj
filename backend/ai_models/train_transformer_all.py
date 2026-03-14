import sys
import os

# Add the parent directory to sys.path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nifty50 import NIFTY50
from ai_models.train_transformer import train

import argparse

def train_transformer_full_suite(force=False):
    # Helper to check if model exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
    train_db = os.path.join(base_dir, "training_db")
    
    # 1. Train the Index Model first (Deep Baseline)
    index_symbol = "^NSEI"
    clean_index = index_symbol.replace("^", "INDEX_")
    index_path = os.path.join(train_db, f"{clean_index}_transformer.pt")
    
    if force or not os.path.exists(index_path):
        print("--- STARTING TRANSFORMER INDEX TRAINING (BASELINE) ---")
        try:
            train(index_symbol)
        except Exception as e:
            print(f"Error training Index: {e}")
    else:
        print(f"--- INDEX MODEL {clean_index} ALREADY EXISTS, SKIPPING ---")
    
    # 2. Train NIFTY 50 Stocks
    print("\n--- STARTING TRANSFORMER NIFTY 50 BATCH TRAINING ---")
    for stock in NIFTY50:
        symbol = f"{stock}.NS"
        model_path = os.path.join(train_db, f"{symbol}_transformer.pt")
        
        if not force and os.path.exists(model_path):
            print(f"[{stock}] Model already exists, skipping...")
            continue
            
        try:
            train(symbol)
        except Exception as e:
            print(f"Error training {stock}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Overwrite existing models")
    args = parser.parse_args()
    
    train_transformer_full_suite(force=args.force)
