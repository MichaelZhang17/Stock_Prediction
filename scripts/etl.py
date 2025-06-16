# scripts/etl.py
import os
import pandas as pd
from sqlalchemy import create_engine, text
from config import DATABASE_URL

def load_raw_to_db(raw_folder="data/raw"):
    engine = create_engine(DATABASE_URL, echo=False)
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE daily_ohlcv;"))

    for fname in os.listdir(raw_folder):
        if not fname.lower().endswith(".csv"):
            continue
        symbol = fname.replace(".csv", "")
        path = os.path.join(raw_folder, fname)

        df = pd.read_csv(path, parse_dates=['date'])
        df['symbol'] = symbol

        df.to_sql("daily_ohlcv", engine,
                  if_exists="append",
                  index=False,
                  chunksize=500)
        print(f"✔ Inserted {len(df)} rows for {symbol}")

    check_sql = """
                SELECT COUNT(*)
                FROM information_schema.STATISTICS
                WHERE table_schema = DATABASE()
                  AND table_name = 'daily_ohlcv'
                  AND index_name = 'idx_symbol_date'; \
                """

    with engine.connect() as conn:
        exists = conn.execute(text(check_sql)).scalar()
        if not exists:
            conn.execute(text("""
                              ALTER TABLE daily_ohlcv
                                  ADD INDEX idx_symbol_date (symbol(16), date);
                              """))
            print("Index idx_symbol_date created.")
        else:
            print("Index already exists, skipping.")

if __name__ == "__main__":
    load_raw_to_db()
