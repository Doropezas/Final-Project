# src/visualization/dashboard.py
import streamlit as st
import yaml
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta, timezone

DATA_PATH = Path(__file__).parent.parent.parent.parent / "data"
CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "config"

# Cache data loading
# @st.cache_data
def load_data():
    return {
        'macro_df': pd.read_parquet(DATA_PATH / "processed/macro_indicators.parquet"),
        'vol_df': pd.read_parquet(DATA_PATH / "processed/fx_volatility.parquet"),
        'sentiment_df': pd.read_parquet(DATA_PATH / "processed/news_sentiment.parquet"),
        'risk_df': pd.read_parquet(DATA_PATH / "processed/risk_scores.parquet"),
        'fx_rates': load_fx_rates(),
        'news': load_recent_news(),
        'country_crncy': load_crncy_mapping(),
        'country_mapping': country_mapping() 
    }

def load_fx_rates():
    """Load all FX CSV files and combine into single DataFrame"""
    fx_files = (DATA_PATH / "raw/fx").rglob("*.csv")
    
    dfs = []
    for file in fx_files:
        try:
            # Extract currency pair from filename
            pair = file.stem.split("_")[0]  
            region = file.parent.name
            df = pd.read_csv(file, parse_dates=['Date'])
            df['pair'] = pair
            df['region'] = region
            dfs.append(df)
        except Exception as e:
            print(f"Error processing {file.name}: {str(e)}")
            continue
    
    return pd.concat(dfs).sort_index()


def country_mapping():
    with open(CONFIG_PATH / "countries_regions.yaml") as f:
        return yaml.safe_load(f)['country_mapping']

def load_recent_news():
    """Load last 7 news articles"""
    news_files = (DATA_PATH / "raw/news").rglob("*.parquet")
    dfs = []
    for file in news_files:
        df = pd.read_parquet(file)
        country_name = file.parent.name.replace("_", " ")
        country_map = country_mapping()
        df['country'] = country_map.get(country_name, "UNKNOWN")
        dfs.append(df)
    all_news = pd.concat(dfs)
    all_news['publishedAt'] = pd.to_datetime(all_news['publishedAt'])
    now_utc = datetime.now(timezone.utc)
    return all_news[all_news['publishedAt'] >= now_utc - timedelta(days=7)]



def load_crncy_mapping() -> dict:
    return {
            'IDN':'IDR',  # Indonesia
            'MYS':'MYR',  # Malaysia
            'THA':'THB',  # Thailand
            'CHN':'CNY',  # China
            'IND':'INR',  # India
            'MEX':'MXN',  # Mexico
            'BRA':'BRL',  # Brazil
            'COL':'COP',  # Colombia
            'CHL':'CLP',  # Chile
            'PER':'PEN',  # Peru
            'ZAF':'ZAR',  # South Africa
            'POL':'PLN',  # Poland
            'HUN':'HUF',  # Hungary
            'TUR':'TRY',  # Turkey
            'CZE':'CZK',  # Czech Republic
            'EGY':'EGP',  # Egypt
            'ROU':'ROU'   # Romania
    }



def create_dashboard():
    st.set_page_config(page_title="EM Investor Dashboard", layout="wide")
    data = load_data()
    
    # Sidebar controls
    st.sidebar.header("Filters")
    selected_region = st.sidebar.selectbox("Select Region", data['risk_df']['region'].unique())
    countries = data['risk_df'][data['risk_df']['region'] == selected_region]['country']
    selected_country = st.sidebar.selectbox("Select Country", countries)
 # Main dashboard
    st.title("Emerging Markets Investment Safety Ranking")
    
    # Global safety ranking
    st.subheader("Global Ranking")
    col1, col2 = st.columns([3, 2])
    
    with col1:
        fig = px.bar(data['risk_df'], 
                    x='risk_score', y='country', orientation='h',
                    color='risk_score', color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.dataframe(data['risk_df'][['country', 'risk_score', 'region']],
                    hide_index=True,
                    column_config={"risk_score": "Risk Score (0-100)"})

    # Country-specific section
    st.divider()
    st.header(f"Country Analysis")
    
    # Currency and news columns
    col1, col2 = st.columns([2, 3])
    
    with col1:
        # Currency trend plot
        currency_pair = f"USD{data['country_crncy'][selected_country]}"
        st.subheader(f"Currency Trend ({currency_pair})")
        fx_data = data['fx_rates'][data['fx_rates']['pair'] == currency_pair]
        if not fx_data.empty:
            fig = px.line(fx_data, x='Date', y='Close',
                          title=f"{currency_pair} Exchange Rate")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No currency data available")

    with col2:
        # Recent news with sentiment
        st.subheader("Recent Market News & Sentiment")
        country_news = data['news'][data['news']['country'] == selected_country]
        
        if not country_news.empty:
            st.dataframe(country_news.head(10),hide_index=True)
        else:
            st.info("No recent news articles found")

    
    # Risk breakdown radar chart
    st.subheader("Risk Score Breakdown")
    categories = ['GDP Growth', 'Inflation', 'FX Volatility', 'Drawdown', 'Value at Risk', 'Expected Return 1Month', 'News Sentiment', 'Debt Level', 'Current Account']
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=data['risk_df'].loc[data['risk_df']['country'] == selected_country, 
        ['gdp_score', 'inflation_score', 'fx_score', 'drawdown_score', 'var_score', 'prophet_score', 'sentiment_score','debt_score', 'current_account_score']].values[0],
        theta=categories,
        fill='toself',
        name=selected_country
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])),
                      showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Macro Indicator Comparison Section in a 2x2 grid
    st.subheader("Macro Indicator Comparison")
    
    # List of indicators to compare
    indicators = ['current_account', 'inflation', 'debt_to_gdp', 'gdp_growth']
    
    # Prepare a copy of the macro dataframe with a flag for the selected country
    macro_comparison = data['macro_df'].copy()
    macro_comparison['highlight'] = macro_comparison['country'] == selected_country
    
    # Define refined colors: red for the selected country and blue for others
    color_map = {True: '#EF553B', False: '#636EFA'}
    
    # Loop over the indicators two at a time to form a 2x2 grid
    for i in range(0, len(indicators), 2):
        col1, col2 = st.columns(2)
        
        # First chart in the row
        indicator = indicators[i]
        sorted_df = macro_comparison.sort_values(by=indicator, ascending=False)
        fig = px.bar(
            sorted_df,
            x='country',
            y=indicator,
            color='highlight',
            color_discrete_map=color_map,
            title=f"{indicator.replace('_', ' ').title()} Comparison"
        )
        col1.plotly_chart(fig, use_container_width=True)
        
        # Check if there's a second indicator for this row
        if i + 1 < len(indicators):
            indicator = indicators[i+1]
            sorted_df = macro_comparison.sort_values(by=indicator, ascending=False)
            fig = px.bar(
                sorted_df,
                x='country',
                y=indicator,
                color='highlight',
                color_discrete_map=color_map,
                title=f"{indicator.replace('_', ' ').title()} Comparison"
            )
            col2.plotly_chart(fig, use_container_width=True)
    
    # FX volatility analysis
    st.subheader("Foreign Exchange Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        
        # Select the FX data for the chosen country (assuming one row per country)
        vol_country = data['vol_df'][data['vol_df']['country'] == selected_country]
        if not vol_country.empty:
            forecast_data = pd.DataFrame({
                'Metric': ['Historical Volatility', 'ARIMA Forecast', 'Prophet Forecast'],
                'Value': [
                    vol_country['volatility'].values[0],
                    vol_country['arima_forecast'].values[0],
                    vol_country['prophet_forecast'].values[0]
                ]
            })
            # Create a bar chart with refined colors
            fig = px.bar(
                forecast_data, 
                x='Metric', 
                y='Value', 
                title=f"FX Volatility Forecast for {selected_country}",
                color='Metric',
                color_discrete_map={
                    'Historical Volatility': '#636EFA',
                    'ARIMA Forecast': '#EF553B',
                    'Prophet Forecast': '#00CC96'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No FX volatility data available for the selected country.")
    
    with col2:
        
        # Compare across countries using available FX metrics: volatility and VaR (using 'var')
        fig = px.bar(
            data['vol_df'],
            x='country',
            y=['volatility', 'var'],
            title="FX Risk Metrics Comparison",
            barmode='group',
            labels={'value': 'Metric Value', 'variable': 'Metric'}
        )
        st.plotly_chart(fig, use_container_width=True)

    
    # News sentiment analysis
    st.subheader("Recent Market Sentiment")
    country_sentiment = data['sentiment_df']
    fig = px.scatter(country_sentiment, x='country', y='avg_sentiment',
                    size='article_count', color='avg_sentiment',
                    color_continuous_scale=px.colors.diverging.RdYlGn)
    st.plotly_chart(fig, use_container_width=True)
    
    # Data download
    st.sidebar.divider()
    st.sidebar.download_button(
        label="Download Country Report",
        data=data['risk_df'][data['risk_df']['country'] == selected_country].to_csv().encode('utf-8'),
        file_name=f"{selected_country}_report.csv"
    )

if __name__ == "__main__":
    create_dashboard()