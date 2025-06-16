# scripts/evaluate.py

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

if __name__ == "__main__":
    evaluate()
