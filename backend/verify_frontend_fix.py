import requests

API = "http://127.0.0.1:8000"
symbol = "RELIANCE"

print(f"Testing LSTM endpoint for {symbol}...")
try:
    res = requests.get(f"{API}/ai/lstm/{symbol}")
    data = res.json()
    
    important_keys = ["rsi", "macd", "sma20", "sma50", "features"]
    for key in important_keys:
        val = data.get(key)
        print(f"  {key}: {val} ({'PASS' if val is not None else 'FAIL'})")
    
    if "features" in data:
        print(f"  Total features in 'features' key: {len(data['features'])}")

except Exception as e:
    print(f"Error: {e}")

print(f"\nTesting Transformer endpoint for {symbol}...")
try:
    res = requests.get(f"{API}/ai/transformer/{symbol}")
    data = res.json()
    
    for key in important_keys:
        val = data.get(key)
        print(f"  {key}: {val} ({'PASS' if val is not None else 'FAIL'})")

except Exception as e:
    print(f"Error: {e}")
