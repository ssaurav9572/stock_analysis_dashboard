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
        address = ", ".join(filter(None, [
            info.get("address1"),
            info.get("address2"),
            info.get("city"),
            info.get("zip"),
            info.get("country")
        ]))
        location = ", ".join(filter(None, [
            info.get("city"),
            info.get("country")
        ]))
        st.subheader("🏢 Company Details")
        details = {
            "Address": address,
            "City": location,
            "Website": f"[{info.get('website','N/A')}]({info.get('website')})" if info.get("website") else "N/A",
            "Phone": info.get("phone", "N/A"),
            "Industry": info.get("industryDisp", "N/A"),
            "Sector": info.get("sectorDisp", "N/A"),
            "Total Employees": f"{info.get('fullTimeEmployees'):,}" if info.get("fullTimeEmployees") else "N/A",
        }
        for key, value in details.items():
            st.write(f"**{key}:** {value}")

        # ✅ Company officers
        st.subheader("👨‍💼 Company Officers")
        officers = info.get("companyOfficers", [])
        valid_officers = [o for o in officers if o.get("name") and o.get("title") and o.get("totalPay")]

        if valid_officers:
            for officer in valid_officers[:5]:
                full_name = officer.get("name", "N/A")
                # Show only first part before comma (or full if no comma)
                collapsed_name = full_name.split(",")[0] if "," in full_name else full_name

                with st.expander(collapsed_name, expanded=False):  # <-- remove manually added ▼
                    title = officer.get("title", "N/A")
                    age = officer.get("age", "N/A")
                    total_pay = officer.get("totalPay")
                    if isinstance(total_pay, (int, float)):
                        total_pay = f"{total_pay:,}"
                    else:
                        total_pay = "N/A"

                    st.write(f"**Full Name:** {full_name}")
                    st.write(f"**Title:** {title}")
                    st.write(f"**Age:** {age}")
                    st.write(f"**Total Pay:** {total_pay}")
        else:
            st.write("No valid officer information available.")
        # ✅ Current price with arrow + % change
        st.subheader("💰 Current Price")
        try:
            price = stock.history(period="1d")['Close'].iloc[-1]
            prev_close = info.get("previousClose")

            if prev_close:
                change = price - prev_close
                pct_change = (change / prev_close) * 100

                # Green arrow if price went up, red if down
                if change > 0:
                    arrow = "⬆️"
                    color = "green"
                elif change < 0:
                    arrow = "⬇️"
                    color = "red"
                else:
                    arrow = "➡️"
                    color = "gray"

                st.markdown(
                    f"<div style='font-size:18px;'>"
                    f"<b>₹{price:,.2f}</b> "
                    f"<span style='color:{color};'>{arrow} {change:+.2f} ({pct_change:+.2f}%)</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            else:
                st.metric("Price", f"₹{price:,.2f}")

        except Exception as e:
            st.warning("Current price not available.")
            st.write(e)

    except Exception as e:
        st.warning("Introduction info not available.")
        st.write(e)

# -------------------------
# Fundamentals Page
# -------------------------
def format_df(df):
    df_formatted = df.copy()

    new_columns = []
    for col in df_formatted.columns:
        if isinstance(col, pd.Timestamp):
            new_columns.append(col.strftime('%Y-%m-%d'))
        else:
            new_columns.append(col)
    df_formatted.columns = new_columns

    for col in df_formatted.columns:
        if pd.api.types.is_numeric_dtype(df_formatted[col]):
            df_formatted[col] = df_formatted[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "")
        elif pd.api.types.is_datetime64_any_dtype(df_formatted[col]) or "date" in str(df_formatted[col].dtype).lower():
            df_formatted[col] = pd.to_datetime(df_formatted[col], errors='coerce').dt.strftime('%Y-%m-%d')

    return df_formatted


def show_fundamentals(stock, ticker):
    st.header(f"📖 Fundamentals - {ticker}")

    def show_df(df, title):
        if df is not None and not df.empty:
            st.subheader(title)
            df_display = format_df(df)
            st.dataframe(df_display, height=500, width=1200)

            csv = df.to_csv().encode('utf-8')
            st.download_button(
                f"📥 Download {title} as CSV",
                data=csv,
                file_name=f"{ticker}_{title}.csv",
                mime="text/csv"
            )

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
