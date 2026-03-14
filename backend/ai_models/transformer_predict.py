import os
import torch
import joblib
import numpy as np
import yfinance as yf
try:
    from ai_models.transformer_model import StockTransformer
except ImportError:
    from transformer_model import StockTransformer

try:
    from feature_engineer import prepare_multivariate_features, add_technical_indicators
except ImportError:
    import sys
    sys.path.append(os.path.dirname(__file__))
    from feature_engineer import prepare_multivariate_features, add_technical_indicators

LOOKBACK = 60
FEATURES = 9
BASE_DIR = os.path.dirname(__file__)
TRAIN_DB = os.path.join(BASE_DIR, "training_db")

# Cache to avoid constantly hitting disk
_transformer_cache = {}

def get_transformer_and_scaler(symbol):
    if not symbol.endswith(".NS") and "^" not in symbol:
        symbol = symbol + ".NS"
    
    clean_symbol = symbol.replace("^", "INDEX_")
    
    if clean_symbol in _transformer_cache:
        return _transformer_cache[clean_symbol]["model"], _transformer_cache[clean_symbol]["scaler"]

    model_path = os.path.join(TRAIN_DB, f"{clean_symbol}_transformer.pt")
    scaler_path = os.path.join(TRAIN_DB, f"{clean_symbol}_scaler.save")

    # Smart Fallback to Index
    if not os.path.exists(model_path):
        print(f"[Transformer] Model for {symbol} not found. Falling back to Index.")
        clean_symbol = "INDEX_NSEI"
        model_path = os.path.join(TRAIN_DB, "INDEX_NSEI_transformer.pt")
        scaler_path = os.path.join(TRAIN_DB, "INDEX_NSEI_scaler.save")

    if not os.path.exists(model_path):
         raise FileNotFoundError(f"Transformer model not found at {model_path}")

    # Initialize Architecture (Must match training params exactly)
    model = StockTransformer(feature_size=FEATURES, num_heads=3, num_layers=2)
    model.load_state_dict(torch.load(model_path))
    model.eval() # Set to inference mode (disables dropout etc)
    
    scaler = joblib.load(scaler_path)
    
    _transformer_cache[clean_symbol] = {"model": model, "scaler": scaler}
    return model, scaler

def predict(symbol):
    res = predict_detailed(symbol)
    if "error" in res:
        return res
    
    return {
        "model": "PyTorch Transformer",
        "current_price": res["current_price"],
        "predicted_price": res["predicted_price"],
        "expected_move": res["expected_move"],
        "signal": res["signal"],
        "rsi": res["history"][-1].get("rsi") if res.get("history") else None,
        "macd": res["history"][-1].get("macd") if res.get("history") else None,
        "sma20": res["history"][-1].get("sma20") if res.get("history") else None,
        "sma50": res["history"][-1].get("sma50") if res.get("history") else None
    }

def predict_detailed(symbol):
    if not symbol.endswith(".NS") and "^" not in symbol:
        symbol = symbol + ".NS"
    
    try:
        # 1. Fetch data
        df = yf.download(symbol, period="7y") # Use full period for volatility calc
        if df.empty:
            return {"error": "No price data available", "signal": "UNKNOWN"}

        df_enriched = add_technical_indicators(df)
        features_matrix = prepare_multivariate_features(df)
        
        if len(features_matrix) < LOOKBACK:
            return {"error": "Insufficient historical data", "signal": "UNKNOWN"}

        # Calculate Volatility for Signal Threshold
        # Use daily returns from the last 60 days
        recent_prices = df['Close'].tail(60).values
        daily_returns = np.diff(recent_prices) / recent_prices[:-1]
        volatility = np.std(daily_returns) * 100 # In percentage
        
        # Determine threshold (e.g., 2.0x volatility but min 1.5%)
        dynamic_threshold = max(1.5, volatility * 2.0)

        # Load specific model & scaler
        model, scaler = get_transformer_and_scaler(symbol)
        
        # Scale Data
        scaled_features = scaler.transform(features_matrix)
        
        # Get last 60 days
        last_60_scaled = scaled_features[-LOOKBACK:]
        last_60_scaled = np.reshape(last_60_scaled, (1, LOOKBACK, last_60_scaled.shape[1]))
        
        # PyTorch Inference
        x_tensor = torch.tensor(last_60_scaled, dtype=torch.float32)
        with torch.no_grad():
            pred_tensor = model(x_tensor)
            pred_val = pred_tensor.item()
            
        # Inverse transform (Close price is index 3)
        dummy = np.zeros((1, scaled_features.shape[1]))
        dummy[0, 3] = pred_val
        predicted_price = float(scaler.inverse_transform(dummy)[0, 3])
        
        # Build history array for charts
        history_df = df_enriched.tail(60)
        history = []
        for date, row in history_df.iterrows():
            history.append({
                "date": date.strftime("%Y-%m-%d"),
                "price": float(row["Close"].item()),
                "open": float(row["Open"].item()),
                "high": float(row["High"].item()),
                "low": float(row["Low"].item()),
                "volume": float(row["Volume"].item()),
                "rsi": float(row["rsi"].item()) if "rsi" in row else None,
                "macd": float(row["macd"].item()) if "macd" in row else None,
                "sma20": float(row["sma20"].item()) if "sma20" in row else None,
                "sma50": float(row["sma50"].item()) if "sma50" in row else None
            })

        current_price = history[-1]["price"]
        change = float(((predicted_price - current_price) / current_price) * 100)

        if change > dynamic_threshold:
            signal = "BUY"
        elif change < -dynamic_threshold:
            signal = "SELL"
        else:
            signal = "HOLD"

        return {
            "model": "PyTorch Transformer",
            "symbol": symbol,
            "current_price": float(current_price),
            "predicted_price": float(predicted_price),
            "expected_move": float(change),
            "threshold_used": float(dynamic_threshold),
            "volatility": float(volatility),
            "signal": signal,
            "history": history
        }

    except Exception as e:
        return {
            "model": "PyTorch Transformer",
            "symbol": symbol,
            "error": str(e),
            "signal": "ERROR"
        }