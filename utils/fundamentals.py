import streamlit as st
import pandas as pd
import io
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent 

# -------------------------
# Introduction Page
# -------------------------
def show_introduction(stock, company):
    st.header(f"Know about - {company}")
    try:
        info = stock.info
        description = info.get("longBusinessSummary", "Description not available.")

        # ✅ Company description
        intro_file = BASE_DIR / "templates" / "intro.html"
        intro_html = intro_file.read_text(encoding="utf-8")
        st.markdown(intro_html.replace("{{ description }}", description), unsafe_allow_html=True)

        # ✅ Company details
        st.subheader("🏢 Company Details")
        details = {
            "Address": info.get("address1", "N/A"),
            "City": info.get("city", "N/A"),
            "Website": f"[{info.get('website','N/A')}]({info.get('website')})" if info.get("website") else "N/A",
            "Phone": info.get("phone", "N/A"),
            "Industry": info.get("industryDisp", "N/A"),
            "Sector": info.get("sectorDisp", "N/A"),
            "Employees": f"{info.get('fullTimeEmployees'):,}" if info.get("fullTimeEmployees") else "N/A",
        }

        # Display details in columns for better alignment
        for key, value in details.items():
            st.write(f"**{key}:** {value}")

        # ✅ Company officers
        st.subheader("👨‍💼 Company Officers")
        officers = info.get("companyOfficers", [])
        valid_officers = [o for o in officers if o.get("name") and o.get("title") and o.get("totalPay")]

        if valid_officers:
            officer_file = BASE_DIR / "templates" / "officer.html"
            officer_template = officer_file.read_text(encoding="utf-8")

            for officer in valid_officers[:5]:
                total_pay = officer.get("totalPay")
                if isinstance(total_pay, (int, float)):
                    total_pay = f"{total_pay:,}"   # format with commas
                else:
                    total_pay = "N/A"

                html_card = officer_template.replace("{{ name }}", officer.get("name", "N/A")) \
                                            .replace("{{ title }}", officer.get("title", "N/A")) \
                                            .replace("{{ age }}", str(officer.get("age", "N/A"))) \
                                            .replace("{{ total_pay }}", str(total_pay))

                st.markdown(html_card, unsafe_allow_html=True)
        else:
            st.write("No valid officer information available.")

        # ✅ Current price
        st.subheader("💰 Current Price")
        try:
            price = stock.history(period="1d")['Close'].iloc[-1]
            st.metric("Price", f"₹{price:,.2f}")
        except:
            st.warning("Current price not available.")

    except Exception as e:
        st.warning("Introduction info not available.")
        st.write(e)


# -------------------------
# Fundamentals Page
# -------------------------
def format_df(df):
    """Format numbers and timestamps in DataFrame for readability"""
    df_formatted = df.copy()

    # Format column headers if they are datetime
    new_columns = []
    for col in df_formatted.columns:
        if isinstance(col, pd.Timestamp):
            new_columns.append(col.strftime('%Y-%m-%d'))
        else:
            new_columns.append(col)
    df_formatted.columns = new_columns

    # Format the data values
    for col in df_formatted.columns:
        # Format numbers with commas
        if pd.api.types.is_numeric_dtype(df_formatted[col]):
            df_formatted[col] = df_formatted[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "")
        # Format timestamps/datetime to YYYY-MM-DD
        elif pd.api.types.is_datetime64_any_dtype(df_formatted[col]) or "date" in str(df_formatted[col].dtype).lower():
            df_formatted[col] = pd.to_datetime(df_formatted[col], errors='coerce').dt.strftime('%Y-%m-%d')

    return df_formatted


def show_fundamentals(stock, ticker):
    st.header(f"📖 Fundamentals - {ticker}")

    def show_df(df, title):
        if df is not None and not df.empty:
            st.subheader(title)
            
            # Format DataFrame
            df_display = format_df(df)
            
            # Display with fixed width and increased height
            st.dataframe(df_display, height=500, width=1200)

            # CSV download
            csv = df.to_csv().encode('utf-8')
            st.download_button(
                f"📥 Download {title} as CSV",
                data=csv,
                file_name=f"{ticker}_{title}.csv",
                mime="text/csv"
            )

            # Excel download
            towrite = io.BytesIO()
            df.to_excel(towrite, index=True, engine='xlsxwriter')
            towrite.seek(0)
            st.download_button(
                f"📥 Download {title} as Excel",
                data=towrite,
                file_name=f"{ticker}_{title}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning(f"{title} not available.")

    # Dictionary of fundamentals
    fundamentals = {
        "Financials (Income Statement)": lambda: stock.financials,
        "Balance Sheet": lambda: stock.balance_sheet,
        "Cashflow": lambda: stock.cashflow,
        "Income Statement (Alternative)": lambda: getattr(stock, 'income_stmt', None)
    }

    for label, func in fundamentals.items():
        try:
            df = func()
            show_df(df, label)
        except Exception as e:
            st.warning(f"{label} not available.")
            st.write(e)
