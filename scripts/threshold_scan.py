#scripts/threshold_scan.py
import pandas as pd
from scripts.backtest import backtest

thresholds = [0, 0.001, 0.002, 0.005, 0.01]
rows = []
for thr in thresholds:
    daily = backtest(threshold=thr)
    total = daily['nav'].iloc[-1]/daily['nav'].iloc[0] - 1
    ret = daily['strat_ret']
    sharpe = (ret.mean()/ret.std())*(252**0.5)
    mdd = ((daily['nav'].cummax()-daily['nav'])/daily['nav'].cummax()).max()
    rows.append({'threshold':thr, 'return':total, 'sharpe':sharpe, 'max_dd':mdd})
df = pd.DataFrame(rows)
df.to_csv('data/results/threshold_results.csv', index=False)