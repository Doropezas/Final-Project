import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
import yaml

PROJECT_ROOT = Path(__file__).parent.parent.parent 

DATA_PATH = PROJECT_ROOT / "data"
CONFIG_PATH = PROJECT_ROOT / "config"

class RiskAssessor:
    def __init__(self):
        self.countries = self._load_country_list()
        self.weights = {
            'gdp_growth': 0.10,
            'inflation': 0.25,
            'fx_volatility': 0.10,
            'drawdown':0.10,
            'var':0.05,
            'arima_forecast': 0.025,
            'prophet_forecast': 0.025,
            'debt_to_gdp': 0.20,
            'current_account': 0.10,
            'sentiment': 0.10
        }
    
    def _load_country_list(self):
        """Load countries from config"""
        with open(Path(__file__).parent.parent.parent / "config/countries_regions.yaml") as f:
            config = yaml.safe_load(f)
            return [c for region in config['regions'].values() for c in region['countries']]

    def _load_macro_data(self):
        """Load processed macroeconomic data"""
        return pd.read_parquet(DATA_PATH / "processed/macro_indicators.parquet")

    def _load_fx_volatility(self):
        """Load 30-day FX volatility"""
        return pd.read_parquet(DATA_PATH / "processed/fx_volatility.parquet")

    def _load_sentiment_scores(self):
        """Load news sentiment data"""
        return pd.read_parquet(DATA_PATH / "processed/news_sentiment.parquet")

    def calculate_scores(self):
        # Load data from all sources
        macro = self._load_macro_data()
        fx_vol = self._load_fx_volatility()
        sentiment = self._load_sentiment_scores()
        
        # Merge datasets
        combined = macro.merge(fx_vol, on='country').merge(sentiment, on='country')
        
        # Normalize indicators (higher = better except for inflation/debt)
        scaler = MinMaxScaler(feature_range=(0,100))
        combined['gdp_score'] = scaler.fit_transform(combined[['gdp_growth']])
        combined['inflation_score'] = 100 - scaler.fit_transform(combined[['inflation']])
        combined['debt_score'] = 100 - scaler.fit_transform(combined[['debt_to_gdp']])
        combined['fx_score'] = 100 - scaler.fit_transform(combined[['volatility']])
        combined['drawdown_score'] = 100 - scaler.fit_transform(combined[['drawdown']])
        combined['var_score'] = 100 - scaler.fit_transform(combined[['var']])
        combined['arima_score'] = scaler.fit_transform(combined[['arima_forecast']])
        combined['prophet_score'] = scaler.fit_transform(combined[['prophet_forecast']])
        combined['current_account_score'] = scaler.fit_transform(combined[['current_account']])
        combined['sentiment_score'] = scaler.fit_transform(combined[['avg_sentiment']])

        combined['debt_score'] = combined['debt_score'].fillna(0)

        # Calculate weighted risk score
        combined['risk_score'] = (
            combined['gdp_score'] * self.weights['gdp_growth'] +
            combined['inflation_score'] * self.weights['inflation'] +
            combined['fx_score'] * self.weights['fx_volatility'] +
            combined['drawdown_score'] * self.weights['drawdown'] +
            combined['var_score'] * self.weights['var'] +
            combined['arima_score'] * self.weights['arima_forecast'] +
            combined['prophet_score'] * self.weights['prophet_forecast'] +
            combined['debt_score'] * self.weights['debt_to_gdp'] +
            combined['current_account_score'] * self.weights['current_account'] +
            combined['sentiment_score'] * self.weights['sentiment']
        )

        

        return combined.sort_values('risk_score', ascending=False)[[
            'country', 'region', 'risk_score', 'gdp_score', 'inflation_score',
            'debt_score', 'fx_score', 'drawdown_score', 'var_score',  'arima_score' , 'prophet_score','current_account_score', 'sentiment_score'
        ]]
    

def main():
    risk_scores = RiskAssessor().calculate_scores()
    risk_scores.reset_index(inplace=True,drop=True)
    risk_scores.to_parquet(DATA_PATH / "processed/risk_scores.parquet")
    print("Latest Risk Scores:\n", risk_scores.head(50))

if __name__ == "__main__":
    main()