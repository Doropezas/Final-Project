import pandas as pd
from pathlib import Path

# Check macro data
macro_path = Path("data/processed/macro_indicators.parquet")
if macro_path.exists():
    macro = pd.read_parquet(macro_path)
    print("Macro Data Columns:", macro.columns.tolist())
    print("GDP Sample Values:\n", macro[['country', 'gdp_growth']].dropna().head())
else:
    print("Macro data file missing!")

# Check FX volatility
fx_vol_path = Path("data/processed/fx_volatility.parquet")
if fx_vol_path.exists():
    fx_vol = pd.read_parquet(fx_vol_path)
    print("\nFX Volatility Data:\n", fx_vol.head())
else:
    print("FX volatility file missing!")

# Check news sentiment
sentiment_path = Path("data/processed/news_sentiment.parquet")
if sentiment_path.exists():
    sentiment = pd.read_parquet(sentiment_path)
    print("\nSentiment Data:\n", sentiment.head())
else:
    print("News sentiment file missing!")