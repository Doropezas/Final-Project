import requests
import yaml
import pandas as pd
from pathlib import Path
import time
from datetime import datetime, timedelta
from urllib.parse import quote_plus

CONFIG_PATH = Path(__file__).parent.parent.parent / "config"
DATA_PATH = Path(__file__).parent.parent.parent / "data/raw/news"

def load_news_config():
    """Load countries and keywords from config"""
    with open(CONFIG_PATH / "news_sources.yaml") as f:
        return yaml.safe_load(f)

def load_api_key(service: str) -> str:
    with open(CONFIG_PATH / "api_keys.yaml") as f:
        return yaml.safe_load(f)['api_keys'][service]

def build_newsapi_query(country: str, keywords: list) -> str:
    """Create NewsAPI query string for a country"""
    base_query = f'("{country}" OR "{country} economy") AND ('
    return base_query + " OR ".join([f'"{kw}"' for kw in keywords]) + ")"

def fetch_newsapi_articles(country: str, keywords: list, api_key: str):
    """Fetch articles from NewsAPI for a country"""
    query = build_newsapi_query(country, keywords)
    url = f"https://newsapi.org/v2/everything?q={quote_plus(query)}&language=en&sortBy=publishedAt&pageSize=100&apiKey={api_key}"
    # Avoid fetching same articules using publishedAt filtering
    # url += f"&from={datetime.now() - timedelta(days=1)}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get('articles', [])
    except Exception as e:
        print(f"NewsAPI error for {country}: {str(e)}")
        return []

def save_articles(articles: list, country: str, region: str):
    """Save articles to region/country folder"""
    if not articles:
        return
    
    region_folder = DATA_PATH / region.replace(" ", "_") / country.replace(" ", "_")
    region_folder.mkdir(parents=True, exist_ok=True)
    
    filename = f"{datetime.now().strftime('%Y%m%d')}.parquet"
    df = pd.DataFrame([{
        'title': a.get('title'),
        'description': a.get('description'),
        'publishedAt': a.get('publishedAt'),
        'source': a.get('source', {}).get('name'),
        'url': a.get('url'),
        'content': a.get('content')[:2000] if a.get('content') else None  # Truncate for storage
    } for a in articles])
    
    df.to_parquet(region_folder / filename)
    print(f"Saved {len(df)} articles for {country}")


def fetch_gdelt_articles(country: str, keywords: list):
    """Fallback to GDELT if NewsAPI limits are hit"""
    query = quote_plus(f'({country}) ({") (".join(keywords)})')
    url = f"https://api.gdeltproject.org/api/v2/doc/doc?query={query}&mode=artlist&format=json"
    
    try:
        response = requests.get(url, timeout=15)
        return response.json().get('articles', [])
    except Exception as e:
        print(f"GDELT error: {str(e)}")
        return []

from bs4 import BeautifulSoup


def main():
    config = load_news_config()
    api_key = load_api_key('newsapi')
    
    for region, countries in config['countries'].items():
        for country in countries:
            print(f"Fetching news for {country}...")
            articles = fetch_newsapi_articles(country, config['news_keywords'], api_key)
            save_articles(articles, country, region)
            time.sleep(3)  # NewsAPI free tier: 100 req/day (~3s between calls)

if __name__ == "__main__":
    main()