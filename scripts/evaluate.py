# scripts/evaluate.py
import json
import os

import numpy as np
import pandas as pd
import joblib
from sqlalchemy import create_engine
from sklearn.metrics import mean_squared_error, accuracy_score
from config import DATABASE_URL

def evaluate():
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql(
        "SELECT * FROM daily_features ORDER BY date",
        engine, parse_dates=['date']
    )

    df['target'] = df.groupby('symbol')['C'].pct_change().shift(-1)
    df.dropna(inplace=True)


    test_mask = df['date'] >= '2025-01-01'
    X_test = df.loc[test_mask, ['O','H','L','C','V','rsi_14','sma_20']]
    y_test = df.loc[test_mask, 'target'].values


    y_base = np.zeros_like(y_test)
    rmse_base = np.sqrt(mean_squared_error(y_test, y_base))


    model = joblib.load("models/model.pkl")
    y_pred = model.predict(X_test)
    rmse_model = np.sqrt(mean_squared_error(y_test, y_pred))

    # 5) 方向准确率
    direction_acc = accuracy_score(y_test > 0, y_pred > 0)

    print(f"Baseline RMSE: {rmse_base:.4f}")
    print(f" Model   RMSE: {rmse_model:.4f}")
    print(f"Direction Accuracy: {direction_acc:.4f}")
    metrics = {
        "baseline_rmse": rmse_base,
        "model_rmse": rmse_model,
        "direction_accuracy": direction_acc
    }

    out_dir = os.path.join("reports", "metrics")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "evaluation_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

# if __name__ == "__main__":
#     evaluate()
