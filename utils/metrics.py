import streamlit as st
from datetime import datetime
import pandas as pd
import sys
import math
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))  # adds stock_market_dashboard to path
from config.metric_name import INFO_NOT_AVAILABLE, key_metrics_list, key_metric_mapping, other_metrics_mapping


def safe_val(x):
    """Return 0 if x is None or NaN"""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return 0
    return x

# ---------------- Helper Functions ----------------
def get_metric(info_dict, keys, default=INFO_NOT_AVAILABLE):
    """Return first available value from keys."""
    for key in keys:
        value = info_dict.get(key)
        if value not in (None, INFO_NOT_AVAILABLE):
            return value
    return default

def df_to_serializable_dict(df):
    """Convert DataFrame to dict with string keys to avoid JSON errors."""
    if df.empty:
        return {}
    df_copy = df.copy()
    df_copy.index = df_copy.index.map(str)
    df_copy.columns = df_copy.columns.map(str)
    return df_copy.to_dict()

def format_value(key, value, key_metrics=None):
    """Format numbers, percentages, and prices for display."""
    if value is None or value == INFO_NOT_AVAILABLE:
        return INFO_NOT_AVAILABLE

    # Price change formatting
    if key in ["Current Price", "Open"] and key_metrics:
        prev_close = key_metrics.get("Previous Close")
        if prev_close not in (None, INFO_NOT_AVAILABLE):
            try:
                diff = value - prev_close
                percent = (diff / prev_close) * 100 if prev_close != 0 else 0
                if diff > 0:
                    change_str = f"<span style='color:green;font-size:13px'>📈 +{round_if_needed(diff)} (+{round_if_needed(percent)}%)</span>"
                elif diff < 0:
                    change_str = f"<span style='color:red;font-size:13px'>📉 {round_if_needed(diff)} ({round_if_needed(percent)}%)</span>"
                else:
                    change_str = f"<span style='color:gray;font-size:13px'>➡️ 0 (0%)</span>"
                return f"{round_if_needed(value)}<br>{change_str}"
            except:
                return str(value)

    # Numeric formatting
    if isinstance(value, (int, float)):
        if "percent" in key.lower() or "yield" in key.lower() or "margins" in key.lower():
            return f"{round_if_needed(value*100)}%" if value < 1 else f"{round_if_needed(value)}%"
        elif "ratio" in key.lower() or "pe" in key.lower():
            return f"{round_if_needed(value)}"
        elif "date" in key.lower() or "epoch" in key.lower() or "yearend" in key.lower():
            try:
                return datetime.utcfromtimestamp(int(value)).strftime('%Y-%m-%d')
            except:
                return str(value)
        else:
            # Use comma for thousands and round if float
            if isinstance(value, int):
                return f"{value:,}"
            else:
                return f"{round_if_needed(value, True):,}"

    return str(value)

def round_if_needed(value, is_float=False):
    """Round float only if more than 3 decimal places."""
    if isinstance(value, float):
        s = str(value)
        if '.' in s and len(s.split('.')[1]) > 3:
            return round(value, 3)
        return value
    return value

def calculate_metric_from_statements(metric_name, info, fi, balance_sheet, income_statement, cashflow):
    """Calculate key metrics from latest fiscal year if not available in info or fi."""
    try:
        # Get latest year from statements
        latest_year_bs = max(balance_sheet.keys(), default=None)
        latest_year_is = max(income_statement.keys(), default=None)
        latest_year_cf = max(cashflow.keys(), default=None)

        # Helper to get value safely
        def get_val(d, key, year=None):
            if year and year in d:
                return d[year].get(key, 0)
            return d.get(key, 0)

        # ---------------- Metric Calculations ----------------
        if metric_name == "EBITDA":
            # EBITDA = Operating Revenue - SG&A - Other Non Interest Expense - Occupancy And Equipment + Depreciation + Amortization
            operating_rev = safe_val(get_val(income_statement, "Operating Revenue", latest_year_is))
            sg_a = safe_val(get_val(income_statement, "Selling General And Administration", latest_year_is))
            other_exp = safe_val(get_val(income_statement, "Other Non Interest Expense", latest_year_is))
            occupancy = safe_val(get_val(income_statement, "Occupancy And Equipment", latest_year_is))
            depreciation = safe_val(get_val(income_statement, "Depreciation And Amortization In Income Statement", latest_year_is))
            
            if None in (operating_rev, sg_a, other_exp, occupancy, depreciation):
                return INFO_NOT_AVAILABLE
            
            ebitda = operating_rev - sg_a - other_exp - occupancy + depreciation
            return ebitda

        if metric_name == "Current Ratio":
            # Current Assets / Current Liabilities
            current_assets = sum([
                safe_val(get_val(balance_sheet, "Cash And Cash Equivalents", latest_year_bs)),
                safe_val(get_val(balance_sheet, "Accounts Receivable", latest_year_bs)),
                safe_val(get_val(balance_sheet, "Other Short Term Investments", latest_year_bs)),
                safe_val(get_val(balance_sheet, "Prepaid Assets", latest_year_bs))
            ])
            current_liabilities = sum([
                safe_val(get_val(balance_sheet, "Current Debt And Capital Lease Obligation", latest_year_bs)),
                safe_val(get_val(balance_sheet, "Accounts Payable", latest_year_bs)),
                safe_val(get_val(balance_sheet, "Current Accrued Expenses", latest_year_bs)),
                safe_val(get_val(balance_sheet, "Other Payable", latest_year_bs))
            ])
            if current_assets and current_liabilities:
                return current_assets / current_liabilities
            return INFO_NOT_AVAILABLE

        if metric_name == "Debt to Equity":
            total_debt = safe_val(get_val(balance_sheet, "Total Debt", latest_year_bs))
            equity = safe_val(get_val(balance_sheet, "Stockholders Equity", latest_year_bs))
            if total_debt and equity:
                return total_debt / equity
            return INFO_NOT_AVAILABLE
        
        if metric_name == "Return on Assets":
            net_income = get_val(info, "netIncomeToCommon") or get_val(income_statement, "Net Income", latest_year_is)
            assets = get_val(balance_sheet, "Total Assets", latest_year_bs)
            return net_income / assets if net_income and assets else INFO_NOT_AVAILABLE

        if metric_name == "Free Cashflow":
            operating_cf = get_val(info, "operatingCashflow") or get_val(cashflow, "Operating Cash Flow", latest_year_cf)
            capex = get_val(info, "capitalExpenditures") or get_val(cashflow, "Capital Expenditure", latest_year_cf)
            return operating_cf - capex if operating_cf is not None and capex is not None else INFO_NOT_AVAILABLE

        if metric_name == "Net Profit Margin":
            net_income = get_val(info, "netIncomeToCommon") or get_val(income_statement, "Net Income", latest_year_is)
            revenue = get_val(info, "totalRevenue") or get_val(income_statement, "Total Revenue", latest_year_is)
            return net_income / revenue if revenue else INFO_NOT_AVAILABLE

        if metric_name == "Operating Margin":
            operating_income = get_val(info, "operatingIncome") or get_val(income_statement, "Operating Income", latest_year_is)
            revenue = get_val(info, "totalRevenue") or get_val(income_statement, "Total Revenue", latest_year_is)
            return operating_income / revenue if revenue else INFO_NOT_AVAILABLE

        if metric_name == "EBITDA Margin":
            ebitda = get_val(info, "ebitda") or get_val(income_statement, "EBITDA", latest_year_is)
            revenue = get_val(info, "totalRevenue") or get_val(income_statement, "Total Revenue", latest_year_is)
            return ebitda / revenue if revenue else INFO_NOT_AVAILABLE

        if metric_name == "Price to Sales":
            market_cap = get_val(info, "marketCap") or get_val(fi, "marketCap")
            revenue = get_val(info, "totalRevenue") or get_val(income_statement, "Total Revenue", latest_year_is)
            return market_cap / revenue if revenue else INFO_NOT_AVAILABLE

        if metric_name == "Gross Margin":
            revenue = get_val(info, "totalRevenue") or get_val(income_statement, "Total Revenue", latest_year_is)
            gross_profit = get_val(info, "grossProfits") or get_val(income_statement, "Gross Profit", latest_year_is)
            return gross_profit / revenue if revenue else INFO_NOT_AVAILABLE

        if metric_name == "EPS Forward":
            net_income = get_val(info, "netIncomeToCommon") or get_val(income_statement, "Net Income", latest_year_is)
            shares_out = get_val(info, "sharesOutstanding") or get_val(balance_sheet, "Shares Outstanding", latest_year_bs)
            return net_income / shares_out if shares_out else INFO_NOT_AVAILABLE

    except:
        return INFO_NOT_AVAILABLE
    return INFO_NOT_AVAILABLE


# ---------------- Main Show Metrics ----------------
def show_metrics(stock, company):
    st.header(f"📊 Key Performance Indicators - {company}")
    try:
        info = stock.info
        fi = stock.fast_info

        # Convert DataFrames to dict
        balance_sheet = df_to_serializable_dict(getattr(stock, "balance_sheet", pd.DataFrame()))
        income_statement = df_to_serializable_dict(getattr(stock, "financials", pd.DataFrame()))
        cashflow = df_to_serializable_dict(getattr(stock, "cashflow", pd.DataFrame()))
        # ---------------- Key Metrics ----------------
        key_metrics = {}
        for metric in key_metrics_list:
            keys = key_metric_mapping.get(metric, [])
            value = get_metric(info, keys) or get_metric(fi, keys)
            if value in (None, INFO_NOT_AVAILABLE):
                value = calculate_metric_from_statements(metric, info, fi, balance_sheet, income_statement, cashflow)
            key_metrics[metric] = value if value is not None else INFO_NOT_AVAILABLE

        st.subheader("🔥 Key Metrics")
        cols_per_row = 4
        keys_list_ordered = list(key_metrics.keys())
        for i in range(0, len(keys_list_ordered), cols_per_row):
            row_metrics = keys_list_ordered[i:i+cols_per_row]
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
        st.subheader("📌 Other Metrics")
        col1, col2, col3 = st.columns(3)
        j = 0
        for key, label in other_metrics_mapping.items():
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



