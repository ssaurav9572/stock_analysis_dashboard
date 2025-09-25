import streamlit as st
import plotly.graph_objects as go

def show_indicators(stock, company):
    st.header(f"📊 Technical Indicators - {company}")
    hist = stock.history(period="1y", interval="1d")

    if not hist.empty:
        # RSI
        delta = hist["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        hist["RSI"] = 100 - (100 / (1 + rs))

        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=hist.index, y=hist["RSI"], mode="lines", name="RSI"))
        fig_rsi.add_hline(y=70, line=dict(color="red", dash="dash"))
        fig_rsi.add_hline(y=30, line=dict(color="green", dash="dash"))
        fig_rsi.update_layout(yaxis_title="RSI")
        st.plotly_chart(fig_rsi, use_container_width=True)

        # MACD
        hist["EMA_12"] = hist["Close"].ewm(span=12, adjust=False).mean()
        hist["EMA_26"] = hist["Close"].ewm(span=26, adjust=False).mean()
        hist["MACD"] = hist["EMA_12"] - hist["EMA_26"]
        hist["Signal"] = hist["MACD"].ewm(span=9, adjust=False).mean()

        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=hist.index, y=hist["MACD"], mode="lines", name="MACD"))
        fig_macd.add_trace(go.Scatter(x=hist.index, y=hist["Signal"], mode="lines", name="Signal"))
        fig_macd.update_layout(yaxis_title="MACD")
        st.plotly_chart(fig_macd, use_container_width=True)

    else:
        st.warning("No historical data for indicators.")
