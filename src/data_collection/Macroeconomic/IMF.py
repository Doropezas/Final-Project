import ace_tools as tools

# IMF API base URL
IMF_BASE_URL = "https://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/"

# WEO dataset for GDP Growth
IMF_INDICATOR = "NGDP_RPCH"  # Real GDP growth rate
IMF_DATASET = "WEO"

# Construct the full API URL
imf_url = f"{IMF_BASE_URL}{IMF_DATASET}/Q.A.{'.'.join(countries)}.{IMF_INDICATOR}?startPeriod=2010&endPeriod=2024"

# Fetch data
response = requests.get(imf_url)
imf_data = response.json()

# Extract the GDP growth values
gdp_growth_data = []
series = imf_data["CompactData"]["DataSet"]["Series"]

for country_data in series:
    country = country_data["@REF_AREA"]
    for obs in country_data["Obs"]:
        gdp_growth_data.append({
            "Country": country,
            "Year": obs["@TIME_PERIOD"],
            "GDP Growth (%)": obs["@OBS_VALUE"]
        })

# Convert to DataFrame
df_imf = pd.DataFrame(gdp_growth_data)

# Show the data
tools.display_dataframe_to_user(name="IMF GDP Growth Data", dataframe=df_imf)
