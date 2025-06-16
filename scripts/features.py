# scripts/features.py
import pandas as pd
from sqlalchemy import create_engine, text
from config import DATABASE_URL
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator

def build_features():
    engine = create_engine(DATABASE_URL, echo=False)

    df = pd.read_sql("SELECT * FROM daily_ohlcv", engine, parse_dates=['date'])

    df.sort_values(['symbol', 'date'], inplace=True)

    df['rsi_14'] = df.groupby('symbol').apply(
        lambda grp: RSIIndicator(close=grp['C'], window=14).rsi()
    ).reset_index(level=0, drop=True)

    df['sma_20'] = df.groupby('symbol').apply(
        lambda grp: SMAIndicator(close=grp['C'], window=20).sma_indicator()
    ).reset_index(level=0, drop=True)

    df.to_sql('daily_features', engine, if_exists='replace', index=False)
    print("✔ daily_features table created with columns:")
    print("  ", df.columns.tolist())

    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE daily_features ADD INDEX idx_feat_sym_date (symbol(16), date);"))

if __name__ == "__main__":
    build_features()
