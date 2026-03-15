import asyncio
import os
import sys
from concurrent.futures import ThreadPoolExecutor
import time
import random

# Add parent dir to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nifty50 import NIFTY50
from news_service import fetch_news
from fundamental_service import get_fundamentals
from technical_service import get_technical
from ai_models.fast_predictor import predict as lstm_predict
from ai_models.transformer_predict import predict as transformer_predict
import aiohttp

def calculate_consensus(lstm, trans):
    """Reused consensus logic for aggregation."""
    if "error" in lstm and "error" in trans:
        return {"verdict": "UNAVAILABLE", "consensus": False}
    
    if "error" in lstm: return {"verdict": trans.get("signal", "UNKNOWN"), "consensus": False}
    if "error" in trans: return {"verdict": lstm.get("signal", "UNKNOWN"), "consensus": False}

    l_sig = lstm.get("signal", "HOLD")
    t_sig = trans.get("signal", "HOLD")
    
    if l_sig == t_sig:
        return {"verdict": l_sig, "consensus": True}
    elif (l_sig == "BUY" and t_sig == "SELL") or (l_sig == "SELL" and t_sig == "BUY"):
        return {"verdict": "DIVERGENT", "consensus": False}
    else:
        return {"verdict": l_sig if l_sig != "HOLD" else t_sig, "consensus": False}

async def get_stock_intelligence(symbol, session=None, retries=2):
    """
    Aggregates all intelligence for a single stock with retries for yfinance stability.
    """
    # Fix symbol naming
    yf_symbol = symbol + ".NS" if "." not in symbol and "^" not in symbol else symbol
    
    for attempt in range(retries + 1):
        try:
            loop = asyncio.get_event_loop()
            
            # News is already async
            news_task = fetch_news(session, symbol) if session else asyncio.sleep(0)
            
            with ThreadPoolExecutor() as pool:
                # Run sync services in threads
                fundamental_task = loop.run_in_executor(pool, get_fundamentals, symbol)
                technical_task = loop.run_in_executor(pool, get_technical, symbol)
                lstm_task = loop.run_in_executor(pool, lstm_predict, symbol)
                trans_task = loop.run_in_executor(pool, transformer_predict, symbol)
                
                results = await asyncio.gather(news_task, fundamental_task, technical_task, lstm_task, trans_task)
                
            news, fundamentals, technicals, lstm, trans = results
            
            # If we got critical data failures, maybe retry? 
            # (Crumb errors often manifest as empty results or specific exceptions)
            if not technicals or (technicals.get("price") is None and attempt < retries):
                time.sleep(random.uniform(1, 3))
                continue

            consensus = calculate_consensus(lstm, trans)
            
            return {
                "symbol": symbol,
                "price": technicals.get("price"),
                "news": {
                    "articles": news.get("articles", []) if news else [],
                    "impact_score": round(sum(a['score'] for a in news.get('articles', []))/len(news.get('articles', [])) if news and news.get('articles') else 0, 2)
                },
                "fundamentals": fundamentals,
                "technicals": technicals,
                "ai": {
                    "lstm": {"signal": lstm.get("signal"), "move": lstm.get("expected_move"), "features": lstm.get("features", {})},
                    "transformer": {"signal": trans.get("signal"), "move": trans.get("expected_move"), "features": trans.get("features", {})},
                    "consensus": consensus
                }
            }
        except Exception as e:
            if attempt < retries:
                print(f"Retry {attempt+1} for {symbol} due to: {e}")
                time.sleep(random.uniform(1, 2))
            else:
                return {"symbol": symbol, "error": str(e), "status": "FAILED"}

async def get_index_intelligence():
    """Aggregates intelligence for all NIFTY 50 stocks with throttling and robust timeouts."""
    # Global timeout for the entire batch - 120s is safer for 50 concurrent yfinance calls
    timeout = aiohttp.ClientTimeout(total=120)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [get_stock_intelligence(stock, session) for stock in NIFTY50]
        # Throttling strictly to 5 concurrent stocks to avoid Yahoo crumb invalidation and CPU contention
        semaphore = asyncio.Semaphore(5)
        
        async def sem_task(task_coro):
            async with semaphore:
                # Add a tiny jitter between starts to further avoid race conditions
                await asyncio.sleep(random.uniform(0.1, 0.5))
                try:
                    # Individual stock timeout - 45s is generous but prevents infinite hangs
                    return await asyncio.wait_for(task_coro, timeout=45)
                except asyncio.TimeoutError:
                    return {"error": "Timeout", "status": "FAILED"}
                except Exception as e:
                    return {"error": str(e), "status": "FAILED"}
        
        print(f"Starting Intelligence Hub for {len(NIFTY50)} stocks with 120s timeout...")
        results = await asyncio.gather(*[sem_task(t) for t in tasks])
        return results
