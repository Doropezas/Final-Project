import pandas as pd
vol_df = pd.read_parquet("data/processed/fx_volatility.parquet")
print(f"Countries with volatility data: {vol_df['country'].unique()}")