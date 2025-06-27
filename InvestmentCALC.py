import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import yfinance as yf
import time

st.set_page_config(page_title="Investment Calculators", layout="wide", page_icon="📈")

def currency_fmt(x): return f"${x:,.2f}"

def compound_schedule(principal, annual_contrib, rate, years, freq):
    r = rate / 100 / freq
    balance = principal
    data = []
    for year in range(1, years + 1):
        for _ in range(freq):
            balance = balance * (1 + r) + annual_contrib / freq
        interest = balance - (principal + annual_contrib * year)
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

# Compound Interest code remains unchanged...

# --- DCA / SIP Tab ---
with tabs[1]:
    st.header("💸 DCA / SIP with Starting Principal")
    start_principal = st.number_input("Starting Principal ($)", min_value=0.0, value=500.0)
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

# ETF Performance tab remains unchanged...
