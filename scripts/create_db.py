# scripts/create_db.py
from sqlalchemy import create_engine, text
from config import DATABASE_URL
engine = create_engine(DATABASE_URL.rsplit('/',1)[0] + '/')
with engine.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS stockdb;"))
    print("Database created or already exists.")