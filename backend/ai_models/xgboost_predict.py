import os
import joblib
import numpy as np
import pandas as pd
import yfinance as yf

# Use absolute import logic
import sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from ai_models.feature_engineer import add_technical_indicators

MODEL_FOLDER = os.path.join(BASE_DIR, "ai_models", "training_db")

FEATURES = [
    'Open', 'High', 'Low', 'Close', 'Volume',
    'sma20', 'sma50', 'ema20', 'ema50', 'ema200',
    'rsi', 'macd', 'roc', 'stoch_k',
    'atr', 'bb_upper', 'bb_lower',
    'obv', 'vwap', 'volume_change'
]

def load_model(ticker):
    # Standardize symbol for lookup
    if not ticker.endswith(".NS") and "^" not in ticker:
        ticker = ticker + ".NS"
    
    clean_ticker = ticker.replace(".", "_").replace("^", "INDEX_")
    path = os.path.join(MODEL_FOLDER, f"xgboost_{clean_ticker}.pkl")
    
    if not os.path.exists(path):
        # Fallback to Index if specific model doesn't exist
        print(f"[XGBoost] Model for {ticker} not found. Falling back to Index.")
        path = os.path.join(MODEL_FOLDER, "xgboost_INDEX_NSEI.pkl")
        
    if not os.path.exists(path):
        return None
        
    return joblib.load(path)

def predict(symbol):
    """
    Fetches data, prepares features, and makes prediction with XGBoost.
    """
    if not symbol.endswith(".NS") and "^" not in symbol:
        symbol = symbol + ".NS"
        
    try:
        # Fetch from 2019 baseline (same as other models)
        df = yf.download(symbol, start="2019-01-01", progress=False)
        if df.empty:
            return {"error": "No data found"}

        # Enrich features
        df_enriched = add_technical_indicators(df)
        
        model = load_model(symbol)
        if model is None:
            return {"error": "Model not found"}

        # Predict using last row
        X = df_enriched[FEATURES].values
        pred = model.predict(X[-1].reshape(1, -1))
        
        predicted_price = float(pred[0])
        current_price = float(df_enriched['Close'].iloc[-1])
        change = ((predicted_price - current_price) / current_price) * 100

        # Simple threshold logic for signal
        if change > 1.5:
            signal = "BUY"
        elif change < -1.5:
            signal = "SELL"
        else:
            signal = "HOLD"

        return {
            "model": "XGBoost",
            "current_price": current_price,
            "predicted_price": predicted_price,
            "expected_move": change,
            "signal": signal
        }

    except Exception as e:
        return {"error": str(e)}