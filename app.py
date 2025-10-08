import streamlit as st
import yfinance as yf
from config.stock_categories import stock_categories
from utils import fundamentals, charts, indicators, metrics  # Assuming these exist based on your structure
from pathlib import Path

# Load CSS
def load_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Streamlit page config
st.set_page_config(page_title="📊 Stock Market Dashboard", layout="wide")
load_css("styles/style.css")

st.title("📊 Stock Market Dashboard")

# Sidebar selections (keep for filters)
category = st.sidebar.selectbox("Select Stock Category", list(stock_categories.keys()))
company = st.sidebar.selectbox("Select a Company", list(stock_categories[category].keys()))
ticker = stock_categories[category][company]

if ticker:
    stock = yf.Ticker(ticker)
    
    # Use tabs for sections (replaces radio)
    tab_introduction, tab_metrics, tab_fundamentals, tab_charts, tab_indicators = st.tabs(
        ["Introduction", "Key Metrics", "Fundamentals", "Charts", "Technical Indicators"]
    )
    
    # Render content inside each tab
    with tab_introduction:
        fundamentals.show_introduction(stock, company)
    
    with tab_metrics:
        metrics.show_metrics(stock, company)
    
    with tab_fundamentals:
        fundamentals.show_fundamentals(stock, ticker)
    
    with tab_charts:
        charts.show_charts(stock, company)
    
    with tab_indicators:
        indicators.show_indicators(stock, company)
else:
    st.warning("Please select a category and company.")
