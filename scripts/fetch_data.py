# scripts/fetch_data.py
import time
import os
import io
import requests
import pandas as pd
import argparse
from config import ALPHA_VANTAGE_API_KEY, BASE_URL

def fetch_data(symbol: str, function: str, interval: str, outputsize: str) -> pd.DataFrame:
    params = {
        "function": function,
        "symbol": symbol,
        "outputsize": outputsize,
        "datatype": "csv",
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    if function == "TIME_SERIES_INTRADAY":
        params["interval"] = interval

    resp = requests.get(BASE_URL, params=params)
    resp.raise_for_status()
    df = pd.read_csv(io.StringIO(resp.text), parse_dates=['timestamp'])
    df.rename(columns={
        'timestamp': 'date',
        'open':      'O',
        'high':      'H',
        'low':       'L',
        'close':     'C',
        'volume':    'V'
    }, inplace=True)
    return df

def main():
    p = argparse.ArgumentParser(description="Fetch OHLCV from Alpha Vantage")
    p.add_argument('-s','--symbols', nargs='+', required=True,
                   help="Stock symbols, e.g. AAPL MSFT GOOG")
    p.add_argument('-f','--function', default="TIME_SERIES_DAILY",
                   choices=["TIME_SERIES_DAILY","TIME_SERIES_INTRADAY",
                            "TIME_SERIES_WEEKLY","TIME_SERIES_MONTHLY"],
                   help="API function")
    p.add_argument('-i','--interval', default="60min",
                   choices=["1min","5min","15min","30min","60min"],
                   help="Required if using INTRADAY")
    p.add_argument('-o','--outputsize', default="full",
                   choices=["compact","full"], help="Compact=100，Full=All")
    p.add_argument('-d','--datadir', default="data/raw",
                   help="Directory to save CSVs")
    args = p.parse_args()

    os.makedirs(args.datadir, exist_ok=True)
    for sym in args.symbols:
        print(f"Fetching {sym} ...")
        df = fetch_data(sym, args.function, args.interval, args.outputsize)
        path = os.path.join(args.datadir, f"{sym}.csv")
        df.to_csv(path, index=False)
        print(f"  → saved {len(df)} rows to {path}")
        time.sleep(12)  # 5 times per minute limit

if __name__ == "__main__":
    main()