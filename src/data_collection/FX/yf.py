import yfinance as yf
import pandas as pd
import ace_tools as tools

# Define currency pairs (Yahoo Finance format: "CURRENCY=USD")
currency_pairs = ["BRL=X", "INR=X", "CNY=X", "RUB=X", "MXN=X", "ZAR=X", "IDR=X", "TRY=X"]

# Fetch historical exchange rates
currency_data = {}

for pair in currency_pairs:
    data = yf.download(pair, start="2010-01-01", end="2024-12-31", interval="1mo")["Adj Close"]
    currency_data[pair] = data

# Convert to DataFrame
df_fx = pd.DataFrame(currency_data)

# Rename columns for readability
df_fx.columns = [pair.replace("=X", "") for pair in df_fx.columns]

# Show the data
tools.display_dataframe_to_user(name="Yahoo Finance FX Rates", dataframe=df_fx)

# Emerging market indices (Yahoo Finance symbols)
indices = {
    "Brazil Bovespa": "^BVSP",
    "India Nifty 50": "^NSEI",
    "China SSE Composite": "000001.SS",
    "Russia RTS Index": "RTSI.ME",
    "Mexico IPC Index": "^MXX",
    "South Africa JSE": "^J203",
    "Indonesia IDX": "^JKSE",
    "Turkey BIST 100": "XU100.IS"
}

# Fetch historical data
market_data = {}

for name, symbol in indices.items():
    data = yf.download(symbol, start="2010-01-01", end="2024-12-31", interval="1mo")["Adj Close"]
    market_data[name] = data

# Convert to DataFrame
df_markets = pd.DataFrame(market_data)

# Show the data
tools.display_dataframe_to_user(name="Yahoo Finance Emerging Market Indices", dataframe=df_markets)
