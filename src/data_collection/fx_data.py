import yfinance as yf
import yaml
import pandas as pd
from pathlib import Path
import time
import sys

CONFIG_PATH = Path(__file__).parent.parent.parent / "config"
DATA_PATH = Path(__file__).parent.parent.parent / "data/raw/fx"

def load_fx_config() -> dict:
    """Load FX pairs configuration from YAML file"""
    with open(CONFIG_PATH / "fx_pairs.yaml") as f:
        return yaml.safe_load(f)['fx_pairs']


def fetch_save_fx_rates():
    """Fetch and store FX rates using yfinance for the last three months"""
    fx_config = load_fx_config()
    
    for region, pairs in fx_config.items():
        region_path = DATA_PATH / region.replace(" ", "_")
        region_path.mkdir(parents=True, exist_ok=True)
        
        for pair in pairs:
            try:
                # Construct the yfinance ticker (e.g., "EURUSD=X")
                ticker = f"{pair}=X"
                # Download three months of historical daily data
                data = yf.download(ticker, period='1Y', interval='1d')
                if data.empty:
                    print(f"No data found for {pair}")
                    continue
                
                # Clean the data to remove extra header rows and adjust columns
                if isinstance(data.columns, pd.MultiIndex):
                    # Here we take the first level of the column names.
                    data.columns = data.columns.get_level_values(0)

                filename = f"{pair}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv"
                data.to_csv(region_path / filename)
                print(f"Saved {pair} data to {filename}")
                
                
            except Exception as e:
                print(f"Failed to fetch {pair}: {str(e)}")
                continue

def main():
    print("Starting FX data collection using yfinance...")
    fetch_save_fx_rates()
    print("FX data collection completed!")

if __name__ == "__main__":
    main()
