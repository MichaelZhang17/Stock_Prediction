#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import joblib
import pandas as pd
from sqlalchemy import create_engine

from scripts.etl import load_raw_to_db
from scripts.features import build_features
from scripts.evaluate import evaluate as evaluate_model
from scripts.backtest import backtest as run_backtest
from config import DATABASE_URL
import scripts.train as train

def run_subprocess(script_name, args=None):
    root_dir = os.path.dirname(__file__)
    scripts_dir = os.path.join(root_dir, 'scripts')
    candidate = os.path.join(scripts_dir, script_name)
    if os.path.isfile(candidate):
        script_path = candidate
    else:
        candidate = os.path.join(root_dir, script_name)
        if os.path.isfile(candidate):
            script_path = candidate
        else:
            raise FileNotFoundError(f"Script not found in scripts/ or root: {script_name}")

    env = os.environ.copy()
    env['PYTHONPATH'] = root_dir + os.pathsep + env.get('PYTHONPATH', '')

    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    subprocess.run(cmd, check=True, env=env)


def generate_signals(model_path, threshold, output_path="data/results/signals.csv"):
    """
    Load the trained model, fetch the latest features from DB, predict next-day returns,
    and emit buy/sell signals based on threshold.
    """
    engine = create_engine(DATABASE_URL)
    df_feat = pd.read_sql_table('daily_features', engine, parse_dates=['date'])
    latest = df_feat.sort_values('date').groupby('symbol').tail(1)

    model = joblib.load(model_path)
    feature_cols = [c for c in latest.columns if c not in ['symbol', 'date']]
    X_pred = latest[feature_cols].values
    preds = model.predict(X_pred)

    signals = pd.DataFrame({
        'symbol': latest['symbol'],
        'date': latest['date'],
        'prediction': preds,
        'signal': ['BUY' if p > threshold else 'SELL' for p in preds]
    })
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    signals.to_csv(output_path, index=False)
    print(f"Signals written to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Run full stock-prediction workflow.")
    parser.add_argument('--symbols', '-s', nargs='+', default=None,
                        help="List of ticker symbols to fetch (e.g. AAPL MSFT). If omitted, skips fetching.")
    parser.add_argument('--function', '-f', default='TIME_SERIES_DAILY',
                        help="Alpha Vantage function to use for fetch_data.")
    parser.add_argument('--interval', '-i', default='60min',
                        help="Data interval (for intraday endpoints).")
    parser.add_argument('--outputsize', '-o', default='full',
                        help="Output size (compact/full).")
    parser.add_argument('--datadir', '-d', default='data/raw',
                        help="Directory to store raw CSVs.")
    parser.add_argument('--trials', type=int, default=50,
                        help="Number of Optuna trials for hyperparameter search.")
    parser.add_argument('--threshold', type=float, default=0.0,
                        help="Threshold for generating BUY/SELL signals.")
    parser.add_argument('--capital', type=float, default=1_000_000,
                        help="Initial capital for backtest.")
    args = parser.parse_args()

    print("==> Creating database...")
    run_subprocess('create_db.py')

    if args.symbols:
        print("==> Fetching raw data...")
        fetch_args = ['-s'] + args.symbols + ['-f', args.function,
                        '-i', args.interval, '-o', args.outputsize,
                        '-d', args.datadir]
        run_subprocess('fetch_data.py', fetch_args)

    print("==> ETL into database...")
    load_raw_to_db(raw_folder=args.datadir)

    print("==> Building features...")
    build_features()

    print("==> Visualizing data...")
    run_subprocess('visualize.py')

    print(f"==> Training model ({args.trials} trials) and saving...")
    train.train_and_save(trials=args.trials, model_path=os.path.join('models', 'model.pkl'))

    print("==> Evaluating model...")
    evaluate_model()

    print("==> Visualizing evaluation metrics...")
    run_subprocess('visualize_metrics.py')

    print("==> Scanning thresholds...")
    run_subprocess('threshold_scan.py')

    print(f"==> Backtesting with threshold={args.threshold} and capital={args.capital}...")
    run_backtest(threshold=args.threshold, initial_capital=args.capital)

    print("==> Generating next-day BUY/SELL signals...")
    generate_signals(model_path=os.path.join('models', 'model.pkl'), threshold=args.threshold)
    print("Workflow complete.")


if __name__ == '__main__':
    main()
