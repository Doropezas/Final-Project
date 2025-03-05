import json
import pandas as pd
from pathlib import Path
import yaml

DATA_PATH = Path(__file__).parent.parent.parent / "data"
CONFIG_PATH = Path(__file__).parent.parent.parent / "config"

def load_country_mapping() -> dict:
    """Map World Bank country codes to country names"""
    with open(CONFIG_PATH / "countries_regions.yaml") as f:
        return yaml.safe_load(f)['regions']

def parse_json_file(file_path: Path) -> pd.DataFrame:
    """Parse a single World Bank JSON file"""
    with open(file_path) as f:
        data = json.load(f)
    
    if len(data) < 2 or not data[1]:
        return pd.DataFrame()
    
    return pd.DataFrame([{
        'country': item['countryiso3code'],
        'indicator': item['indicator']['id'],
        'year': item['date'],
        'value': item['value']
    } for item in data[1]])

def process_macro_data():
    """Process all raw macroeconomic files into structured format"""
    raw_files = (DATA_PATH / "raw/macroeconomic").rglob("*.json")
    country_regions = load_country_mapping()
    
    all_data = []
    for file in raw_files:
        try:
            df = parse_json_file(file)
            if not df.empty:
                # Add region information
                region = next(
                    r for r, countries in country_regions.items() 
                    if df.iloc[0]['country'] in countries['countries']
                )
                df['region'] = region
                all_data.append(df)
        except Exception as e:
            print(f"Error processing {file.name}: {str(e)}")
            continue
    
    combined = pd.concat(all_data)
    
    # Pivot to wide format (one row per country-year)
    processed = combined.pivot_table(
        index=['country', 'region', 'year'],
        columns='indicator',
        values='value',
        aggfunc='first'
    ).reset_index()
    
    # Rename columns using World Bank indicator codes
    processed.columns.name = None
    processed = processed.rename(columns={
        'NY.GDP.MKTP.KD.ZG': 'gdp_growth',
        'FP.CPI.TOTL.ZG': 'inflation',
        'GC.DOD.TOTL.GD.ZS': 'debt_to_gdp',
        'BN.CAB.XOKA.GD.ZS': 'current_account'
    })
    
    # Save to processed directory
    output_path = DATA_PATH / "processed/macro_indicators.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    processed.to_parquet(output_path)
    print(f"Saved processed data to {output_path}")

if __name__ == "__main__":
    process_macro_data()