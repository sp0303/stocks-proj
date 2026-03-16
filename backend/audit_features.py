import joblib
import os

db_path = r"d:\stocks-proj\backend\ai_models\training_db"
files = [f for f in os.listdir(db_path) if f.endswith("_scaler.save")]

print(f"Checking {len(files)} scalers in {db_path}...")
counts = {}
for f in files[:10]: # Check first 10
    s = joblib.load(os.path.join(db_path, f))
    n = getattr(s, "n_features_in_", "unknown")
    counts[f] = n
    print(f"{f}: {n} features")

# Count distribution
feature_dist = {}
for n in counts.values():
    feature_dist[n] = feature_dist.get(n, 0) + 1
print("\nFeature Distribution (Sample):", feature_dist)
