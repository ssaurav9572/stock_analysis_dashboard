import streamlit as st
from datetime import datetime

def format_value(key, value):
    """Format numbers, percentages, and dates for readability"""
    if value is None or value == "N/A":
        return "N/A"
    if key == "Debt to Equity":
        return f"{value:.2f}"

    # Format large numbers with commas
    if isinstance(value, (int, float)):
        if "percent" in key.lower() or "yield" in key.lower() or "margins" in key.lower():
            return f"{value*100:.2f}%" if value < 1 else f"{value:.2f}%"
        elif "ratio" in key.lower() or "pe" in key.lower():
            return f"{value:.2f}"
        elif "date" in key.lower() or "epoch" in key.lower() or "yearend" in key.lower():
            try:
                return datetime.utcfromtimestamp(int(value)).strftime('%Y-%m-%d')
            except:
                return str(value)
        else:
            return f"{value:,.0f}"  # comma format for numbers

    return str(value)


def show_metrics(stock, company):
    st.header(f"📊 Key Performance Indicators - {company}")
    try:
        info = stock.info
        fi = stock.fast_info
        # Fetch Debt to Equity safely
        debt_to_equity = info.get("debtToEquity") or info.get("debtEquity") or fi.get("debt_to_equity") or "N/A"
        market_cap = fi.get("market_cap") or info.get("marketCap") or info.get("market_cap") or "N/A"
        # ✅ All metrics you want in Key Metrics
        key_metrics = {
            "Previous Close": info.get("previousClose", "N/A"),
            "Open": info.get("open", "N/A"),
            "Day Low": info.get("dayLow", "N/A"),
            "Day High": info.get("dayHigh", "N/A"),
            "Market Cap": market_cap,
            "52-Week Low": info.get("fiftyTwoWeekLow", "N/A"),
            "52-Week High": info.get("fiftyTwoWeekHigh", "N/A"),
            "EBITDA": info.get("ebitda", "N/A"),
            "Debt to Equity": debt_to_equity,
            "Current Ratio": info.get("currentRatio", "N/A"),
            "Return on Equity": info.get("returnOnEquity", "N/A"),
            "Free Cashflow": info.get("freeCashflow", "N/A"),
            "Recommendation": info.get("recommendationKey", "N/A"),
            "Regular Market Price": info.get("regularMarketPrice", "N/A"),
            "Dividend Yield": info.get("dividendYield", "N/A"),
            "Total Revenue": info.get("totalRevenue", "N/A"),
        }

        # ✅ Key Metrics Display
        st.subheader("🔥 Key Metrics")
        cols_per_row = 4
        keys = list(key_metrics.keys())
        for i in range(0, len(keys), cols_per_row):
            row_metrics = keys[i:i+cols_per_row]
            cols = st.columns(len(row_metrics))
            for col, metric in zip(cols, row_metrics):
                value = format_value(metric, key_metrics[metric])
                col.markdown(f"""
                <div class='metric-card'>
                    <div style='font-size:14px'>{metric}</div>
                    <div style='font-size:20px;margin-top:5px'>{value}</div>
                </div>
                """, unsafe_allow_html=True)

        # ✅ Only allowed "Other Metrics"
        allowed_other_metrics = {
            "boardRisk": "Board Risk",
            "overallRisk": "Overall Risk",
            "priceHint": "Price Hint",
            "regularMarketOpen": "Regular Market Open",
            "dividendRate": "Dividend Rate",
            "payoutRatio": "Payout Ratio",
            "trailingPE": "Trailing PE",
            "regularMarketVolume": "Regular Market Volume",
            "averageDailyVolume10Day": "Average Daily Volume (10 Day)",
            "twoHundredDayAverage": "200 Day Average",
            "profitMargins": "Profit Margins",
            "heldPercentInsiders": "Held Percent Insiders",
            "bookValue": "Book Value",
            "netIncomeToCommon": "Net Income to Common",
            "enterpriseToEbitda": "Enterprise to EBITDA",
            "lastDividendValue": "Last Dividend Value",
            "targetMeanPrice": "Target Mean Price",
            "totalCashPerShare": "Total Cash per Share",
            "quickRatio": "Quick Ratio",
            "operatingCashflow": "Operating Cashflow",
            "grossMargins": "Gross Margins",
            "epsTrailingTwelveMonths": "EPS (Trailing 12M)",
            "priceEpsCurrentYear": "Price/EPS Current Year",
            "fiveYearAvgDividendYield": "5Y Avg Dividend Yield",
            "forwardPE": "Forward PE",
            "averageVolume": "Average Volume",
            "priceToSalesTrailing12Months": "Price/Sales (TTM)",
            "floatShares": "Float Shares",
            "heldPercentInstitutions": "Held Percent Institutions",
            "priceToBook": "Price to Book",
            "revenuePerShare": "Revenue per Share",
            "grossProfits": "Gross Profits",
            "earningsGrowth": "Earnings Growth",
            "ebitdaMargins": "EBITDA Margins",
            "epsForward": "EPS Forward",
            "trailingPegRatio": "Trailing PEG Ratio",
            "regularMarketPreviousClose": "Regular Market Prev Close",
            "beta": "Beta",
            "volume": "Volume",
            "averageVolume10days": "Average Volume (10 Days)",
            "fiftyDayAverage": "50 Day Average",
            "enterpriseValue": "Enterprise Value",
            "sharesOutstanding": "Shares Outstanding",
            "forwardEps": "Forward EPS",
            "totalCash": "Total Cash",
            "totalDebt": "Total Debt",
            "returnOnAssets": "Return on Assets",
            "revenueGrowth": "Revenue Growth",
            "operatingMargins": "Operating Margins",
            "epsCurrentYear": "EPS Current Year"
        }
        st.subheader("📌 Other Metrics")
        col1, col2, col3 = st.columns(3)
        j = 0
        for key, label in allowed_other_metrics.items():
            value = info.get(key, "N/A")
            if value != "N/A":
                formatted_value = format_value(key, value)
                if j % 3 == 0:
                    col1.write(f"**{label}:** {formatted_value}")
                elif j % 3 == 1:
                    col2.write(f"**{label}:** {formatted_value}")
                else:
                    col3.write(f"**{label}:** {formatted_value}")
                j += 1

    except Exception as e:
        st.warning("Could not fetch Key Metrics.")
        st.write(e)
