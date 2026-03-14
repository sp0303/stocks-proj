# Stock Intelligence Dashboard 📈

A sophisticated AI-driven stock analysis platform that combines **Deep Learning (LSTM)**, **Transformer Networks**, and **Real-Time Sentiment Analysis** to provide professional-grade market insights for the NIFTY 50.

---

## 🧠 Core Intelligence Architecture: The "Dual-Brain" System

The platform operates on a redundant AI architecture where every stock is analyzed by two distinct neural networks to ensure signals are robust and validated.

### 1. Multivariate LSTM (TensorFlow)
*   **Role**: Sequential Trend Analysis.
*   **Architecture**: Multi-layered Long Short-Term Memory network.
*   **Focus**: Capturing long-term temporal dependencies and "smooth" price trends.
*   **Feature Set**: 9-dimensional input vector (OHLCV + RSI + MACD + SMA20 + SMA50).

### 2. PyTorch StockTransformer
*   **Role**: Pattern Recognition & Volatility Attention.
*   **Architecture**: Attention-based Transformer with **Learned Positional Encoding**.
*   **Focus**: Identifying non-linear patterns and "attention spikes" in market data.
*   **Advanced Logic**: Uses dropout regularization and positional embeddings to understand the 60-day window context.

### 3. The Consensus Engine
To prevent false positives, the backend implements a **Reconciliation Layer**:
*   ✅ **High Confidence**: Both models agree on a signal.
*   ⚠️ **Conflict (Divergent)**: Models disagree (e.g., LSTM says SELL while Transformer says BUY). These are flagged in the UI as High Uncertainty.
*   **Volatility-Adjusted**: Signal thresholds are not static; they scale dynamically based on the stock's 60-day price standard deviation.

---

## 📂 Project Structure

```text
stocks-proj/
├── backend/                    # FastAPI AI Engine
│   ├── main.py                 # API Layer & Routes
│   ├── services.py             # Indices & Market Data Orchestration
│   ├── nifty50.py              # Constituent Data
│   ├── technical_service.py    # Traditional Technical Analysis
│   ├── fundamental_service.py  # Company Health Metrics
│   ├── news_service.py         # Live News Sentiment Analysis
│   ├── ai_models/              # AI Subsystem
│   │   ├── training_db/        # Local Database for .pt and .h5 models
│   │   ├── transformer_model.py # PyTorch Transformer Definition
│   │   ├── train_model.py      # LSTM Training Script
│   │   ├── train_transformer.py # Transformer Training Script
│   │   ├── fast_predictor.py   # LSTM Inference Engine
│   │   ├── transformer_predict.py # Transformer Inference Engine
│   │   └── feature_engineer.py # Shared Technical Indicator Math
│   └── requirements.txt        # TF, Torch, YFinance, etc.
├── frontend/                   # Modern Web Interface
│   ├── index.html              # Main Dashboard
│   ├── lstm_index.html         # Detailed AI Analytics Page
│   ├── style.css               # Glassmorphic Dark-Mode UI
│   └── script.js               # Frontend Controller
└── social_media/               # External Intelligence
    ├── scraper.py              # Social Scraping Logic
    └── service.py              # Scraper API Bridge
```

---

## 🔄 Logical Flow

1.  **Ingestion**: `yfinance` fetches 7 years of daily historical data.
2.  **Feature Engineering**: Data is passed through `feature_engineer.py` to calculate RSI, MACD, and SMAs, creating a 9-feature matrix.
3.  **Scaling**: `MinMaxScaler` normalizes data per-stock to handle different price magnitudes (e.g., RELIANCE vs MRF).
4.  **Training**: 
    *   Models look at slices of **60 days** to predict the **61st day's Close price**.
    *   Training runs for 15-20 epochs with MSE loss.
5.  **Inference**:
    *   The API fetches the latest 60 days of data.
    *   Both models run live predictions.
    *   Results are reconciled via the **Consensus logic**.
6.  **Visualization**:
    *   `script.js` calls `/ai/consensus/` and `/ai/transformer/`.
    *   Predictions are plotted on **Chart.js** canvases in the frontend.

---

## 🛠️ How to Train Models

### Prerequisites
Ensure you have the backend environment active and all dependencies installed.

### Batch Training (Full NIFTY 50)
The system includes automation scripts to train all 50 stocks + the Index baseline at once.

**1. Train LSTM Models (TensorFlow):**
```powershell
# From the backend directory
python ai_models/train_all.py
```

**2. Train Transformer Models (PyTorch):**
```powershell
# Standard run (resumes where it left off)
python ai_models/train_transformer_all.py

# Forced re-train (necessary if architecture changes)
python ai_models/train_transformer_all.py --force
```

### Individual Training
```powershell
python ai_models/train_transformer.py --symbol RELIANCE.NS
```

---

## 🚀 Deployment & Running

1. **Start Backend**:
   ```bash
   uvicorn main:app --port 8000 --reload
   ```
2. **Start Social Service** (Optional):
   ```bash
   python service.py
   ```
3. **Open Frontend**:
   Serve the `frontend/` directory or open `index.html` directly.

---
*Powered by DeepMind-inspired architectures for the Indian Stock Market.*
