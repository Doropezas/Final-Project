
import requests
import json
import pandas as pd
# from ace_tools import tools
from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.timeseries import TimeSeries

# Set API Key
api_key = ""

# Initialize Foreign Exchange API
fx = ForeignExchange(key=api_key, output_format="pandas")

# Fetch FX rates for BRL/USD, INR/USD, CNY/USD, RUB/USD, MXN/USD, ZAR/USD, IDR/USD, TRY/USD
fx_data = {}

for currency in ["BRL", "INR", "CNY", "RUB", "MXN", "ZAR", "IDR", "TRY"]:
    data, _ = fx.get_currency_exchange_daily(from_symbol=currency, to_symbol="USD", outputsize="full")
    fx_data[currency] = data["4. close"]

# Convert to DataFrame
df_alpha_fx = pd.DataFrame(fx_data)

# print(df_alpha_fx)

# Show the data
# tools.display_dataframe_to_user(name="Alpha Vantage FX Rates", dataframe=df_alpha_fx)
