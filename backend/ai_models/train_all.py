import sys
import os

# Add the parent directory to sys.path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nifty50 import NIFTY50
from ai_models.train_model import train

def train_full_suite():
    # 1. Train the Index Model first (Deep Baseline)
    print("--- STARTING INDEX TRAINING (BASELINE) ---")
    train("^NSEI")
    
    # 2. Train NIFTY 50 Stocks
    print("\n--- STARTING NIFTY 50 BATCH TRAINING ---")
    for stock in NIFTY50:
        try:
            train(f"{stock}.NS")
        except Exception as e:
            print(f"Error training {stock}: {e}")

if __name__ == "__main__":
    train_full_suite()
