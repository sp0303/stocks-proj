import traceback
import sys
import os
from ai_models.fast_predictor import predict_detailed

try:
    print("Testing RELIANCE...")
    res = predict_detailed("RELIANCE")
    print("Result Model:", res.get("model"))
    print("Result Error:", res.get("error"))
    if "error" in res and res["error"] == "'price'":
        print("DETECTED 'price' error in return dict.")
except Exception:
    traceback.print_exc()

# Let's try to find where it's happening by forcing it to fail WITHOUT the catch block
def predict_raw(symbol):
    # This is a copy-paste of predict_detailed but without the broad try-except 
    # so we can see the real traceback in the console if it crashes.
    from ai_models.fast_predictor import add_technical_indicators, prepare_multivariate_features, get_model_and_scaler, LOOKBACK
    import yfinance as yf
    import numpy as np

    if not symbol.endswith(".NS") and "^" not in symbol:
        symbol = symbol + ".NS"
    
    df = yf.download(symbol, start="2019-01-01")
    df_enriched = add_technical_indicators(df)
    features_matrix = prepare_multivariate_features(df)
    model, scaler = get_model_and_scaler(symbol)
    scaled_features = scaler.transform(features_matrix)
    last_60_scaled = scaled_features[-LOOKBACK:]
    last_60_scaled = np.reshape(last_60_scaled, (1, LOOKBACK, last_60_scaled.shape[1]))
    pred = model.predict(last_60_scaled)
    dummy = np.zeros((1, scaled_features.shape[1]))
    dummy[0, 3] = pred[0][0]
    predicted_price = float(scaler.inverse_transform(dummy)[0, 3])
    history_df = df_enriched.tail(60)
    history = []
    feature_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'sma20', 'sma50', 'ema20', 'ema50', 'ema200', 'rsi', 'macd', 'roc', 'stoch_k', 'atr', 'bb_upper', 'bb_lower', 'obv', 'vwap', 'volume_change']
    for date, row in history_df.iterrows():
        item = {"date": date.strftime("%Y-%m-%d")}
        for col in feature_cols:
            if col in row:
                val = row[col]
                item[col.lower()] = float(val.item()) if hasattr(val, 'item') else float(val)
        history.append(item)
    
    # We suspect it fails here or near here
    current_price = history[-1]["close"]
    return current_price

print("\nRunning raw test to see traceback...")
try:
    cp = predict_raw("RELIANCE")
    print(f"Current Price from raw: {cp}")
except Exception:
    traceback.print_exc()
