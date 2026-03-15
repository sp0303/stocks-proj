import yfinance as yf
import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import joblib
import os
try:
    from ai_models.feature_engineer import prepare_multivariate_features
except ImportError:
    import sys
    sys.path.append(os.path.dirname(__file__))
    from feature_engineer import prepare_multivariate_features

BASE_DIR = os.path.dirname(__file__)
TRAIN_DB = os.path.join(BASE_DIR, "training_db")

# Ensure training_db exists
if not os.path.exists(TRAIN_DB):
    os.makedirs(TRAIN_DB)

LOOKBACK = 60

def train(symbol="RELIANCE.NS"):
    # Fix symbol naming for filesystem
    clean_symbol = symbol.replace("^", "INDEX_")
    model_path = os.path.join(TRAIN_DB, f"{clean_symbol}_model.keras")
    scaler_path = os.path.join(TRAIN_DB, f"{clean_symbol}_scaler.save")

    print(f"Training multivariate model for {symbol}...")
    
    # Fetch from 2019-01-01 baseline
    df = yf.download(symbol, start="2019-01-01")
    
    if df.empty:
        print("Error: No data found")
        return

    # Prepare 20-feature matrix
    data = prepare_multivariate_features(df)
    
    if len(data) < LOOKBACK + 50:
        print(f"Skipping {symbol}: Insufficient data points ({len(data)})")
        return
    
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(data)

    X = []
    y = []

    # Features are [OHLCV, SMAs, EMAs, RSI, MACD, ROC, Stoch, ATR, BB, OBV, VWAP, VolChange]
    # We predict 'Close' (index 3)
    target_idx = 3

    for i in range(LOOKBACK, len(scaled)):
        X.append(scaled[i-LOOKBACK:i])
        y.append(scaled[i, target_idx])

    X = np.array(X)
    y = np.array(y)

    print(f"X shape: {X.shape}, y shape: {y.shape}")

    model = Sequential()
    
    # Multivariate input shape: (LOOKBACK, num_features)
    model.add(LSTM(64, return_sequences=True, input_shape=(LOOKBACK, X.shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(64, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(1))

    model.compile(
        optimizer='adam',
        loss='mse'
    )

    model.fit(X, y, epochs=15, batch_size=32, verbose=1)

    model.save(model_path)
    joblib.dump(scaler, scaler_path)

    print("Multivariate model trained and saved successfully")

if __name__ == "__main__":
    train()