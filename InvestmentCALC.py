import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf

st.set_page_config(page_title="Investment Calculators", layout="wide", page_icon="📈")

def currency_fmt(x): return f"${x:,.2f}"

def compound_schedule(principal, annual_contrib, rate, years, freq):
    r = rate / 100 / freq
    balance = principal
    data = []
    for year in range(1, years+1):
        for _ in range(freq):
            balance = balance * (1 + r) + annual_contrib / freq
        interest = balance - (principal + annual_contrib*year)
        data.append({
            "Year": year,
            "Deposit": annual_contrib if year > 1 else principal + annual_contrib,
            "Interest": interest,
            "Ending Balance": balance
        })
    return pd.DataFrame(data)

def sip_schedule(start_principal, monthly_contrib, rate, years):
    r = rate / 100 / 12
    balance = start_principal
    data = []
    for m in range(1, years * 12 + 1):
        balance = balance * (1 + r) + monthly_contrib
        data.append({
            "Month": m,
            "Total Contributed": start_principal + monthly_contrib * m,
            "Balance": balance
        })
    return pd.DataFrame(data)

st.title("📊 Investment Calculators")
tabs = st.tabs(["Compound Interest", "DCA / SIP", "ETF Performance"])

# --- Compound Interest Tab ---
with tabs[0]:
    st.header("🧮 Compound Interest Calculator")
    principal = st.number_input("Initial Investment ($)", min_value=0.0, value=1000.0)
    annual_contrib = st.number_input("Annual Contribution ($)", min_value=0.0, value=1200.0)
    rate = st.slider("Expected Annual Return (%)", 0.0, 20.0, 7.0)
    years = st.slider("Investment Duration (Years)", 1, 50, 20)
    freq = st.selectbox("Compounding Frequency", [1, 4, 12],
                        format_func=lambda x: {1: "Yearly", 4: "Quarterly", 12: "Monthly"}[x])
    if st.button("Calculate Compound Interest"):
        df = compound_schedule(principal, annual_contrib, rate, years, freq)
        st.line_chart(df.set_index("Year")["Ending Balance"])
        st.dataframe(df.style.format({
            "Deposit": "${:,.2f}",
            "Interest": "${:,.2f}",
            "Ending Balance": "${:,.2f}"
        }), use_container_width=True)

# --- DCA / SIP Tab ---
with tabs[1]:
    st.header("💸 DCA / SIP with Starting Principal")
    start_principal = st.number_input("Starting Investment ($)", min_value=0.0, value=500.0)
    monthly = st.number_input("Monthly Contribution ($)", min_value=0.0, value=500.0)
    rate2 = st.slider("Expected Annual Return (%)", 0.0, 20.0, 8.0)
    years2 = st.slider("Duration (Years)", 1, 50, 10)
    if st.button("Calculate DCA"):
        df2 = sip_schedule(start_principal, monthly, rate2, years2)
        st.line_chart(df2.set_index("Month")["Balance"])
        st.dataframe(df2.style.format({
            "Total Contributed": "${:,.2f}",
            "Balance": "${:,.2f}"
        }), use_container_width=True)

# --- ETF Performance Tab ---
with tabs[2]:
    st.header("📈 Live ETF Performance Simulator")
    tickers = st.multiselect("Select ETFs", ["SPY", "QQQ", "JEPI", "JEPQ"], default=["SPY", "QQQ"])
    invest_method = st.selectbox("Investment Method", ["Lump Sum", "Monthly DCA"])
    amount = st.number_input("Total Investment Amount ($)", min_value=0.0, value=10000.0)
    months = st.slider("Duration (Months)", 1, 120, 12)
    drip = st.checkbox("Enable DRIP (reinvest dividends)", True)

    if st.button("🚀 Simulate ETF Performance"):
        for ticker in tickers:
            data = yf.Ticker(ticker).history(period=f"{months}mo", interval="1mo")
            prices = data['Close']
            if prices.empty:
                st.warning(f"No data found for {ticker}.")
                continue

            if invest_method == "Lump Sum":
                shares = amount / prices.iloc[0]
                final_value = shares * prices.iloc[-1]
            else:
                shares = 0
                for price in prices:
                    monthly_amount = amount / months
                    shares += (monthly_amount / price) * (1 + (0.0 if not drip else 0))
                final_value = shares * prices.iloc[-1]

            profit = final_value - amount
            roi = profit / amount * 100

            col1, col2 = st.columns(2)
            with col1:
                st.subheader(f"{ticker} Summary")
                st.metric("Final Value", currency_fmt(final_value))
                st.metric("Profit", currency_fmt(profit))
                st.metric("ROI (%)", f"{roi:.2f}%")
            with col2:
                fig = go.Figure(go.Scatter(
                    x=prices.index, y=prices.values, mode="lines", name=ticker))
                fig.update_layout(xaxis_title="Date", yaxis_title="Price ($)")
                st.plotly_chart(fig, use_container_width=True)
