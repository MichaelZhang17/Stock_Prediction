# scripts/test_db.py
import sqlalchemy
from sqlalchemy import text
from config import DATABASE_URL

engine = sqlalchemy.create_engine(DATABASE_URL)
with engine.connect() as conn:
    count = conn.execute(text("SELECT COUNT(*) FROM daily_ohlcv;")).scalar()
    print("Total rows in daily_ohlcv:", count)