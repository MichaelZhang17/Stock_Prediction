# Automated Stock Prediction & Trading Strategy Pipeline

## Project Overview

This project provides an end-to-end, one-command workflow that handles data acquisition, cleaning, feature engineering, model training, evaluation, backtesting, visualization, and next-day trade signal generation. It’s designed to help quantitative researchers and algo traders rapidly build, test, and deploy stock prediction strategies.

---

## Key Features

1. **Database Initialization**  
2. **Raw Data Fetching** (supports multiple tickers)  
3. **ETL**: Load CSV data into a SQL database  
4. **Feature Engineering**: Compute RSI, SMA, and other technical indicators  
5. **Data Visualization**: Histograms, time series plots, correlation heatmaps  
6. **Model Training & Hyperparameter Tuning** (Optuna + LightGBM)  
7. **Model Evaluation**: RMSE, direction accuracy, and output to JSON  
8. **Strategy Backtesting**: Daily portfolio NAV, total return, Sharpe, max drawdown  
9. **Backtest Visualization**: Equity curve & drawdown curve  
10. **Signal Generation**: Create BUY/SELL signals based on threshold

---

## Dependencies

- Python 3.8+  
- pandas, numpy, SQLAlchemy  
- scikit-learn, lightgbm, optuna  
- matplotlib, requests
- ...

Install with:
```bash
pip install -r requirements.txt
```
## Project Structure
```arduino
.
├── config.py
├── main.py
├── scripts/
│   ├── create_db.py
│   ├── fetch_data.py
│   ├── etl.py
│   ├── features.py
│   ├── visualize.py
│   ├── train.py
│   ├── evaluate.py
│   ├── visualize_metrics.py
│   ├── threshold_scan.py
│   ├── backtest.py
│   └── visualize_backtest.py
└── reports/
    ├── metrics/            # evaluation_metrics.json
    ├── backtest/           # results.csv (date, nav)
    └── plots/              # all PNG charts
```

- **config.py**: Contains database URL, API keys, and global settings.  
- **main.py**: Single entrypoint to run the full pipeline.  
- **scripts/**: Modular scripts for each step (data fetching, ETL, feature building, visualization, training, evaluation, backtesting).  
- **reports/**: Stores output artifacts—JSON metrics, backtest CSV, and visualization charts.  

## Usage

Run from the project root:

```bash
python main.py \
  --symbols TSLA NVDA NFLX META \
  --trials 75 \
  --threshold 0.015 \
  --capital 250000
```

- `--symbols`: List of ticker symbols to process  
- `--trials`: Number of Optuna hyperparameter trials  
- `--threshold`: BUY/SELL signal threshold  
- `--capital`: Initial capital for backtest  

This command executes the full pipeline in order, from database setup through data fetching, ETL, feature engineering, visualization, training, evaluation, backtesting, and finally next-day signal generation.

## Customization & Extension

- **New Data Sources**  
  Update `scripts/fetch_data.py` and configure API keys in `config.py`.  
- **Feature Engineering**  
  Implement new indicator functions in `scripts/features.py`.  
- **Alternate Models**  
  Modify `scripts/train.py` to swap out LightGBM for other frameworks.  
- **Live Trading Integration**  
  Extend `generate_signals()` in `main.py` to send orders via your broker API.  
- **Report Export**  
  Add PDF/HTML export logic or integrate with Jupyter notebooks.  

