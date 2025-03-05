from prophet import Prophet
import pandas as pd

def forecast_inflation(country_data: pd.DataFrame):
    """ARIMA forecast for inflation using Prophet"""
    df = country_data[['date', 'CPI']].rename(columns={'date':'ds', 'CPI':'y'})
    
    model = Prophet(
        yearly_seasonality=True,
        changepoint_prior_scale=0.5
    )
    model.fit(df)
    
    future = model.make_future_dataframe(periods=12, freq='M')
    forecast = model.predict(future)
    
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]