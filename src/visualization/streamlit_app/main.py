import streamlit as st
from data_collection.Macroeconomic.World_bank import fetch_worldbank_data

def main():
    st.title("Emerging Markets Dashboard")
    country = st.selectbox("Select Country", ["BRA", "ZAF", "TUR"])
    gdp_data = fetch_worldbank_data(country, "NY.GDP.MKTP.KD.ZG")
    st.line_chart(gdp_data.set_index('date')['value'])

if __name__ == "__main__":
    main()