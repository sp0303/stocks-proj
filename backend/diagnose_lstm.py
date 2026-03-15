import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Suppose y_train_true and y_val_true are true targets (unscaled or scaled accordingly)
# and preds_scaled are model outputs (what model returns).

def diagnostics(y_true, preds, scaler_y=None, desc="val"):
    # optionally inverse-transform if scaler provided
    if scaler_y is not None:
        y_true_inv = scaler_y.inverse_transform(y_true.reshape(-1,1)).ravel()
        preds_inv = scaler_y.inverse_transform(preds.reshape(-1,1)).ravel()
    else:
        y_true_inv, preds_inv = y_true.ravel(), preds.ravel()

    print(f"=== Diagnostics ({desc}) ===")
    print("true mean/std:", np.mean(y_true_inv), np.std(y_true_inv))
    print("pred mean/std:", np.mean(preds_inv), np.std(preds_inv))
    print("MAE:", mean_absolute_error(y_true_inv, preds_inv))
    print("RMSE:", mean_squared_error(y_true_inv, preds_inv, squared=False))
    # sample tail check
    diff = preds_inv - y_true_inv
    print("Top 10 prediction diffs (pred - true):")
    print(np.sort(diff)[-10:])
    return y_true_inv, preds_inv, diff