from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from services import get_indices, get_stocks, get_gainers, get_movers, get_volume_spike, get_price_changes
from news_service import fetch_all_news
from nifty50 import NIFTY50
import asyncio
import os
import sys

from fundamental_service import get_fundamentals, get_fundamentals_batch
from technical_service import get_technical, get_technical_batch
from social_sentiment import get_social_sentiment
from ai_models.fast_predictor import predict as lstm_predict, predict_detailed as lstm_predict_detailed
from ai_models.transformer_predict import predict as transformer_predict, predict_detailed as transformer_predict_detailed
from intelligence_service import get_stock_intelligence, get_index_intelligence

from fastapi.responses import FileResponse, JSONResponse
import httpx
import aiohttp
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
PORT = int(os.getenv("PORT", 8000))
SOCIAL_SERVICE_PORT = int(os.getenv("SOCIAL_SERVICE_PORT", 8001))

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/indices")
def indices():
    return get_indices()


@app.get("/stocks")
def stocks():
    return get_stocks()


@app.get("/movers")
async def movers(index: str = "NIFTY 50"):
    return await get_movers(index)


@app.get("/gainers")
async def gainers(index: str = "NIFTY 50"):
    return await get_gainers("gainers", index)


@app.get("/losers")
async def losers(index: str = "NIFTY 50"):
    return await get_gainers("losers", index)


@app.get("/news-impact")
async def news_impact():
    return await fetch_all_news(NIFTY50)


@app.get("/fundamentals")
def fundamentals(symbol: str = None, symbols: str = None):
    if symbols:
        return get_fundamentals_batch(symbols.split(","))
    return get_fundamentals(symbol)


@app.get("/fundamentals-batch")
def fundamentals_batch(symbols: str):
    return get_fundamentals_batch(symbols.split(","))


@app.get("/technical")
def technical(symbol: str = None, symbols: str = None):
    if symbols:
        return get_technical_batch(symbols.split(","))
    return get_technical(symbol)


@app.get("/technical-batch")
def technical_batch(symbols: str):
    return get_technical_batch(symbols.split(","))


@app.get("/social-sentiment/{symbol}")
async def social_sentiment(symbol: str):
    return await get_social_sentiment(symbol)


@app.get("/stock-insights/{symbol}")
def stock_insights(symbol):

    volume = get_volume_spike(symbol)
    price = get_price_changes(symbol)

    return {
        "volume": volume,
        "returns": price
    }

@app.get("/ai/lstm/{symbol}")
def lstm_prediction(symbol: str):
    return lstm_predict(symbol)

@app.get("/ai/lstm-detailed/{symbol}")
def lstm_prediction_detailed(symbol: str):
    return lstm_predict_detailed(symbol)

@app.get("/ai/transformer/{symbol}")
def transformer_prediction_fast(symbol: str):
    return transformer_predict(symbol)

@app.get("/ai/transformer-detailed/{symbol}")
def transformer_prediction(symbol: str):
    return transformer_predict_detailed(symbol)

@app.get("/ai/consensus/{symbol}")
def get_ai_consensus(symbol: str):
    lstm = lstm_predict(symbol)
    trans = transformer_predict(symbol)
    
    # Error handling
    if "error" in lstm and "error" in trans:
        return {"verdict": "UNAVAILABLE", "reason": "Both models failed"}
    
    # If one fails, use the other
    if "error" in lstm: return {"verdict": trans["signal"], "consensus": False, "note": "LSTM failed"}
    if "error" in trans: return {"verdict": lstm["signal"], "consensus": False, "note": "Transformer failed"}

    # Consensus Logic
    l_sig = lstm["signal"]
    t_sig = trans["signal"]
    
    if l_sig == t_sig:
        verdict = l_sig # Agreement
        consensus = True
    elif (l_sig == "BUY" and t_sig == "SELL") or (l_sig == "SELL" and t_sig == "BUY"):
        verdict = "DIVERGENT" # Conflict
        consensus = False
    else:
        # One says HOLD, the other has a direction. 
        # We'll take the direction but mark it as weak consensus.
        verdict = l_sig if l_sig != "HOLD" else t_sig
        consensus = False

    return {
        "symbol": symbol,
        "verdict": verdict,
        "consensus": consensus,
        "lstm": {"signal": l_sig, "move": lstm["expected_move"]},
        "transformer": {"signal": t_sig, "move": trans["expected_move"]},
        "timestamp": os.path.getmtime(os.path.join(os.path.dirname(__file__), "ai_models/training_db")) # Placeholder for freshness
    }

@app.get("/ai/intelligence/stock/{symbol}")
async def stock_intelligence(symbol: str):
    """Get full intelligence (News, Funda, Tech, AI) for one stock."""
    async with aiohttp.ClientSession() as session:
        return await get_stock_intelligence(symbol, session)

@app.get("/ai/intelligence/index/nifty50")
async def index_intelligence():
    """Get full intelligence for entire NIFTY 50."""
    return await get_index_intelligence()

# PROXIES FOR SOCIAL SERVICE
@app.get("/social-results/{symbol}")
async def get_social_results(symbol: str):
    url = f"http://localhost:{SOCIAL_SERVICE_PORT}/results/{symbol}.json"
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(url)
            if res.status_code == 200:
                return JSONResponse(content=res.json())
            return JSONResponse(content={"error": "Not found"}, status_code=404)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)

# Mount frontend static files LAST to avoid shadowing API routes
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")



@app.get("/social-screenshots/{filename}")
async def get_social_screenshot(filename: str):
    url = f"http://localhost:{SOCIAL_SERVICE_PORT}/screenshots/{filename}"
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(url)
            if res.status_code == 200:
                from fastapi.responses import Response
                return Response(content=res.content, media_type="image/png")
            return JSONResponse(content={"error": "Not found"}, status_code=404)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)