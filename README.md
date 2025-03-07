# Final-Project

# Emerging Markets Investor Helper

## Overview:
The Emerging Markets Investor Helper is an application that empowers investors to analyze risks and identify opportunities in emerging markets.

It integrates macroeconomic data, currency analysis, and sentiment analysis to produce actionable insights, enabling users to make informed investment decisions.

---

## Set up 

### 1. Install Venv, run requirements
      - python -m venv venv
      - source venv/bin/activate
      - pip install -r requirements

### 2. Add config/api_keys.yaml

### 3. Collect Data
      - Run fx_data.py
      - Run macroeconomic_data.py
      - Run news_collector.py

### 4. Process data
      - Run process_macro_data.py
      - Run process_news_sentiment.py
      - Run volatility_calculations.py
      - risk_assessment.py

## 5. Visualization in Streamlit
      - streamlit run src/visualization/streamlit_app/main.py

---

## Features:
### 1. Country Risk Analysis:
- Pull macroeconomic indicators such as GDP growth, inflation, debt-to-GDP ratio, unemployment rate, and current account balance from sources like the World Bank API.

### 2. Currency Risk Assessment:
- Analyze FX volatility and trends using historical currency exchange rates from Yahoo finance
- Provide metrics like rolling standard deviation, average drawdown, and Value at Risk (VaR).
- Forecast potential movements using basic time-series models like ARIMA and Prophet.

### 3. News Sentiment Analysis:
- Use financial news APIs (NewsAPI) to gather headlines and articles for emerging markets.
- Apply NLP techniques (sentiment scoring with Vader) to gauge market sentiment.
- Summarize sentiment trends at the country or sector level.

### 4. Risk Index
- Score each country using a risk assessment model that factors:
   - Macroeconomic data.
   - FX Volatility, dradown, var and expected return
   - News sentiment

### 4. Interactive Visualization:
- Develop a dashboard using Streamlit, Dash, or Plotly to allow users to explore data interactively.
- Include features like country comparisons, sentiment trendlines, and sector-specific breakdowns.


---

## Key Tools and Libraries:
### 1. Data Collection:
- **APIs:** World Bank API, Yahoo Finance API, NewsAPI..

### 2. Data Processing:
- Pandas, NumPy for data cleaning and manipulation.
- Scikit-learn for feature extraction and model building.

### 3. Analysis:
- **Risk Analysis:** Statsmodels, PyPortfolioOpt.
- **Sentiment Analysis:** Vader
- **Time-Series Analysis:** ARIMA, Prophet.

### 4. Visualization:
- Plotly, Matplotlib for visualizations.
- Streamlit for interactive dashboards.

---

## Deliverables:
1. **Interactive Dashboard:**
   - Explore country risk, currency trends, sector opportunities, and sentiment data.
   - Enable filtering by regions, sectors, or risk thresholds.

2. **Codebase:**
   - A self-contained repository with all code, documentation, and setup instructions.

3. **Video Walkthrough:**
   - A demonstration of the app's features, code structure, and implementation trade-offs.


