import sys
import os
import pandas as pd
import numpy as np

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_models.fast_predictor import predict

symbol = "RELIANCE"
print(f"Running backend predict({symbol})...")
try:
    result = predict(symbol)
    if "error" in result:
        print(f"Predict Error: {result['error']}")
    else:
        print(f"Success! Model: {result['model']}")
        print(f"Signal: {result['signal']}")
        print(f"RSI: {result['rsi']}")
        print(f"Features: {list(result['features'].keys())}")
        print(f"History Length: {len(result['history'])}")
        if result['history']:
            print(f"First item keys: {list(result['history'][0].keys())}")
except Exception as e:
    import traceback
    traceback.print_exc()
