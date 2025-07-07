# AlphaQuant: an Automated Stock Prediction & Trading Strategy Pipeline

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
11. 
---

## Creating Your `config.py`

In your project root, create a file named `config.py` with the following three constants:

```python
import os

# 1. Database connection URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/your_db")

# 2. Alpha Vantage API key
ALPHA_API_KEY = os.getenv("ALPHA_API_KEY", "")

# 3. Alpha Vantage base URL
ALPHA_BASE_URL = os.getenv("ALPHA_BASE_URL", "https://www.alphavantage.co")
```

DATABASE_URL: Points your code to where price and feature data are stored.

ALPHA_API_KEY: Grants access to Alpha Vantage’s market data API.

ALPHA_BASE_URL: Lets you switch between endpoints or staging servers if needed.

With just a valid database connection and your Alpha Vantage API key (plus the base URL), you have everything you need to fetch price data, compute features, and run your model end to end.


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
# Stock Prediction Pipeline Workflow

Below is the end-to-end workflow for the **Stock_Prediction** project, laid out as a sequence of discrete steps.

1. **Configure Environment**  
   - Create `config.py` with three constants:  
     ```python
     DATABASE_URL     # your database connection string  
     ALPHA_API_KEY    # your Alpha Vantage API key  
     ALPHA_BASE_URL   # Alpha Vantage endpoint URL  
     ```
   - Ensure these are loaded from environment variables to keep credentials out of version control.

2. **Initialize Database**  
   - Run `scripts/create_db.py` to create the PostgreSQL schema.  
   - Tables include raw price storage, feature tables, and results tables.

3. **Fetch Raw Market Data**  
   - Execute `scripts/fetch_data.py`.  
   - For each symbol in your list, pull time-series data from Alpha Vantage and write CSV files to disk.

4. **Load Data into SQL (ETL)**  
   - Run `scripts/etl.py` to ingest the downloaded CSVs into your database tables.  
   - Centralizes all historic price data for downstream processing.

5. **Compute Features**  
   - Launch `scripts/features.py`.  
   - Calculate technical indicators (e.g. SMA, EMA, RSI) and write feature vectors back into SQL.

6. **Visualize Data & Features**  
   - Use `scripts/visualize.py` to generate exploratory plots (time-series charts, histograms, correlation heatmaps).  
   - Inspect and validate feature distributions.

7. **Model Training & Hyperparameter Tuning**  
   - Run `scripts/train.py` with LightGBM + Optuna:  
     - Specify number of trials, early-stopping criteria, etc.  
   - The script saves the best model object and its evaluation metrics (RMSE, accuracy) to JSON.

8. **Evaluate Model Performance**  
   - Execute `scripts/evaluate.py`.  
   - Load the saved metrics JSON and print or tabulate results (e.g. validation vs. test performance).

9. **Backtest Strategy**  
   - Run `scripts/backtest.py`.  
   - Simulate daily portfolio returns, compute performance statistics (Sharpe ratio, max drawdown, total return).  
   - Output daily NAV series as a CSV.

10. **Backtest Visualization**  
    - Use `scripts/visualize_backtest.py` to plot:  
      - Equity curve  
      - Drawdown curve  
    - Quickly assess risk-return characteristics visually.

11. **Generate Live Signals**  
    - Finally, run the orchestrator `main.py`:  
      ```bash
      python main.py \
        --symbols TSLA NVDA NFLX META \
        --trials 75 \
        --threshold 0.015 \
        --capital 250000
      ```  
    - This single command covers steps 3–10 and produces next-day BUY/SELL signals in JSON or console output.

---

Each step is modular and lives under the `scripts/` directory; all reports and charts are stored in `reports/`. You can run any step independently for debugging or re-running specific stages without re-processing the entire pipeline.



