import pandas as pd
import yaml
from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent.parent 

DATA_PATH = PROJECT_ROOT / "data"
CONFIG_PATH = PROJECT_ROOT / "config"

class NewsSentimentProcessor:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.hf_pipeline = pipeline("sentiment-analysis", 
                                   model="finiteautomata/bertweet-base-sentiment-analysis")
        self.country_map = self._load_country_mapping()
    
    def _load_country_mapping(self):
        with open(CONFIG_PATH / "countries_regions.yaml") as f:
            return yaml.safe_load(f)['country_mapping']

    def _load_raw_news(self) -> pd.DataFrame:
        """Load all raw news articles"""
        news_files = (DATA_PATH / "raw/news").rglob("*.parquet")
        dfs = []
        
        for file in news_files:
            try:
                df = pd.read_parquet(file)
                country_name = file.parent.name.replace("_", " ")
                df['country'] = self.country_map.get(country_name, "UNKNOWN")
                dfs.append(df)
            except Exception as e:
                print(f"Error loading {file}: {str(e)}")
                continue
                
        return pd.concat(dfs).reset_index(drop=True)
    
    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score using hybrid approach"""
        try:
            # First pass with VADER
            vader_score = self.analyzer.polarity_scores(text)['compound']
            
            # Second pass with Hugging Face if neutral
            if -0.5 < vader_score < 0.5:
                hf_result = self.hf_pipeline(text[:512])  # Truncate to 512 tokens
                return hf_result[0]['score'] * (1 if hf_result[0]['label'] == 'POS' else -1)
            return vader_score
        except:
            return np.nan
    
    def process_sentiment(self):
        """Main processing workflow"""
        news_df = self._load_raw_news()
        
        # Calculate sentiment scores
        news_df['sentiment'] = news_df['content'].fillna('').apply(self._calculate_sentiment)
        
        # Aggregate by country and date
        news_df['date'] = pd.to_datetime(news_df['publishedAt']).dt.date
        aggregated = news_df.groupby(['country']).agg(
            avg_sentiment=('sentiment', 'mean'),
            article_count=('sentiment', 'count')
        ).reset_index()
        

        # Save processed data
        output_path = DATA_PATH / "processed/news_sentiment.parquet"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        aggregated.to_parquet(output_path)
        print(f"Saved sentiment data to {output_path}")

if __name__ == "__main__":
    processor = NewsSentimentProcessor()
    processor.process_sentiment()