from alpha_vantage.foreignexchange import ForeignExchange
import yaml
import pandas as pd
from pathlib import Path
import time
import sys

CONFIG_PATH = Path(__file__).parent.parent.parent / "config"
DATA_PATH = Path(__file__).parent.parent.parent / "data/raw/fx"

def load_api_keys() -> dict:
    """Load API keys from YAML file"""
    try:
        with open(CONFIG_PATH / "api_keys.yaml") as f:
            return yaml.safe_load(f)['api_keys']
    except FileNotFoundError:
        print("Error: api_keys.yaml not found in config directory!")
        sys.exit(1)
    except KeyError:
        print("Error: 'api_keys' section missing in YAML file!")
        sys.exit(1)

def load_fx_config() -> dict:
    """Load FX pairs configuration"""
    with open(CONFIG_PATH / "fx_pairs.yaml") as f:
        return yaml.safe_load(f)['fx_pairs']

def fetch_save_fx_rates():
    """Fetch and store FX rates using API key from config"""
    api_keys = load_api_keys()
    fx_config = load_fx_config()
    
    try:
        # Use pandas output for easier filtering
        fx = ForeignExchange(key=api_keys['alpha_vantage'], output_format='pandas')
    except KeyError:
        print("Error: alpha_vantage key missing in api_keys.yaml!")
        sys.exit(1)

    for region, pairs in fx_config.items():
        region_path = DATA_PATH / region.replace(" ", "_")
        region_path.mkdir(parents=True, exist_ok=True)
        
        for pair in pairs:
            try:
                # Fetch daily FX historical data
                data, meta_data = fx.get_currency_exchange_daily(
                    from_symbol=pair[:3], 
                    to_symbol=pair[3:],
                    outputsize='full'
                )
                # Filter data for the last three months
                three_months_ago = pd.Timestamp.now() - pd.DateOffset(months=3)
                filtered_data = data[data.index >= three_months_ago.strftime('%Y-%m-%d')]
                
                filename = f"{pair}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv"
                filtered_data.to_csv(region_path / filename)
                print(f"Saved {pair} data to {filename}")
                
                # Respect AlphaVantage's rate limit
                time.sleep(12)  # 5 calls per minute
                
            except Exception as e:
                print(f"Failed to fetch {pair}: {str(e)}")
                continue

def main():
    print("Starting FX data collection...")
    fetch_save_fx_rates()
    print("FX data collection completed!")

if __name__ == "__main__":
    main()
