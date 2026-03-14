import os
import torch
import torch.nn as nn
import numpy as np
import yfinance as yf
import joblib
from sklearn.preprocessing import MinMaxScaler
from transformer_model import StockTransformer

try:
    from feature_engineer import prepare_multivariate_features
except ImportError:
    import sys
    sys.path.append(os.path.dirname(__file__))
    from feature_engineer import prepare_multivariate_features

BASE_DIR = os.path.dirname(__file__)
TRAIN_DB = os.path.join(BASE_DIR, "training_db")

if not os.path.exists(TRAIN_DB):
    os.makedirs(TRAIN_DB)

LOOKBACK = 60
FEATURES = 20

def train(symbol="RELIANCE.NS"):
    print(f"[Transformer] Training model for {symbol}...")
    
    clean_symbol = symbol.replace("^", "INDEX_")
    model_path = os.path.join(TRAIN_DB, f"{clean_symbol}_transformer.pt")
    scaler_path = os.path.join(TRAIN_DB, f"{clean_symbol}_scaler.save") # Share scaler format or overwrite

    # 1. Fetch Data
    df = yf.download(symbol, period="7y")
    if df.empty:
        print("Error: No data found")
        return

    # 2. Extract 9-features
    data = prepare_multivariate_features(df)
    
    # 3. Scale Data
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(data)

    X, y = [], []
    target_idx = 3 # 'Close' price is index 3 in the 9-feature array

    for i in range(LOOKBACK, len(scaled)):
        X.append(scaled[i-LOOKBACK:i])
        y.append(scaled[i, target_idx])

    X = np.array(X)
    y = np.array(y)

    print(f"X shape: {X.shape}, y shape: {y.shape}")

    # Convert to PyTorch tensors
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32).unsqueeze(1) # shape (batch, 1)

    # 4. Initialize Model
    model = StockTransformer(
        feature_size=FEATURES,
        num_heads=4, # 20 features is divisible by 4
        num_layers=2
    )

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # 5. Training Loop
    epochs = 15 # Match LSTM for fair comparison
    batch_size = 32
    dataset = torch.utils.data.TensorDataset(X_tensor, y_tensor)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=False) # Time series usually shouldn't be shuffled aggressively, but fine for basic batching

    model.train()
    for epoch in range(epochs):
        epoch_loss = 0.0
        for batch_X, batch_y in dataloader:
            optimizer.zero_grad()
            output = model(batch_X)
            loss = criterion(output, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * batch_X.size(0)
        
        avg_loss = epoch_loss / len(dataset)
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.4f}")

    # 6. Save State
    torch.save(model.state_dict(), model_path)
    joblib.dump(scaler, scaler_path)
    print(f"[Transformer] Model trained and saved to {model_path}")

if __name__ == "__main__":
    train()