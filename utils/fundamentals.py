import streamlit as st
import pandas as pd
import io
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent.parent 

def clean_officer_name(full_name):
    """
    Remove common degrees/certifications, commas, dots, and extra spaces from officer names.
    Example:
        "Mr. Sandeep Bakhshi B.E." -> "Mr Sandeep Bakhshi"
        "Mr. Rakesh Jha BE, PGDM" -> "Mr Rakesh Jha"
    """
    if not full_name:
        return full_name

    # Common degrees/certifications patterns
    degree_patterns = [
        r'\bB\.?E\.?\b', r'\bM\.?E\.?\b', r'\bPGDM\b', r'\bMBA\b', r'\bB\.?Com\.?\b',
        r'\bM\.?Com\.?\b', r'\bCA\b', r'\bCS\b', r'\bCFA\b', r'\bA\.?C\.?S\.?\b',
        r'\bF\.?C\.?A\.?\b', r'\bPh\.?D\.?\b'
    ]

    # Remove degrees/certifications
    pattern = '|'.join(degree_patterns)
    cleaned = re.sub(pattern, '', full_name, flags=re.IGNORECASE)

    # Remove commas, dots, multiple spaces, and trim
    cleaned = re.sub(r'[,\.]+', '', cleaned)
    cleaned = re.sub(r'\s{2,}', ' ', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned


# -------------------------
# Introduction Page
# -------------------------
def show_introduction(stock, company):
    st.header(f"Know about - {company}")
    try:
        info = stock.info
        description = info.get("longBusinessSummary", "Description not available.")

        # ✅ Company description - Using intro.html
        intro_file = BASE_DIR / "templates" / "intro.html"
        intro_html = intro_file.read_text(encoding="utf-8")
        st.markdown(
            f'<div class="intro-text">{intro_html.replace("{{ description }}", description)}</div>',
            unsafe_allow_html=True
        )

        # ✅ Company details - Use columns for better layout (responsive)
        address = ", ".join(filter(None, [
            info.get("address1"),
            info.get("address2"),
            info.get("city"),
            info.get("country"),
            info.get("zip")
        ]))
        location = ", ".join(filter(None, [
            info.get("city"),
            info.get("country")
        ]))
        details = {
            "Address": address,
            "City": location,
            "Website": f"[{info.get('website','N/A')}]({info.get('website')})" if info.get("website") else "N/A",
            "Phone": info.get("phone", "N/A"),
            "Industry": info.get("industryDisp", "N/A"),
            "Sector": info.get("sectorDisp", "N/A"),
            "Total Employees": f"{info.get('fullTimeEmployees'):,}" if info.get("fullTimeEmployees") else "N/A",
        }
        st.subheader("🏢 Company Details")
        cols = st.columns(2)  # 2 columns on desktop, stacks on mobile
        for i, (key, value) in enumerate(details.items()):
            with cols[i % 2]:
                st.write(f"**{key}:** {value}")

        # ✅ Company officers - Using officer.html template
        st.subheader("👨‍💼 Company Officers")
        officers = info.get("companyOfficers", [])
        valid_officers = [o for o in officers if o.get("name") and o.get("title") and o.get("totalPay")]

        if valid_officers:
            officer_file = BASE_DIR / "templates" / "officer.html"
            officer_html = officer_file.read_text(encoding="utf-8")
            for officer in valid_officers[:5]:
                full_name = officer.get("name", "N/A")
                collapsed_name = clean_officer_name(full_name)
                title = officer.get("title", "N/A")
                age = officer.get("age", "N/A")
                total_pay = officer.get("totalPay")
                if isinstance(total_pay, (int, float)):
                    total_pay = f"${total_pay:,}"  # Assuming USD, adjust if needed
                else:
                    total_pay = "N/A"

                # Render HTML template
                rendered_html = officer_html.replace("{{ name }}", full_name).replace("{{ title }}", title).replace("{{ age }}", str(age)).replace("{{ total_pay }}", total_pay)
                st.markdown(f'<div class="officer-card">{rendered_html}</div>', unsafe_allow_html=True)
        else:
            st.info("No valid officer information available.")

        # ✅ Current price with arrow + % change - Custom card
        # ... (rest of the file unchanged until Current Price section)

        # ✅ Current price with arrow + % change - Custom card
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
                    change_str = f"+&#x20B9;{change:.2f} ({pct_change:+.2f}%)"
                    card_class = "current-price-card"
                elif change < 0:
                    arrow = "⬇️"
                    change_str = f"&#x20B9;{abs(change):.2f} ({pct_change:+.2f}%)"
                    card_class = "current-price-card negative"
                else:
                    arrow = "➡️"
                    change_str = "No change"
                    card_class = "current-price-card"

                st.markdown(
                    f'<div class="{card_class}">'
                    f'<div style="font-size: 1.5rem; margin-bottom: 0.5rem;">&#x20B9;{price:,.2f}</div>'
                    f'<div>{arrow} {change_str}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(f'<div class="current-price-card">&#x20B9;{price:,.2f}</div>', unsafe_allow_html=True)

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
            st.dataframe(df_display, height=500, width=1200, use_container_width=True)  # Added use_container_width for mobile

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
