# Define the API endpoint
BASE_URL = "http://api.worldbank.org/v2/country/{}/indicator/{}?format=json&date=2010:2024"

# List of country codes for emerging markets (ISO 3166-1 alpha-3 codes)
countries = ["BRA", "IND", "CHN", "RUS", "MEX", "ZAF", "IDN", "TUR"]

# Economic indicators (you can change them)
indicators = {
    "GDP Growth (%)": "NY.GDP.MKTP.KD.ZG",
    "Inflation (%)": "FP.CPI.TOTL.ZG",
    "Debt to GDP (%)": "GC.DOD.TOTL.GD.ZS"
}

# Fetch data
data_list = []

for country in countries:
    for indicator_name, indicator_code in indicators.items():
        url = BASE_URL.format(country, indicator_code)
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1 and "value" in data[1][0]:
                for entry in data[1]:
                    data_list.append({
                        "Country": country,
                        "Indicator": indicator_name,
                        "Year": entry["date"],
                        "Value": entry["value"]
                    })

# Convert to DataFrame
df_wb = pd.DataFrame(data_list)

# Show the data
import ace_tools as tools
tools.display_dataframe_to_user(name="World Bank Economic Data", dataframe=df_wb)
