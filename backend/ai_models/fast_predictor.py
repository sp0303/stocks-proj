import os
import joblib
import numpy as np
import yfinance as yf
from tensorflow.keras.models import load_model
try:
    from ai_models.feature_engineer import prepare_multivariate_features
except ImportError:
    from feature_engineer import prepare_multivariate_features

LOOKBACK = 60
BASE_DIR = os.path.dirname(__file__)
TRAIN_DB = os.path.join(BASE_DIR, "training_db")

# Model Cache
_model_cache = {}

def get_model_and_scaler(symbol):
    # Standardize symbol for lookup
    if not symbol.endswith(".NS") and "^" not in symbol:
        symbol = symbol + ".NS"
    
    clean_symbol = symbol.replace("^", "INDEX_")
    
    if clean_symbol in _model_cache:
        return _model_cache[clean_symbol]["model"], _model_cache[clean_symbol]["scaler"]

    model_path = os.path.join(TRAIN_DB, f"{clean_symbol}_model.h5")
    scaler_path = os.path.join(TRAIN_DB, f"{clean_symbol}_scaler.save")

    # Fallback to Index model if specific stock model doesn't exist
    if not os.path.exists(model_path):
        print(f"Specific model for {symbol} not found. Falling back to Index model.")
        symbol = "^NSEI"
        clean_symbol = "INDEX_NSEI"
        model_path = os.path.join(TRAIN_DB, "INDEX_NSEI_model.h5")
        scaler_path = os.path.join(TRAIN_DB, "INDEX_NSEI_scaler.save")
        
        if clean_symbol in _model_cache:
            return _model_cache[clean_symbol]["model"], _model_cache[clean_symbol]["scaler"]

    try:
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            print(f"Loading AI model for {symbol}...")
            model = load_model(model_path, compile=False)
            scaler = joblib.load(scaler_path)
            _model_cache[clean_symbol] = {"model": model, "scaler": scaler}
            return model, scaler
        else:
            raise FileNotFoundError(f"No model found for {symbol} or fallback INDEX_NSEI")
    except Exception as e:
        print(f"Error loading model: {e}")
        # Final fallback to old legacy paths if they exist (backward compatibility)
        legacy_model = os.path.join(BASE_DIR, "saved_model.h5")
        legacy_scaler = os.path.join(BASE_DIR, "scaler.save")
        if os.path.exists(legacy_model):
            return load_model(legacy_model, compile=False), joblib.load(legacy_scaler)
        raise e

def predict(symbol):
    res = predict_detailed(symbol)
    if "error" in res:
        return res
    
    return {
        "model": "Multivariate LSTM",
        "current_price": res["current_price"],
        "predicted_price": res["predicted_price"],
        "expected_move": res["expected_move"],
        "signal": res["signal"],
        "rsi": res["history"][-1].get("rsi"),
        "macd": res["history"][-1].get("macd"),
        "sma20": res["history"][-1].get("sma20"),
        "sma50": res["history"][-1].get("sma50")
    }

def predict_detailed(symbol):
    if not symbol.endswith(".NS") and "^" not in symbol:
        symbol = symbol + ".NS"
    
    try:
        # Fetch 7 years for consistent volatility baseline
        df = yf.download(symbol, period="7y")

        if df.empty:
            return {
                "model": "Multivariate LSTM",
                "symbol": symbol,
                "error": "No price data available",
                "signal": "UNKNOWN"
            }

        # Calculate Volatility for Signal Threshold
        recent_prices = df['Close'].tail(60).values.flatten()
        daily_returns = np.diff(recent_prices) / recent_prices[:-1]
        volatility = np.std(daily_returns) * 100 # In percentage
        
        # Determine threshold (e.g., 2.0x volatility but min 1.5%)
        dynamic_threshold = max(1.5, volatility * 2.0)

        # Prepare 9-feature matrix and get the enriched dataframe
        from ai_models.feature_engineer import add_technical_indicators
        df_enriched = add_technical_indicators(df)
        features_matrix = prepare_multivariate_features(df)
        
        if len(features_matrix) < LOOKBACK:
            return {
                "model": "Multivariate LSTM",
                "symbol": symbol,
                "error": "Insufficient historical data",
                "signal": "UNKNOWN"
            }

        model, scaler = get_model_and_scaler(symbol)
        
        # Scale the full feature set
        scaled_features = scaler.transform(features_matrix)
        
        # Get the last LOOKBACK days
        last_60_scaled = scaled_features[-LOOKBACK:]
        last_60_scaled = np.reshape(last_60_scaled, (1, LOOKBACK, last_60_scaled.shape[1]))

        # Predict
        pred = model.predict(last_60_scaled)
        
        # Scaling back is tricky with multivariate. 
        # We need a dummy matrix to inverse transform only the 'Close' price (index 3).
        dummy = np.zeros((1, scaled_features.shape[1]))
        dummy[0, 3] = pred[0][0]
        predicted_price = float(scaler.inverse_transform(dummy)[0, 3])
        
        # Get history for display (Full Multivariate Set)
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
            "model": "Multivariate LSTM",
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
            "model": "Multivariate LSTM",
            "symbol": symbol,
            "error": str(e),
            "signal": "ERROR"
        }