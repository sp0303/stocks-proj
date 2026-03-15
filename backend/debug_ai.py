from ai_models.fast_predictor import predict_detailed
import json
import traceback

try:
    res = predict_detailed("RELIANCE")
    print(json.dumps(res, indent=2))
except Exception:
    traceback.print_exc()
