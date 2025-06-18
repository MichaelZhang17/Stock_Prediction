# scripts/backtest.py
import os

import numpy as np
import pandas as pd
import joblib
from sqlalchemy import create_engine
from config import DATABASE_URL


def backtest(threshold=0.0, initial_capital=1_000_000):

    engine = create_engine(DATABASE_URL)
    df = pd.read_sql(
        "SELECT date, symbol, O, H, L, C AS close, V, rsi_14, sma_20 "
        "FROM daily_features ORDER BY date",
        engine, parse_dates=['date']
    )
    df['target'] = df.groupby('symbol')['close'].pct_change().shift(-1)
    df.dropna(inplace=True)

    test = df[df['date'] >= '2025-01-01'].copy()
    X_test = test[['O', 'H', 'L', 'close', 'V', 'rsi_14', 'sma_20']].rename(columns={'close': 'C'})

    model = joblib.load("models/model.pkl")
    test['pred'] = model.predict(X_test)

    test['signal'] = np.where(test['pred'] > threshold, 1,
                              np.where(test['pred'] < -threshold, -1, 0))

    test['ret'] = test.groupby('symbol')['close'].pct_change()
    test['strat_ret'] = test['signal'].shift(1) * test['ret']

    daily = (test
             .groupby('date')[['strat_ret']]
             .mean()
             .sort_index()
             )


    daily['nav'] = (1 + daily['strat_ret']).cumprod() * initial_capital

    total_return = daily['nav'].iloc[-1] / initial_capital - 1
    daily_vol = daily['strat_ret'].std()
    sharpe = (daily['strat_ret'].mean() / daily_vol) * np.sqrt(252)

    print(f"Threshold = {threshold:.3f}")
    print(f"Total return:   {total_return * 100:.1f}%")
    print(f"Annualized Sharpe: {sharpe:.2f}")
    print(f"Max drawdown:   {((daily['nav'].cummax() - daily['nav']) / daily['nav'].cummax()).max() * 100:.1f}%")

    out_dir = os.path.join("reports", "backtest")
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "results.csv")
    daily.reset_index()[['date', 'nav']].to_csv(csv_path, index=False)

    return daily


# if __name__ == "__main__":
#     nav = backtest(threshold=0.0)
