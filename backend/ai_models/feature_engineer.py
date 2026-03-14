import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator

def add_technical_indicators(df):
    """
    Adds RSI, MACD, SMA20, and SMA50 to the dataframe.
    Expects 'Close' column to exist.
    """
    df = df.copy()
    
    # Ensure Close is 1D Series (yfinance sometimes returns 2D DataFrame)
    close_1d = df['Close'].squeeze()
    
    # RSI
    df['rsi'] = RSIIndicator(close=close_1d, window=14).rsi()
    
    # MACD
    macd = MACD(close=close_1d)
    df['macd'] = macd.macd()
    
    # SMAs
    df['sma20'] = SMAIndicator(close=close_1d, window=20).sma_indicator()
    df['sma50'] = SMAIndicator(close=close_1d, window=50).sma_indicator()
    
    # Fill NaNs from indicators (indicators need lead time)
    df = df.ffill().bfill()
    
    return df

def prepare_multivariate_features(df):
    """
    Extracts the professional feature set:
    Open, High, Low, Close, Volume, RSI, MACD, SMA20, SMA50
    """
    df = add_technical_indicators(df)
    
    features = ['Open', 'High', 'Low', 'Close', 'Volume', 'rsi', 'macd', 'sma20', 'sma50']
    
    # Ensure all features exist
    for f in features:
        if f not in df.columns:
            # Fallback for Volume if missing (unlikely with yfinance)
            df[f] = 0
            
    return df[features].values
