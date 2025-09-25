import streamlit as st
import yfinance as yf
from config.stock_categories import stock_categories
from utils import fundamentals, charts, indicators, metrics
from pathlib import Path

# Load CSS
def load_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load HTML snippets
def load_html(file_name):
    return Path(file_name).read_text()

# Streamlit page config
st.set_page_config(page_title="📊 Stock Market Dashboard", layout="wide")
load_css("styles/style.css")

st.title("📊 Stock Market Dashboard")

# Sidebar selections
category = st.sidebar.selectbox("Select Stock Category", list(stock_categories.keys()))
company = st.sidebar.selectbox("Select a Company", list(stock_categories[category].keys()))
ticker = stock_categories[category][company]

if ticker:
    stock = yf.Ticker(ticker)
    section = st.sidebar.radio("Select Section", ["Introduction", "Key Metrics", "Fundamentals", "Charts", "Technical Indicators"])

    if section == "Introduction":
        fundamentals.show_introduction(stock, company)

    elif section == "Fundamentals":
        fundamentals.show_fundamentals(stock, ticker)

    elif section == "Charts":
        charts.show_charts(stock, company)

    elif section == "Technical Indicators":
        indicators.show_indicators(stock, company)

    elif section == "Key Metrics":
        metrics.show_metrics(stock, company)
