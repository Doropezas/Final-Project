import streamlit as st
import plotly.express as px
from src.data_collection.macroeconomic_data import fetch_worldbank_data

def regional_comparison():
    st.header("Regional Economic Health Dashboard")
    
    # GDP Comparison
    gdp_data = fetch_worldbank_data('NY.GDP.MKTP.KD.ZG')
    fig = px.choropleth(gdp_data, 
                        locations="countryiso3code",
                        color="value",
                        animation_frame="date",
                        scope="asia",
                        title="GDP Growth - Asian Focus")
    st.plotly_chart(fig)
    
    # Risk Score Heatmap
    risk_scores = calculate_risk_scores(processed_data)
    fig = px.density_heatmap(risk_scores, 
                            x="region", 
                            y="country", 
                            z="risk_score")
    st.plotly_chart(fig)