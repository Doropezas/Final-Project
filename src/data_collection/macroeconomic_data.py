# src/data_collection/macroeconomic_data.py
import requests
import yaml
import pandas as pd
from pathlib import Path
import time
from datetime import datetime
import json

CONFIG_PATH = Path(__file__).parent.parent.parent / "config"
DATA_PATH = Path(__file__).parent.parent.parent / "data/raw/macroeconomic"

def load_config(file: str) -> dict:
    with open(CONFIG_PATH / file) as f:
        return yaml.safe_load(f)

def fetch_country_indicator(country: str, indicator: str) -> dict:
    """Fetch single indicator for a country"""
    url = f"http://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {indicator} for {country}: {str(e)}")
        return None

def save_data(data: dict, country: str, indicator: str):
    """Save raw JSON response with timestamp"""
    if not data or len(data) < 2:
        return
        
    region_config = load_config("countries_regions.yaml")
    for region, countries in region_config["regions"].items():
        if country in countries["countries"]:
            region_folder = region.replace(" ", "_")
            break
    
    file_path = DATA_PATH / region_folder / f"{country}_{indicator}_{datetime.now().strftime('%Y%m%d')}.json"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, "w") as f:
        json.dump(data, f)
    print(f"Saved {indicator} for {country} to {file_path}")

def main():
    print("Starting macroeconomic data collection...")
    indicators_config = load_config("indicators.yaml")
    
    for category, indicators in indicators_config["indicators"].items():
        print(f"\nFetching {category} indicators:")
        for indicator in indicators:
            countries_config = load_config("countries_regions.yaml")
            for region, countries in countries_config["regions"].items():
                for country in countries["countries"]:
                    data = fetch_country_indicator(country, indicator)
                    if data:
                        save_data(data, country, indicator)
                    time.sleep(1)  # Respect API rate limits

if __name__ == "__main__":
    main()