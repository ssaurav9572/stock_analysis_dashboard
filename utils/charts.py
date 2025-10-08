import streamlit as st
import plotly.graph_objects as go

def show_charts(stock, company):
    st.header(f"📈 Charts - {company}")

    col1, col2 = st.columns([1, 1])
    with col1:
        chart_type = st.radio("Chart Type", ["Line Chart", "Candlestick"], index=0)
    with col2:
        time_ranges = {
            "1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo",
            "1 Year": "1y", "5 Years": "5y", "Max": "max"
        }
        time_choice = st.selectbox("Time Range", list(time_ranges.keys()), index=3)
        period = time_ranges[time_choice]

    hist = stock.history(period=period, interval="1d")

    if not hist.empty:
        # Moving averages
        hist["SMA_50"] = hist["Close"].rolling(window=50).mean()
        hist["SMA_200"] = hist["Close"].rolling(window=200).mean()
        hist["EMA_50"] = hist["Close"].ewm(span=50, adjust=False).mean()
        hist["EMA_200"] = hist["Close"].ewm(span=200, adjust=False).mean()

        st.subheader("Moving Averages")
        col3, col4 = st.columns([1, 1])
        with col3:
            show_sma50 = st.checkbox("Show 50-day SMA", value=True)
            show_sma200 = st.checkbox("Show 200-day SMA", value=True)
        with col4:
            show_ema50 = st.checkbox("Show 50-day EMA", value=False)
            show_ema200 = st.checkbox("Show 200-day EMA", value=False)

        dark_template = {
            "layout": {
                "paper_bgcolor": "#1e293b",
                "plot_bgcolor": "#1e293b",
                "font": {"color": "#e2e8f0"},
                "xaxis": {"gridcolor": "#334155", "color": "#e2e8f0"},
                "yaxis": {"gridcolor": "#334155", "color": "#e2e8f0"}
            }
        }

        if chart_type == "Line Chart":
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode="lines", name="Close Price", line=dict(color="#60a5fa")))
            if show_sma50: fig.add_trace(go.Scatter(x=hist.index, y=hist["SMA_50"], name="50-day SMA", line=dict(color="#94a3b8")))
            if show_sma200: fig.add_trace(go.Scatter(x=hist.index, y=hist["SMA_200"], name="200-day SMA", line=dict(color="#64748b")))
            if show_ema50: fig.add_trace(go.Scatter(x=hist.index, y=hist["EMA_50"], name="50-day EMA", line=dict(color="#3b82f6")))
            if show_ema200: fig.add_trace(go.Scatter(x=hist.index, y=hist["EMA_200"], name="200-day EMA", line=dict(color="#1d4ed8")))
            fig.update_layout(
                title=f"{company} - Line Chart",
                yaxis_title="Price (&#x20B9;)",
                template=dark_template,
                showlegend=True,
                legend=dict(bgcolor="#334155", bordercolor="#475569", font=dict(color="#e2e8f0"))
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = go.Figure(data=[go.Candlestick(
                x=hist.index, open=hist['Open'], high=hist['High'],
                low=hist['Low'], close=hist['Close'],
                increasing_line_color="#10b981", decreasing_line_color="#ef4444",
                name="Candlestick"
            )])
            if show_sma50: fig.add_trace(go.Scatter(x=hist.index, y=hist["SMA_50"], name="50-day SMA", line=dict(color="#94a3b8")))
            if show_sma200: fig.add_trace(go.Scatter(x=hist.index, y=hist["SMA_200"], name="200-day SMA", line=dict(color="#64748b")))
            if show_ema50: fig.add_trace(go.Scatter(x=hist.index, y=hist["EMA_50"], name="50-day EMA", line=dict(color="#3b82f6")))
            if show_ema200: fig.add_trace(go.Scatter(x=hist.index, y=hist["EMA_200"], name="200-day EMA", line=dict(color="#1d4ed8")))
            fig.update_layout(
                xaxis_rangeslider_visible=False,
                title=f"{company} - Candlestick Chart",
                yaxis_title="Price (&#x20B9;)",
                template=dark_template,
                showlegend=True,
                legend=dict(bgcolor="#334155", bordercolor="#475569", font=dict(color="#e2e8f0"))
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No historical data found for this ticker.")
