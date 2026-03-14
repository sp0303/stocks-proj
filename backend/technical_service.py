import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
from concurrent.futures import ThreadPoolExecutor


def get_technical(symbol):
    try:
        ticker = yf.Ticker(symbol + ".NS")
        df = ticker.history(period="3mo")

        if df.empty:
            return {
                "symbol": symbol,
                "rsi": None,
                "macd": None,
                "macd_signal": None,
                "sma20": None,
                "sma50": None,
                "action": "Neutral",
                "score": 50
            }

        # RSI
        rsi = RSIIndicator(close=df["Close"], window=14)
        df["rsi"] = rsi.rsi()

        # MACD
        macd = MACD(close=df["Close"])
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()

        # Moving averages
        sma20 = SMAIndicator(close=df["Close"], window=20)
        sma50 = SMAIndicator(close=df["Close"], window=50)

        df["sma20"] = sma20.sma_indicator()
        df["sma50"] = sma50.sma_indicator()

        latest = df.iloc[-1]
        
        data = {
            "symbol": symbol,
            "rsi": round(latest["rsi"], 2) if not pd.isna(latest["rsi"]) else None,
            "macd": round(latest["macd"], 2) if not pd.isna(latest["macd"]) else None,
            "macd_signal": round(latest["macd_signal"], 2) if not pd.isna(latest["macd_signal"]) else None,
            "sma20": round(latest["sma20"], 2) if not pd.isna(latest["sma20"]) else None,
            "sma50": round(latest["sma50"], 2) if not pd.isna(latest["sma50"]) else None,
            "price": round(latest["Close"], 2)
        }
        
        action, score = calculate_technical_score(data)
        data["action"] = action
        data["score"] = score
        
        return data
    except Exception as e:
        print(f"Error fetching technicals for {symbol}: {e}")
        return {
            "symbol": symbol,
            "rsi": None,
            "macd": None,
            "macd_signal": None,
            "sma20": None,
            "sma50": None,
            "action": "Neutral",
            "score": 50
        }


def get_technical(symbol):
    try:
        ticker = yf.Ticker(symbol + ".NS")
        # Fetch 6 months of history for 3-month returns and SMA50
        df = ticker.history(period="6mo")

        if df.empty:
            return {
                "symbol": symbol,
                "rsi": None,
                "macd": None,
                "macd_signal": None,
                "sma20": None,
                "sma50": None,
                "action": "Neutral",
                "score": 5,
                "heatmap_score": 5,
                "heatmap_signal": "Neutral"
            }

        # RSI
        rsi = RSIIndicator(close=df["Close"], window=14)
        df["rsi"] = rsi.rsi()

        # MACD
        macd = MACD(close=df["Close"])
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()

        # Moving averages
        sma20 = SMAIndicator(close=df["Close"], window=20)
        sma50 = SMAIndicator(close=df["Close"], window=50)

        df["sma20"] = sma20.sma_indicator()
        df["sma50"] = sma50.sma_indicator()

        latest = df.iloc[-1]
        
        # Additional data for Heatmap
        # Volume Spike (20-day avg)
        avg_vol_20 = df["Volume"].tail(20).mean()
        volume_ratio = latest["Volume"] / avg_vol_20 if avg_vol_20 > 0 else 1.0
        
        # Returns
        def get_pct_change(days):
            if len(df) < days + 1: return 0
            old_price = df["Close"].iloc[-(days + 1)]
            return ((latest["Close"] - old_price) / old_price) * 100

        data = {
            "symbol": symbol,
            "rsi": float(round(latest["rsi"], 2)) if not pd.isna(latest["rsi"]) else None,
            "macd": float(round(latest["macd"], 2)) if not pd.isna(latest["macd"]) else None,
            "macd_signal": float(round(latest["macd_signal"], 2)) if not pd.isna(latest["macd_signal"]) else None,
            "sma20": float(round(latest["sma20"], 2)) if not pd.isna(latest["sma20"]) else None,
            "sma50": float(round(latest["sma50"], 2)) if not pd.isna(latest["sma50"]) else None,
            "price": float(round(latest["Close"], 2)),
            "volume_ratio": float(volume_ratio),
            "return_1m": float(get_pct_change(21)),
            "return_3m": float(get_pct_change(63)),
            "is_bullish_crossover": bool((df["macd"].iloc[-2] <= df["macd_signal"].iloc[-2]) and (df["macd"].iloc[-1] > df["macd_signal"].iloc[-1]))
        }
        
        heatmap_score, heatmap_signal = calculate_heatmap_score(data)
        data["heatmap_score"] = heatmap_score
        data["heatmap_signal"] = heatmap_signal
        
        # Preserve old score/action for compatibility if needed, but update to use new logic if preferred
        # For now, let's keep them distinct but align them
        data["action"] = heatmap_signal
        data["score"] = heatmap_score * 10 # Convert 0-10 to 0-100
        
        return data
    except Exception as e:
        print(f"Error fetching technicals for {symbol}: {e}")
        return {
            "symbol": symbol,
            "rsi": None,
            "macd": None,
            "macd_signal": None,
            "sma20": None,
            "sma50": None,
            "action": "Neutral",
            "score": 50,
            "heatmap_score": 5,
            "heatmap_signal": "Neutral"
        }


def calculate_heatmap_score(data):
    """Calculate the Technical Heatmap Score (0-10) based on weighted indicators."""
    
    # 1. RSI Score
    rsi = data.get("rsi")
    if rsi is None: r_score = 5
    elif rsi < 30: r_score = 8
    elif 30 <= rsi < 50: r_score = 6
    elif 50 <= rsi < 70: r_score = 4
    else: r_score = 2
    
    # 2. MACD Score
    m_score = 3
    if data.get("is_bullish_crossover"):
        m_score = 10
    elif data.get("macd") and data.get("macd_signal"):
        if data["macd"] > data["macd_signal"]:
            m_score = 6
            
    # 3. SMA Trend Scores
    price = data.get("price")
    sma20 = data.get("sma20")
    sma50 = data.get("sma50")
    
    s20_score = 10 if (price and sma20 and price > sma20) else 3
    s50_score = 10 if (price and sma50 and price > sma50) else 3
    
    # 4. Volume Spike Score
    v = data.get("volume_ratio", 1.0)
    if v > 2: v_score = 10
    elif 1.5 < v <= 2: v_score = 7
    elif 1 < v <= 1.5: v_score = 5
    else: v_score = 3
    
    # 5. Momentum Scores (Returns)
    def score_return(ret):
        if ret > 15: return 10
        elif 10 <= ret <= 15: return 8
        elif 5 <= ret < 10: return 6
        elif 0 <= ret < 5: return 4
        else: return 2
        
    r1m_score = score_return(data.get("return_1m", 0))
    r3m_score = score_return(data.get("return_3m", 0))
    
    # Final Weighted Calculation
    # Score = 0.2*R + 0.2*M + 0.15*S20 + 0.15*S50 + 0.1*V + 0.1*R1M + 0.1*R3M
    final_score = (
        0.20 * r_score +
        0.20 * m_score +
        0.15 * s20_score +
        0.15 * s50_score +
        0.10 * v_score +
        0.10 * r1m_score +
        0.10 * r3m_score
    )
    
    final_score = float(round(final_score, 1))
    
    # Determine Signal
    if final_score >= 8.0: signal = "Strong Buy"
    elif final_score >= 6.5: signal = "Buy"
    elif final_score <= 3.5: signal = "Strong Sell"
    elif final_score <= 5.0: signal = "Sell"
    else: signal = "Neutral"
    
    return final_score, signal


def get_technical_batch(symbols):
    """Fetch technicals for multiple symbols in parallel."""
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(get_technical, symbols))
    return results