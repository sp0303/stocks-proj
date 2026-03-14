import yfinance as yf
import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense


LOOKBACK = 60


def fetch_stock_data(symbol):
    df = yf.download(symbol, period="6mo", interval="1d")
    df = df[['Close']]
    return df


def prepare_data(data):

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    x = []
    y = []

    for i in range(LOOKBACK, len(scaled_data)):
        x.append(scaled_data[i-LOOKBACK:i])
        y.append(scaled_data[i])

    x = np.array(x)
    y = np.array(y)

    return x, y, scaler


def build_model(input_shape):

    model = Sequential()

    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(50))
    model.add(Dense(1))

    model.compile(
        optimizer='adam',
        loss='mean_squared_error'
    )

    return model


def train_model(x, y):

    model = build_model((x.shape[1], 1))

    model.fit(
        x,
        y,
        epochs=5,
        batch_size=16,
        verbose=0
    )

    return model


def predict(symbol):

    df = fetch_stock_data(symbol)

    x, y, scaler = prepare_data(df.values)

    model = train_model(x, y)

    last_60 = df.values[-LOOKBACK:]
    last_60 = scaler.transform(last_60)

    last_60 = np.reshape(last_60, (1, LOOKBACK, 1))

    predicted_price = model.predict(last_60)

    predicted_price = float(scaler.inverse_transform(predicted_price)[0][0])

    current_price = float(df['Close'].iloc[-1])

    change = float(((predicted_price - current_price) / current_price) * 100)

    if change > 2:
        signal = "BUY"
    elif change < -2:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {
        "model": "lstm",
        "current_price": float(current_price),
        "predicted_price": float(predicted_price),
        "expected_move_percent": float(change),
        "signal": signal
    }