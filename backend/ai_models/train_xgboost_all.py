import os
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib

# Use absolute import to be safe if running as script
import sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from ai_models.feature_engineer import add_technical_indicators

DATA_FOLDER = os.path.join(BASE_DIR, "data", "nifty50")
MODEL_FOLDER = os.path.join(BASE_DIR, "ai_models", "training_db")

os.makedirs(MODEL_FOLDER, exist_ok=True)

FEATURES = [
    'Open', 'High', 'Low', 'Close', 'Volume',
    'sma20', 'sma50', 'ema20', 'ema50', 'ema200',
    'rsi', 'macd', 'roc', 'stoch_k',
    'atr', 'bb_upper', 'bb_lower',
    'obv', 'vwap', 'volume_change'
]

TARGET = "Close"


def train_stock(csv_path):

    ticker = os.path.basename(csv_path).replace(".csv", "")

    print(f"Training XGBoost for {ticker}...")

    df = pd.read_csv(csv_path)

    # Standardize column names if they are lowercase from CSV
    df_enriched = add_technical_indicators(df)

    # Prepare features
    X = df_enriched[FEATURES].values
    y = df_enriched[TARGET].values

    model = xgb.XGBRegressor(
        n_estimators=400,
        learning_rate=0.03,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror"
    )

    model.fit(X, y)

    model_path = os.path.join(
        MODEL_FOLDER,
        f"xgboost_{ticker}.pkl"
    )

    joblib.dump(model, model_path)

    print(f"Saved model → {model_path}")


def train_all():

    if not os.path.exists(DATA_FOLDER):
        print(f"Error: Data folder {DATA_FOLDER} not found.")
        return

    csv_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]
    total = len(csv_files)
    
    print(f"Found {total} CSV files in {DATA_FOLDER}. Starting training...")
    
    success_count = 0
    for i, file in enumerate(csv_files):
        try:
            csv_path = os.path.join(DATA_FOLDER, file)
            print(f"[{i+1}/{total}] ", end="")
            train_stock(csv_path)
            success_count += 1
        except Exception as e:
            print(f"Error training {file}: {e}")

    print("\n" + "="*30)
    print(f"XGBoost Training Complete!")
    print(f"Successfully trained: {success_count} / {total}")
    print("="*30)


if __name__ == "__main__":

    train_all()