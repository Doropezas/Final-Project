import pandas as pd
import numpy as np
from pathlib import Path
import yaml

DATA_PATH = Path(__file__).parent.parent.parent / "data"
CONFIG_PATH = Path(__file__).parent.parent.parent / "config"

class FXVolatility:
    def __init__(self):
        self.country_map = self._load_country_mapping()
        self.fx_data = self._load_and_preprocess_data()
    
    def _load_country_mapping(self) -> dict:
        """Map currency codes to country codes"""
        with open(CONFIG_PATH / "countries_regions.yaml") as f:
            countries = yaml.safe_load(f)['regions']
            all_countries = [c for region in countries.values() for c in region['countries']]
        
        # Manual mapping of currency codes to country codes
        return {
            'IDR': 'IDN',  # Indonesia
            'MYR': 'MYS',  # Malaysia
            'THB': 'THA',  # Thailand
            'CNY': 'CHN',  # China
            'INR': 'IND',  # India
            'MXN': 'MEX',  # Mexico
            'BRL': 'BRA',  # Brazil
            'COP': 'COL',  # Colombia
            'CLP': 'CHL',  # Chile
            'PEN': 'PER',  # Peru
            'ZAR': 'ZAF',  # South Africa
            'PLN': 'POL',  # Poland
            'HUF': 'HUN',  # Hungary
            'TRY': 'TUR',  # Turkey
            'CZK': 'CZE',  # Czech Republic
            'EGP': 'EGY',  # Egypt
            'ROU': 'ROU'   # Romania
        }
    
    def _load_and_preprocess_data(self) -> pd.DataFrame:
        """Load all FX CSV files and combine into single DataFrame"""
        fx_files = (DATA_PATH / "raw/fx").rglob("*.csv")
        
        dfs = []
        for file in fx_files:
            try:
                # Extract currency pair from filename
                pair = file.stem.split("_")[0]  
                region = file.parent.name
                
                df = pd.read_csv(file, parse_dates=['date'], index_col='date')
                df['pair'] = pair
                df['region'] = region
                dfs.append(df)
            except Exception as e:
                print(f"Error processing {file.name}: {str(e)}")
                continue
        
        return pd.concat(dfs).sort_index()

    def calculate_volatility(self, window: int = 30) -> pd.DataFrame:
        """Calculate rolling volatility for each currency pair"""
        if self.fx_data.empty:
            raise ValueError("No FX data loaded")
        
        # Calculate daily returns
        returns = self.fx_data.groupby('pair')['4. close'] \
            .transform(lambda x: x.astype(float).pct_change())
        
        # Calculate rolling volatility (annualized)
        volatility = returns.groupby(self.fx_data['pair']) \
            .rolling(window=window) \
            .std() \
            * np.sqrt(252)  # Annualize
        
        # Get latest volatility for each pair
        latest_vol = volatility.reset_index() \
            .groupby('pair')['4. close'] \
            .last() \
            .reset_index() \
            .rename(columns={'4. close': 'volatility'})
        
        # Map to country codes
        latest_vol['country'] = latest_vol['pair'].str[3:].map(self.country_map)
        
        return latest_vol[['country', 'volatility']]

    def save_volatility_data(self, output_file: str = "processed/fx_volatility.parquet"):
        vol_df = self.calculate_volatility()
        output_path = DATA_PATH / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        vol_df.to_parquet(output_path)
        print(f"Saved volatility data to {output_path}")

if __name__ == "__main__":
    calculator = FXVolatility()
    calculator.save_volatility_data()