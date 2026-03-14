import yfinance as yf

indices = {
    "nifty50": "^NSEI",
    "sensex": "^BSESN"
}

stocks = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS"
]


def get_indices():

    data = {}

    for name, ticker in indices.items():
        stock = yf.Ticker(ticker)
        info = stock.history(period="1d")

        price = round(info["Close"].iloc[-1], 2)

        data[name] = price

    return data


def get_stocks():

    result = []

    for ticker in stocks:

        stock = yf.Ticker(ticker)
        info = stock.history(period="1d")

        price = round(info["Close"].iloc[-1], 2)

        result.append({
            "symbol": ticker,
            "price": price
        })

    return result

import requests
from news_service import fetch_all_news
from fundamental_service import get_fundamentals_batch
from technical_service import get_technical_batch

async def _fetch_stock_data(index="NIFTY 50"):
    # Encode index for URL
    encoded_index = index.replace(" ", "%20")
    fallback_url = f"https://www.nseindia.com/api/equity-stockIndices?index={encoded_index}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "*/*"
    }

    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=10)

        # Fetch index-specific data
        res = session.get(fallback_url, headers=headers, timeout=10)
        res.raise_for_status()
        json_data = res.json()
        
        raw_data = []
        if "data" in json_data:
            # Skip the first item if it's the index summary (priority 1)
            raw_data = [s for s in json_data["data"] if s.get('priority') != 1 and s.get('symbol') != index]
        
        result = []
        for item in raw_data:
            p_change = item.get("pChange", item.get("perChange", item.get("net_price", 0)))
            price = item.get("lastPrice", item.get("ltp", item.get("price", 0)))
            volume = item.get("totalTradedVolume", item.get("trade_quantity", item.get("trdVol", item.get("trdQty", item.get("totalTradedQty", 0)))))

            result.append({
                "company": item.get("symbol", item.get("companyName", "N/A")),
                "price": price,
                "change": item.get("change", 0),
                "pchange": p_change,
                "volume": volume,
                "news_impact": 0
            })
        return result
    except Exception as e:
        print(f"Error fetching stock data for {index}: {e}")
        return []

async def get_gainers(type="gainers", index="NIFTY 50"):
    result = await _fetch_stock_data(index)
    if not result: return []

    is_gainers = (type == "gainers")
    # Filter based on type
    if is_gainers:
        filtered = [s for s in result if s["pchange"] > 0]
    else:
        filtered = [s for s in result if s["pchange"] < 0]

    # Batch enrichment
    return await _enrich_stock_data(filtered, sort_reverse=is_gainers)

async def get_movers(index="NIFTY 50"):
    result = await _fetch_stock_data(index)
    if not result: return []
    
    # Enrich all 50 stocks
    return await _enrich_stock_data(result)

async def _enrich_stock_data(stocks, sort_reverse=True):
    if not stocks: return []
    
    # Ensure result is sorted by pchange by default (Gainers style)
    stocks = sorted(stocks, key=lambda x: x["pchange"], reverse=sort_reverse)
    
    # Cap enrichments to 50 for safety
    target_stocks = stocks[:50]
    symbols = [s["company"] for s in target_stocks]

    # 1. Fetch News
    news_data = await fetch_all_news(symbols)
    news_map = {item["company"]: item["articles"] for item in news_data}
    
    # 2. Fetch Fundamentals
    fundamentals_data = get_fundamentals_batch(symbols)
    fund_map = {f["symbol"]: f for f in fundamentals_data}
    
    # 3. Fetch Technicals
    technicals_data = get_technical_batch(symbols)
    tech_map = {t["symbol"]: t for t in technicals_data}

    # symbols = [s["company"] for s in target_stocks] (removed heavy batch)

    for stock in target_stocks:
        # News
        articles = news_map.get(stock["company"], [])
        stock["articles"] = articles
        if articles:
            stock["news_impact"] = sum(a["score"] for a in articles) / len(articles)
        
        # Fundamentals
        stock["fundamentals"] = fund_map.get(stock["company"], {})
        stock["fundamental_score"] = stock["fundamentals"].get("score", 0)
        
        # Technicals
        stock["technicals"] = tech_map.get(stock["company"], {})
        stock["technical_action"] = stock["technicals"].get("action", "Neutral")

        # Insights (removed for lazy loading)
        stock["insights"] = {}

    return target_stocks



def get_insights_batch(symbols):
    # Ensure .NS suffix for NSE stocks
    yf_symbols = [s if (s.endswith(".NS") or "^" in s) else f"{s}.NS" for s in symbols]
    
    try:
        # Download 5y history for all (for price changes and volume spike)
        data = yf.download(yf_symbols, period="5y", interval="1d", group_by='ticker', threads=True, progress=False)
        
        results = {}
        for symbol, yf_symbol in zip(symbols, yf_symbols):
            try:
                # Handle single vs multi-ticker dataframe structure
                if len(symbols) == 1:
                    hist = data
                else:
                    hist = data[yf_symbol]
                
                hist = hist.dropna(subset=['Close'])
                if hist.empty:
                    results[symbol] = {
                        "volume": {"today_volume": 0, "avg_volume_20": 0, "volume_spike": 1.0},
                        "returns": {p: 0 for p in ["1_week", "1_month", "3_month", "6_month", "1_year", "5_year"]}
                    }
                    continue

                # Volume spike
                today_vol = hist["Volume"].iloc[-1]
                avg_vol = hist["Volume"].tail(20).mean()
                spike = today_vol / avg_vol if avg_vol > 0 else 1.0
                
                # Returns calculation
                latest = hist["Close"].iloc[-1]
                def get_pct(days):
                    if len(hist) < days: return 0
                    old = hist["Close"].iloc[-days]
                    return round((latest - old) / old * 100, 2)
                
                results[symbol] = {
                    "volume": {
                        "today_volume": int(today_vol),
                        "avg_volume_20": int(avg_vol),
                        "volume_spike": float(round(spike, 2))
                    },
                    "returns": {
                        "1_week": float(get_pct(5)),
                        "1_month": float(get_pct(21)),
                        "3_month": float(get_pct(63)),
                        "6_month": float(get_pct(126)),
                        "1_year": float(get_pct(252)),
                        "5_year": float(get_pct(len(hist)-1))
                    }
                }
            except Exception as e:
                print(f"Error parsing insights for {symbol}: {e}")
                results[symbol] = {
                    "volume": {"today_volume": 0, "avg_volume_20": 0, "volume_spike": 1.0},
                    "returns": {p: 0 for p in ["1_week", "1_month", "3_month", "6_month", "1_year", "5_year"]}
                }
        return results
    except Exception as e:
        print(f"Error in batch insights download: {e}")
        return {s: {"volume": {"today_volume": 0, "avg_volume_20": 0, "volume_spike": 1.0}, "returns": {p: 0 for p in ["1_week", "1_month", "3_month", "6_month", "1_year", "5_year"]}} for s in symbols}

def get_volume_spike(symbol):
    if not symbol.endswith(".NS") and "^" not in symbol:
        symbol += ".NS"

    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo")

        if hist.empty:
            return {
                "today_volume": 0,
                "avg_volume_20": 0,
                "volume_spike": 1.0
            }

        today_volume = hist["Volume"].iloc[-1]
        avg_volume_20 = hist["Volume"].tail(20).mean()

        spike_ratio = today_volume / avg_volume_20 if avg_volume_20 > 0 else 1.0

        return {
            "today_volume": int(today_volume),
            "avg_volume_20": int(avg_volume_20),
            "volume_spike": round(spike_ratio, 2)
        }
    except Exception as e:
        print(f"Error in volume spike for {symbol}: {e}")
        return {"today_volume": 0, "avg_volume_20": 0, "volume_spike": 1.0}

def get_price_changes(symbol):
    if not symbol.endswith(".NS") and "^" not in symbol:
        symbol += ".NS"

    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5y")

        if hist.empty:
            return {p: 0 for p in ["1_week", "1_month", "3_month", "6_month", "1_year", "5_year"]}

        latest = hist["Close"].iloc[-1]

        def pct_change(days):
            if len(hist) < days:
                return None
            old = hist["Close"].iloc[-days]
            return round((latest - old) / old * 100, 2)

        return {
            "1_week": pct_change(5),
            "1_month": pct_change(21),
            "3_month": pct_change(63),
            "6_month": pct_change(126),
            "1_year": pct_change(252),
            "5_year": pct_change(len(hist) - 1)
        }
    except Exception as e:
        print(f"Error in price changes for {symbol}: {e}")
        return {p: 0 for p in ["1_week", "1_month", "3_month", "6_month", "1_year", "5_year"]}


