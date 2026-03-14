import yfinance as yf
from concurrent.futures import ThreadPoolExecutor


def get_fundamentals(symbol):
    try:
        ticker = yf.Ticker(symbol + ".NS")
        info = ticker.info

        fundamentals = {
            "symbol": symbol,
            "pe": info.get("trailingPE"),
            "pb": info.get("priceToBook"),
            "roe": info.get("returnOnEquity"),
            "debt_equity": info.get("debtToEquity"),
            "profit_margin": info.get("profitMargins"),
            "market_cap": info.get("marketCap")
        }

        fundamentals["score"] = calculate_score(fundamentals)
        return fundamentals
    except Exception as e:
        print(f"Error fetching fundamentals for {symbol}: {e}")
        return {
            "symbol": symbol,
            "pe": None,
            "pb": None,
            "roe": None,
            "debt_equity": None,
            "profit_margin": None,
            "market_cap": None,
            "score": 0
        }


def get_fundamentals_batch(symbols):
    """Fetch fundamentals for multiple symbols in parallel using threading."""
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(get_fundamentals, symbols))
    return results


def calculate_score(data):

    score = 0
    total = 0

    # PE ratio (lower better)
    if data["pe"]:
        total += 1
        if data["pe"] < 25:
            score += 1

    # PB ratio
    if data["pb"]:
        total += 1
        if data["pb"] < 5:
            score += 1

    # ROE
    if data["roe"]:
        total += 1
        if data["roe"] > 0.15:
            score += 1

    # Debt equity
    if data["debt_equity"]:
        total += 1
        if data["debt_equity"] < 1:
            score += 1

    # profit margin
    if data["profit_margin"]:
        total += 1
        if data["profit_margin"] > 0.1:
            score += 1

    if total == 0:
        return 0

    return round(score / total * 10, 2)