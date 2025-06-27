import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf

st.set_page_config(page_title="Investment Calculator", layout="centered")

# Formatting helper
def to_currency(x): return f"${x:,.2f}"

st.title("📈 Monthly DCA Investment Simulator")

# Inputs
col1, col2 = st.columns(2)
with col1:
    principal = st.number_input("🧩 Starting Principal ($)", min_value=0.0, value=500.0, step=100.0)
    monthly = st.number_input("💵 Monthly Contribution ($)", min_value=0.0, value=500.0, step=50.0)
with col2:
    years = st.slider("🕰 Duration (years)", min_value=1, max_value=50, value=30)
    etfs = st.multiselect("📊 ETFs (max 5)", ["SPY", "QQQ", "JEPI", "JEPQ", "SGOV"], default=["SPY", "QQQ"])

# Portfolio allocation
alloc = {}
if etfs:
    st.subheader("⚖️ Portfolio Allocation")
    cols = st.columns(len(etfs))
    for i, ticker in enumerate(etfs):
        alloc[ticker] = cols[i].slider(f"{ticker} %", min_value=0, max_value=100, value=int(100/len(etfs)))
    total_pct = sum(alloc.values())
    if total_pct != 100:
        st.error(f"Total allocation must equal 100% (currently {total_pct}%)")

if st.button("🚀 Run Simulation") and etfs and total_pct == 100:
    months = years * 12
    dates = pd.date_range(end=pd.Timestamp.today(), periods=months, freq='M')
    
    df = pd.DataFrame(index=dates)
    df["Principal Paid"] = 0.0
    df["Portfolio Value"] = 0.0
    
    df["Contribution"] = monthly
    df.iloc[0, df.columns.get_loc("Contribution")] += principal

    balances = {t: 0.0 for t in etfs}
    alloc_frac = {t: p / 100 for t, p in alloc.items()}
    
    hist = {}
    for t in etfs:
        hist[t] = yf.Ticker(t).history(period=f"{years}y", interval="1mo")["Close"].reindex(dates, method='ffill')
    
    for i, date in enumerate(dates):
        # Contribute
        contrib = df["Contribution"].iloc[i]
        for t in etfs:
            balances[t] += contrib * alloc_frac[t] / hist[t].iloc[i]  # shares added

        # Revalue
        total_val = sum(balances[t] * hist[t].iloc[i] for t in etfs)
        df["Portfolio Value"].iloc[i] = total_val
        paid = principal + monthly * i
        df["Principal Paid"].iloc[i] = paid

    # Plot chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Principal Paid"], mode="lines", name="Principal Paid", line=dict(color="#1f77b4")))
    fig.add_trace(go.Scatter(x=df.index, y=df["Portfolio Value"], mode="lines", name="Portfolio Value", line=dict(color="#2ca02c")))
    fig.update_layout(title="Investment Value Over Time", xaxis_title="Date", yaxis_title="Amount ($)",
                      hovermode="x unified", template="simple_white")
    st.plotly_chart(fig, use_container_width=True)

    # Display summary metrics
    final = df["Portfolio Value"].iloc[-1]
    st.markdown(f"**📌 Final Value:** {to_currency(final)} &nbsp;&nbsp;&nbsp; **💰 Principal Paid:** {to_currency(df['Principal Paid'].iloc[-1])} &nbsp;&nbsp;&nbsp; **📈 Gain:** {to_currency(final - df['Principal Paid'].iloc[-1])}")

    # Show table
    yearly = df.resample("Y").last()
    yearly["Principal Paid"] = yearly["Principal Paid"]
    yearly["Gain"] = yearly["Portfolio Value"] - yearly["Principal Paid"]
    yearly_display = yearly[["Principal Paid", "Gain", "Portfolio Value"]].copy()
    yearly_display.index = yearly_display.index.year
    yearly_display.columns = ["Principal Paid", "Gain", "Total Value"]
    st.dataframe(yearly_display.style.format(to_currency))

else:
    if etfs:
        st.info("🎯 Set allocation to total 100%, then click **Run Simulation**")
