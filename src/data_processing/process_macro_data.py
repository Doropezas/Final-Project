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
    """Process all raw macroeconomic files into a structured format using the most recent value for each indicator."""
    raw_files = (DATA_PATH / "raw/macroeconomic").rglob("*.json")
    country_regions = load_country_mapping()
    
    all_data = []
    for file in raw_files:
        try:
            df = parse_json_file(file)
            if not df.empty:
                # Determine region using the country mapping
                region = next(
                    (r for r, countries in country_regions.items() 
                     if df.iloc[0]['country'] in countries['countries']),
                    None
                )
                if region is None:
                    print(f"Region not found for country {df.iloc[0]['country']} in file {file.name}")
                    continue
                df['region'] = region
                all_data.append(df)
        except Exception as e:
            print(f"Error processing {file.name}: {str(e)}")
            continue
    
    if not all_data:
        print("No data processed.")
        return

    # Combine all raw data into one DataFrame
    combined = pd.concat(all_data, ignore_index=True)
    
    # Convert 'year' to numeric so sorting works as expected
    combined['year'] = pd.to_numeric(combined['year'], errors='coerce')
    
    # Sort descending by year so that the most recent records appear first
    combined.sort_values('year', ascending=False, inplace=True)
    
    # Optionally drop rows with missing values; this ensures we only consider valid indicator values.
    combined = combined.dropna(subset=['value'])
    
    # For each country-region-indicator, keep only the first record (i.e. the most recent)
    latest = combined.groupby(['country', 'region', 'indicator'], as_index=False).first()
    
    # Pivot the table to have one row per country with each indicator as a separate column
    processed = latest.pivot(index=['country', 'region'], columns='indicator', values='value').reset_index()
    
    # Rename columns using World Bank indicator codes to more friendly names
    processed = processed.rename(columns={
        'NY.GDP.MKTP.KD.ZG': 'gdp_growth',
        'FP.CPI.TOTL.ZG': 'inflation',
        'GC.DOD.TOTL.GD.ZS': 'debt_to_gdp',
        'BN.CAB.XOKA.GD.ZS': 'current_account'
    })
    
    # Save the processed data to the output directory
    output_path = DATA_PATH / "processed/macro_indicators.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    processed.to_parquet(output_path)
    print(f"Saved processed data to {output_path}")

if __name__ == "__main__":
    process_macro_data()
