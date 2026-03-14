# Stock AI Dashboard 📈

A comprehensive stock analysis dashboard providing deep insights into technicals, fundamentals, news impact, and social sentiment.

## 🚀 Features

- **Market Movers**: Real-time tracking of top gainers and losers across multiple indices (Nifty 50, Bank, IT, Auto, etc.).
- **Technical Heatmap**: A sophisticated 0-10 scoring system based on weighted indicators (RSI, MACD, SMAs, Volume, and Returns).
- **Fundamental Analysis**: Key financial metrics (PE, ROE, D/E) with an overall health score.
- **Intelligence Insights**: Detailed analysis of volume spikes and multi-period performance.
- **Social Intelligence**: Sentiment analysis from social media platforms with evidence-based screenshotting.
- **News Impact**: Real-time news fetching and automated sentiment assessment on stock prices.
- **Responsive Design**: Fully optimized for Desktop, Tablet, and Mobile devices.

## 📂 Project Structure

```text
stocks-proj/
├── README.md               # Overall project documentation
├── stylesrules.md          # Design & responsiveness guidelines
├── backend/                # FastAPI backend engine
│   ├── main.py             # API entry point & routes
│   ├── services.py         # Data aggregation & processing
│   ├── technical_service.py # Indicators & Heatmap scoring
│   ├── fundamental_service.py # Finance metrics & health
│   ├── news_service.py     # Live news & sentiment analysis
│   ├── social_sentiment.py # Social data integration
│   ├── nifty50.py          # Nifty 50 constituent data
│   └── requirements.txt    # Backend dependencies
├── frontend/               # Modern web dashboard
│   ├── index.html          # Dashboard layout
│   ├── style.css           # Custom styles & media queries
│   └── script.js           # Dashboard logic & API calls
└── social_media/           # Intelligence scrapers
    ├── scraper.py          # Platform-specific scraping
    └── service.py          # Scraper orchestration
```

## 🏗️ Architecture

### Backend (FastAPI)
- **Modular Services**: Decoupled services for Technicals, Fundamentals, News, and Social Sentiment.
- **Weighted Scoring Engines**: Custom logic to normalize various indicators into easy-to-understand 0-10 and 0-100 scores.
- **Data sanitization**: Robust handling of NumPy/Pandas data types for clean JSON API responses.

### Frontend (Vanilla JS/CSS)
- **Zero Dependencies**: Lightweight and fast, using modern CSS Flexbox/Grid and Vanilla JavaScript.
- **Premium Aesthetics**: Dark-mode primary theme with glassmorphism components and smooth transitions.
- **Responsive Layout**: Adheres to guidelines defined in `stylesrules.md`.

### Social Scrapers
- Python-based scrapers designed to fetch raw content from social platforms for analysis.

## 🛠️ Getting Started

### Backend Setup
1. Navigate to the `backend` folder.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the API:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Simply open `frontend/index.html` in your browser or serve it using a local live server.

## 📖 Design Guidelines
For information on colors, typography, and responsiveness rules, see [stylesrules.md](stylesrules.md).

---
*Built with precision for professional stock analysis.*




2️⃣ Updated Project Structure

I would extend your project like this:

stocks-proj/

backend/
   main.py
   services.py

   technical_service.py
   fundamental_service.py
   news_service.py
   social_sentiment.py

   ai_models/
       lstm_predictor.py
       transformer_model.py
       rl_trader.py
       ensemble.py

frontend/
   index.html
   style.css
   script.js
3️⃣ Data Flow in Your System

You already collect:

technical indicators
news sentiment
social sentiment
fundamentals

Now feed them into AI models.

technical_service
news_service
social_sentiment
      │
      ▼
AI MODELS
      │
      ▼
AI Prediction
4️⃣ LSTM Model (Price Prediction)

File:

backend/ai_models/lstm_predictor.py

Input:

last 60 days OHLCV
RSI
MACD
SMA

Output:

predicted_price
expected_move
signal
confidence

Example API result:

{
 "model": "lstm",
 "predicted_price": 446,
 "expected_move": 3.7,
 "signal": "BUY",
 "confidence": 71
}
5️⃣ Transformer Model (Market Intelligence)

You already have news + tweets + indicators.

This module combines them.

File:

backend/ai_models/transformer_model.py

Input:

news sentiment
tweets sentiment
technical indicators
volume spike
returns

Output:

market sentiment
signal
confidence

Example:

{
 "model": "transformer",
 "news_sentiment": "positive",
 "social_sentiment": "neutral",
 "trend": "bullish",
 "signal": "BUY",
 "confidence": 68
}
6️⃣ Reinforcement Learning Trader

File:

backend/ai_models/rl_trader.py

Input:

RSI
MACD
price momentum
volume spike
news sentiment

Output:

action
expected_return
risk_score

Example:

{
 "model": "rl_agent",
 "action": "HOLD",
 "expected_return": 1.2,
 "risk": "medium",
 "confidence": 63
}
7️⃣ Ensemble Model (Final Decision)

File:

backend/ai_models/ensemble.py

Combine predictions.

Example logic:

BUY = +1
SELL = -1
HOLD = 0

Example:

LSTM = BUY
Transformer = BUY
RL = HOLD

Score:

1 + 1 + 0 = 2

Final:

BUY
Confidence: 74%

## 📂 Current Project Structure (Validated: 2026-03-13 21:16)

```text
stocks-proj/
├── README.md               # Documentation & Project Roadmap
├── stylesrules.md          # UI/UX & Design Guidelines
├── backend/                # FastAPI AI Engine
│   ├── main.py             # API Entry (Technicals, AI, Fundamentals)
│   ├── services.py         # Business logic & Data aggregation
│   ├── technical_service.py # Indicators & Heatmap Logic
│   ├── fundamental_service.py # Company Health Analysis
│   ├── news_service.py     # Live RSS News & VADER Sentiment
│   ├── social_sentiment.py # Social Media data orchestration
│   ├── database.py         # SQLite & SQLAlchemy configuration
│   ├── nifty50.py          # Static Index Data
│   ├── requirements.txt    # ML & Web dependencies
│   ├── test_fast_predictor.py # AI Verification Script
│   ├── ai_models/          # AI Prediction Models
│   │   ├── train_model.py  # Model Training pipeline (LSTM)
│   │   ├── fast_predictor.py # Real-time Prediction inference
│   │   ├── lstm_experiment.py # Experimental AI explorations
│   │   └── saved_model.h5  # Pre-trained LSTM weights
│   └── models/             # Database Schemas
│       └── prediction_store.py # AI Prediction DB model
├── frontend/               # Dashboard UI (Responsive)
│   ├── index.html          # Main Dashboard
│   ├── style.css           # Premium Dark Theme
│   └── script.js           # Live data rendering
└── social_media/           # Intelligence data source
    ├── scraper.py          # Platform Scraping logic
    └── service.py          # Scraper API bridge
```

---
*Documentation updated with AI Infrastructure on Mar 13, 2026.*

Example response:

{
 "final_signal": "BUY",
 "confidence": 74
}
8️⃣ API Endpoint

Add in main.py

/predict/{stock}

Response:

{
 "stock": "COALINDIA",

 "lstm": {
   "signal": "BUY",
   "confidence": 71
 },

 "transformer": {
   "signal": "BUY",
   "confidence": 68
 },

 "rl_agent": {
   "signal": "HOLD",
   "confidence": 63
 },

 "final_signal": "BUY",
 "confidence": 74
}
9️⃣ Frontend UI

Add new section:

AI PREDICTIONS

Example:

AI PREDICTION ENGINE

LSTM MODEL
Signal: BUY
Confidence: 71%

TRANSFORMER MODEL
Signal: BUY
Confidence: 68%

RL TRADING AGENT
Action: HOLD
Confidence: 63%

FINAL AI SIGNAL
BUY
Confidence: 74%# stocks-proj
