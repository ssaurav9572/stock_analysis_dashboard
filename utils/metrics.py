import streamlit as st
from datetime import datetime

# ✅ Constant for missing data
INFO_NOT_AVAILABLE = "Information not available"

# ✅ Helper function to fetch metrics safely
def get_metric(info_dict, keys, default=INFO_NOT_AVAILABLE):
    """
    Try multiple keys in order and return the first available value.
    """
    for key in keys:
        value = info_dict.get(key)
        if value is not None:
            return value
    return default

# ✅ Format values for display (with price change embedded for Open & Current Price)
def format_value(key, value, key_metrics=None):
    if value is None or value == INFO_NOT_AVAILABLE:
        return INFO_NOT_AVAILABLE

    # Special handling for price metrics vs Previous Close
    if key in ["Current Price", "Open"] and key_metrics:
        prev_close = key_metrics.get("Previous Close")
        if prev_close not in (None, INFO_NOT_AVAILABLE):
            try:
                diff = value - prev_close
                percent = (diff / prev_close) * 100 if prev_close != 0 else 0

                if diff > 0:
                    change_str = f"<span style='color:green;font-size:13px'>📈 +{diff:.2f} (+{percent:.2f}%)</span>"
                elif diff < 0:
                    change_str = f"<span style='color:red;font-size:13px'>📉 -{abs(diff):.2f} ({percent:.2f}%)</span>"
                else:
                    change_str = f"<span style='color:gray;font-size:13px'>➡️ 0.00 (0.00%)</span>"

                return f"{value}<br>{change_str}"
            except Exception:
                return str(value)

    # Debt to Equity (fixed decimal)
    if key == "Debt to Equity":
        return f"{value:.2f}"

    # Numeric formatting
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
            return f"{value:,.0f}"

    return str(value)


# ✅ Show metrics function
def show_metrics(stock, company):
    st.header(f"📊 Key Performance Indicators - {company}")
    try:
        info = stock.info
        fi = stock.fast_info
        # ---------------- Key Metrics ----------------
        key_metrics = {}

        # Basic Price Metrics
        key_metrics["Current Price"] = get_metric(info, ["currentPrice"])
        key_metrics["Open"] = get_metric(info, ["open", "regularMarketOpen"])
        key_metrics["Previous Close"] = get_metric(info, ["previousClose", "regularMarketPreviousClose"])
        key_metrics["Day High"] = get_metric(info, ["dayHigh", "regularMarketDayHigh"])
        key_metrics["Day Low"] = get_metric(info, ["dayLow", "regularMarketDayLow"])
        key_metrics["Market Cap"] = get_metric(fi, ["marketCap"]) or get_metric(info, ["marketCap", "market_cap"])
        key_metrics["52-Week Low"] = get_metric(info, ["fiftyTwoWeekLow"])
        key_metrics["52-Week High"] = get_metric(info, ["fiftyTwoWeekHigh"])
        key_metrics["EBITDA"] = get_metric(info, ["ebitda"])

        # Debt to Equity
        debt = get_metric(info, ["totalDebt"])
        equity = get_metric(info, ["bookValue"])
        key_metrics["Debt to Equity"] = get_metric(info, ["debtToEquity", "debtEquity"]) \
                                        or get_metric(fi, ["debt_to_equity"]) \
                                        or (debt / equity if debt != INFO_NOT_AVAILABLE and equity != INFO_NOT_AVAILABLE else INFO_NOT_AVAILABLE)

        # Current Ratio
        current_assets = get_metric(info, ["totalCurrentAssets"])
        current_liabilities = get_metric(info, ["totalCurrentLiabilities"])
        key_metrics["Current Ratio"] = get_metric(info, ["currentRatio"]) \
                                       or (current_assets / current_liabilities if current_assets != INFO_NOT_AVAILABLE and current_liabilities != INFO_NOT_AVAILABLE else INFO_NOT_AVAILABLE)

        # Return on Equity (ROE)
        net_income = get_metric(info, ["netIncomeToCommon"])
        key_metrics["Return on Equity"] = get_metric(info, ["returnOnEquity"]) \
                                          or (net_income / equity if net_income != INFO_NOT_AVAILABLE and equity != INFO_NOT_AVAILABLE else INFO_NOT_AVAILABLE)

        # Free Cashflow
        operating_cf = get_metric(info, ["operatingCashflow"])
        capex = get_metric(info, ["capitalExpenditures"])
        key_metrics["Free Cashflow"] = get_metric(info, ["freeCashflow"]) \
                                       or (operating_cf - capex if operating_cf != INFO_NOT_AVAILABLE and capex != INFO_NOT_AVAILABLE else INFO_NOT_AVAILABLE)

        # Other Key Metrics
        key_metrics["Recommendation"] = get_metric(info, ["recommendationKey"])
        key_metrics["Regular Market Price"] = get_metric(info, ["regularMarketPrice"])
        key_metrics["Dividend Yield"] = get_metric(info, ["dividendYield"])
        key_metrics["Total Revenue"] = get_metric(info, ["totalRevenue"])
        key_metrics["Net Profit Margin"] = get_metric(info, ["profitMargins"]) \
                                           or (net_income / key_metrics["Total Revenue"] if net_income != INFO_NOT_AVAILABLE and key_metrics["Total Revenue"] != INFO_NOT_AVAILABLE else INFO_NOT_AVAILABLE)
        key_metrics["Earning per share"] = get_metric(info, ["trailingEps", "epsTrailingTwelveMonths"])
        key_metrics["Dividend payout ratio"] = get_metric(info, ["payoutRatio"])
        key_metrics["Price to Earning ratio"] = get_metric(info, ["trailingPE", "forwardPE"])

        # Display Key Metrics
        st.subheader("🔥 Key Metrics")
        cols_per_row = 4
        keys = list(key_metrics.keys())
        for i in range(0, len(keys), cols_per_row):
            row_metrics = keys[i:i+cols_per_row]
            cols = st.columns(len(row_metrics))
            for col, metric in zip(cols, row_metrics):
                value = format_value(metric, key_metrics[metric], key_metrics)
                col.markdown(f"""
                    <div class='metric-card'>
                        <div style='font-size:14px'>{metric}</div>
                        <div style='font-size:20px;margin-top:5px'>{value}</div>
                    </div>
                """, unsafe_allow_html=True)

        # ---------------- Other Metrics ----------------
        allowed_other_metrics = {
            "auditRisk": "Audit Risk",
            "boardRisk": "Board Risk",
            "compensationRisk": "Compensation Risk",
            "shareHolderRightsRisk": "Shareholder Rights Risk",
            "overallRisk": "Overall Risk",
            "priceHint": "Price Hint",
            "dividendRate": "Dividend Rate",
            "payoutRatio": "Payout Ratio",
            "regularMarketVolume": "Regular Market Volume",
            "averageDailyVolume10Day": "Average Daily Volume (10 Day)",
            "twoHundredDayAverage": "200 Day Average",
            "heldPercentInsiders": "Held Percent by Insiders",
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
            "heldPercentInstitutions": "Held Percent by Institutions",
            "priceToBook": "Price to Book",
            "revenuePerShare": "Revenue per Share",
            "grossProfits": "Gross Profits",
            "earningsGrowth": "Earnings Growth",
            "ebitdaMargins": "EBITDA Margins",
            "epsForward": "EPS Forward",
            "trailingPegRatio": "Trailing PEG Ratio",
            "regularMarketPreviousClose": "Regular Market Prev Close",
            "regularMarketOpen": "Regular Market Open",
            "regularMarketDayLow": "Regular Market Day Low",
            "regularMarketDayHigh": "Regular Market Day High",
            "exDividendDate": "Ex-Dividend Date",
            "trailingAnnualDividendRate": "Trailing Annual Dividend Rate",
            "trailingAnnualDividendYield": "Trailing Annual Dividend Yield",
            "allTimeHigh": "All Time High",
            "allTimeLow": "All Time Low",
            "fiftyTwoWeekLowChange": "52-Week Low Change",
            "fiftyTwoWeekLowChangePercent": "52-Week Low Change Percent",
            "fiftyTwoWeekRange": "52-Week Range",
            "fiftyTwoWeekHighChange": "52-Week High Change",
            "fiftyTwoWeekHighChangePercent": "52-Week High Change Percent",
            "fiftyTwoWeekChangePercent": "52-Week Change Percent",
            "epsCurrentYear": "EPS Current Year",
            "fiftyDayAverageChange": "50-Day Average Change",
            "fiftyDayAverageChangePercent": "50-Day Average Change Percent",
            "twoHundredDayAverageChange": "200-Day Average Change",
            "twoHundredDayAverageChangePercent": "200-Day Average Change Percent",
            "averageAnalystRating": "Average Analyst Rating",
            "cryptoTradeable": "Crypto Tradeable",
            "shares": "Shares",
            "tenDayAverageVolume": "10-Day Average Volume",
            "threeMonthAverageVolume": "3-Month Average Volume",
            "lastPrice": "Last Price",
            "lastVolume": "Last Volume",
            "yearChange": "Year Change",
            "yearHigh": "Year High",
            "yearLow": "Year Low",
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
        }

        st.subheader("📌 Other Metrics")
        col1, col2, col3 = st.columns(3)
        j = 0
        for key, label in allowed_other_metrics.items():
            value = get_metric(info, [key])
            if value != INFO_NOT_AVAILABLE:
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

