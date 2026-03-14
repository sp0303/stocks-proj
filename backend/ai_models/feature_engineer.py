import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator, ROCIndicator, StochasticOscillator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import AverageTrueRange, BollingerBands
from ta.volume import OnBalanceVolumeIndicator, VolumeWeightedAveragePrice

def add_technical_indicators(df):
    """
    Adds 20 technical indicators to the dataframe.
    """
    df = df.copy()
    
    # Ensure Close is 1D Series
    close_1d = df['Close'].squeeze()
    high_1d = df['High'].squeeze()
    low_1d = df['Low'].squeeze()
    volume_1d = df['Volume'].squeeze()
    
    # 1-5. OHLCV (Already in DF)
    
    # 6-10. Moving Averages
    df['sma20'] = SMAIndicator(close=close_1d, window=20).sma_indicator()
    df['sma50'] = SMAIndicator(close=close_1d, window=50).sma_indicator()
    df['ema20'] = EMAIndicator(close=close_1d, window=20).ema_indicator()
    df['ema50'] = EMAIndicator(close=close_1d, window=50).ema_indicator()
    df['ema200'] = EMAIndicator(close=close_1d, window=200).ema_indicator()
    
    # 11-14. Momentum
    df['rsi'] = RSIIndicator(close=close_1d, window=14).rsi()
    df['macd'] = MACD(close=close_1d).macd()
    df['roc'] = ROCIndicator(close=close_1d, window=12).roc()
    df['stoch_k'] = StochasticOscillator(high=high_1d, low=low_1d, close=close_1d, window=14, smooth_window=3).stoch()
    
    # 15-17. Volatility
    df['atr'] = AverageTrueRange(high=high_1d, low=low_1d, close=close_1d, window=14).average_true_range()
    bb = BollingerBands(close=close_1d, window=20, window_dev=2)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
    
    # 18-20. Volume
    df['obv'] = OnBalanceVolumeIndicator(close=close_1d, volume=volume_1d).on_balance_volume()
    df['vwap'] = VolumeWeightedAveragePrice(high=high_1d, low=low_1d, close=close_1d, volume=volume_1d, window=14).volume_weighted_average_price()
    df['volume_change'] = df['Volume'].pct_change() * 100
    
    # Fill NaNs from indicators
    df = df.ffill().bfill()
    
    return df

def prepare_multivariate_features(df):
    """
    Extracts the updated 20-feature set:
    OHLCV, SMAs, EMAs, RSI, MACD, ROC, Stoch, ATR, BB, OBV, VWAP, VolChange
    """
    df = add_technical_indicators(df)
    
    features = [
        'Open', 'High', 'Low', 'Close', 'Volume',
        'sma20', 'sma50', 'ema20', 'ema50', 'ema200',
        'rsi', 'macd', 'roc', 'stoch_k',
        'atr', 'bb_upper', 'bb_lower',
        'obv', 'vwap', 'volume_change'
    ]
    
    # Ensure all features exist and are cleaned
    for f in features:
        if f not in df.columns:
            df[f] = 0
            
    return df[features].values
