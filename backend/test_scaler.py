import joblib
import os
import numpy as np

base_dir = r"d:\stocks-proj\backend\ai_models\training_db"
scaler_path = os.path.join(base_dir, "INDEX_NSEI_scaler.save")

if os.path.exists(scaler_path):
    scaler = joblib.load(scaler_path)
    print("Scaler type:", type(scaler))
    if hasattr(scaler, "n_features_in_"):
        print("Expected features:", scaler.n_features_in_)
    else:
        # Fallback for very old scikit-learn
        try:
            print("Expected features (min_):", len(scaler.min_))
        except:
            print("Could not determine features")
else:
    print("Scaler not found")
