import pandas as pd
import numpy as np
from pathlib import Path
import yaml
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
import warnings
warnings.filterwarnings("ignore")

DATA_PATH = Path(__file__).parent.parent.parent / "data"
CONFIG_PATH = Path(__file__).parent.parent.parent / "config"

class FXVolatility:
    def __init__(self, window=90, var_confidence=0.95):
        self.window = window
        self.var_confidence = var_confidence
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
    
    def _calculate_drawdowns(self, series):
        """Calculate rolling maximum drawdown"""
        rolling_max = series.rolling(self.window, min_periods=1).max()
        drawdown = (series - rolling_max) / rolling_max
        return drawdown.rolling(self.window).mean()
    
    def _calculate_var(self, returns):
        """Calculate Value at Risk using historical simulation"""
        return np.percentile(returns.dropna(), (1 - self.var_confidence)*100)

    def _forecast_arima(self, series):
        """ARIMA(1,1,1) forecast for next 30 days"""
        try:
            model = ARIMA(series, order=(1,1,1))
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=30)
            return forecast.mean()
        except:
            return np.nan

    def _forecast_prophet(self, series):
        """Prophet forecast for next 30 days"""
        try:
            df = pd.DataFrame({
                'ds': series.index,
                'y': series.values
            })
            model = Prophet(daily_seasonality=False)
            model.fit(df)
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            return forecast.tail(30)['yhat'].mean()
        except:
            return np.nan

    
    def _load_and_preprocess_data(self) -> pd.DataFrame:
        """Load all FX CSV files and combine into single DataFrame"""
        fx_files = (DATA_PATH / "raw/fx").rglob("*.csv")
        
        dfs = []
        for file in fx_files:
            try:
                # Extract currency pair from filename
                pair = file.stem.split("_")[0]  
                region = file.parent.name
                
                df = pd.read_csv(file, parse_dates=['Date'], index_col='Date')
                df['pair'] = pair
                df['region'] = region
                dfs.append(df)
            except Exception as e:
                print(f"Error processing {file.name}: {str(e)}")
                continue
        
        return pd.concat(dfs).sort_index()

    def calculate_volatility(self) -> pd.DataFrame:
        """Calculate rolling volatility for each currency pair"""
        if self.fx_data.empty:
            raise ValueError("No FX data loaded")
        
        # Calculate daily returns
        returns = self.fx_data.groupby('pair')['Close'] \
            .transform(lambda x: x.astype(float).pct_change())
        
        metrics = []

        for pair, group in self.fx_data.groupby('pair'):
            pair_data = group['Close'].astype(float)
            returns = pair_data.pct_change().dropna()
            
            # Basic volatility
            vol = returns.rolling(self.window).std() * np.sqrt(252)
            
            # Additional metrics
            metrics.append({
                'pair': pair,
                'volatility': vol.iloc[-1],
                'drawdown': self._calculate_drawdowns(pair_data).iloc[-1],
                'var': self._calculate_var(returns),
                'arima_forecast': self._forecast_arima(vol.dropna()),
                'prophet_forecast': self._forecast_prophet(vol.dropna())
            })
            
        metrics_df = pd.DataFrame(metrics)
        
        # Map to country codes
        metrics_df['country'] = metrics_df['pair'].str[3:].map(self.country_map)
        
        return metrics_df

    def save_volatility_data(self, output_file: str = "processed/fx_volatility.parquet"):
        vol_df = self.calculate_volatility()
        output_path = DATA_PATH / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        vol_df.to_parquet(output_path)
        print(f"Saved volatility data to {output_path}")

if __name__ == "__main__":
    calculator = FXVolatility()
    calculator.save_volatility_data()