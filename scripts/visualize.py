#!/usr/bin/env python3
import os
from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt
from config import DATABASE_URL

def main():
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql_table('daily_features', engine, parse_dates=['date'])

    # Ensure output directory exists
    out_dir = os.path.join('results', 'plots')
    os.makedirs(out_dir, exist_ok=True)

    # 1. Close price distribution
    plt.figure()
    df['C'].hist(bins=50)
    plt.title('Close Price Distribution')
    plt.xlabel('Close Price')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'close_price_distribution.png'))
    plt.close()

    # 2. Volume distribution
    plt.figure()
    df['V'].hist(bins=50)
    plt.title('Volume Distribution')
    plt.xlabel('Volume')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'volume_distribution.png'))
    plt.close()

    # 3. RSI over time
    plt.figure()
    for symbol, group in df.groupby('symbol'):
        plt.plot(group['date'], group['rsi_14'], label=symbol)
    plt.title('RSI 14 Over Time')
    plt.xlabel('Date')
    plt.ylabel('RSI 14')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'rsi_over_time.png'))
    plt.close()

    # 4. Correlation heatmap
    plt.figure()
    features = ['O','H','L','C','V','rsi_14','sma_20']
    corr = df[features].corr()
    im = plt.imshow(corr, interpolation='nearest', aspect='auto')
    plt.colorbar(im)
    plt.xticks(range(len(features)), features, rotation=45)
    plt.yticks(range(len(features)), features)
    plt.title('Feature Correlation Heatmap')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'correlation_heatmap.png'))
    plt.close()

    print(f"Plots saved to {out_dir}")
