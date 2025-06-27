import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf

st.set_page_config(page_title="Investment Calculators", layout="wide", page_icon="📈")
st.experimental_singleton.clear()  # clear cache to fetch fresh data

def currency_fmt(x): return f"${x:,.2f}"

def compound_schedule(principal, annual_contrib, rate, years, freq):
    r = rate/100/freq; balance = principal
    data = []
    for year in range(1, years+1):
        for _ in range(freq):
            balance = balance*(1+r) + annual_contrib/freq
        interest = balance - (principal + annual_contrib*year)
        data.append({"Year":year, "Deposit":annual_contrib if year>1 else principal+annual_contrib,
                     "Interest":interest, "Ending Balance":balance})
    return pd.DataFrame(data)

def sip_schedule(monthly_contrib, rate, years):
    r = rate/100/12; balance = 0; data=[]
    for m in range(1, years*12+1):
        balance = balance*(1+r) + monthly_contrib
        data.append({"Month":m, "Contributed":monthly_contrib*m, "Balance":balance})
    return pd.DataFrame(data)

st.title("📊 Investment Calculators")

tabs = st.tabs(["Compound Interest", "DCA / SIP", "ETF Performance"])

# --- Compound Interest Tab ---
with tabs[0]:
    # ... same as previous code for compound interest ...

# --- DCA / SIP Tab ---
with tabs[1]:
    # ... same as previous code for DCA ...

# --- ETF Performance Tab ---
with tabs[2]:
    st.header("📉 Live ETF Performance Simulator")
    tickers = st.multiselect("Select ETFs", ["SPY","QQQ","JEPI","JEPQ"], default=["SPY","QQQ"])
    invest_method = st.selectbox("Strategy", ["Lump Sum", "Monthly DCA"])
    amount = st.number_input("Investment Amount ($)", min_value=0.0, value=10000.0)
    months = st.slider("Duration (Months)", 1, 120, 12)
    drip = st.checkbox("Enable DRIP", True)
    auto_refresh = st.checkbox("Auto-refresh Prices every 5s", True)

    if auto_refresh:
        st.experimental_rerun()  # refresh to get new live data

    if st.button("🚀 Simulate ETF Performance"):
        col1, col2 = st.columns(2)
        for ticker in tickers:
            data = yf.Ticker(ticker).history(period=f"{months}mo", interval="1mo")
            prices = data['Close']
            if invest_method == "Lump Sum":
                shares = amount / prices.iloc[0]
                final_value = shares * prices.iloc[-1]
            else:
                shares = 0; total = 0
                for price in prices:
                    monthly_amount = amount / months
                    shares += (monthly_amount / price) * (1 + (0.0 if not drip else 0))
                    total += monthly_amount
                final_value = shares * prices.iloc[-1]
            profit = final_value - amount
            roi = profit / amount * 100

            with col1:
                st.subheader(f"{ticker} Summary")
                st.metric("🧮 Final Value", currency_fmt(final_value))
                st.metric("💵 Profit", currency_fmt(profit))
                st.metric("📈 ROI (%)", f"{roi:.2f}%")
            with col2:
                fig = go.Figure([go.Scatter(x=prices.index, y=prices.values, mode="lines", name=ticker)])
                fig.update_layout(title=f"{ticker} Price History", yaxis_title="Price ($)", xaxis_title="Date")
                st.plotly_chart(fig, use_container_width=True)
