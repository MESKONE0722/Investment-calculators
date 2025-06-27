import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Investment Calculators", layout="wide")

def currency_fmt(x):
    return f"${x:,.2f}"

def compound_interest(start, rate, years, freq, contrib):
    schedule = []
    balance = start
    r = rate / 100 / freq
    for y in range(1, years + 1):
        for _ in range(freq):
            balance = balance * (1 + r) + contrib / freq
        interest = balance - start - contrib * y
        schedule.append([y, contrib * y, interest, balance])
    return pd.DataFrame(schedule, columns=["Year", "Contributions", "Interest", "Ending Balance"])

st.title("📊 Investment Calculators")

# Define tab structure BEFORE using it
tabs = st.tabs([
    "Compound Interest", "Dividend Income", "SIP / DCA",
    "FIRE", "Loan Payoff", "ROI Calculator"
])

with tabs[0]:
    st.header("🧮 Compound Interest (Enhanced)")

    # Layout controls
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        start = st.number_input("Initial Amount ($)", min_value=0.0, value=10000.0, step=100.0)
        contrib = st.number_input("Annual Contribution ($)", min_value=0.0, value=12000.0, step=100.0)
    with col2:
        period_type = st.selectbox("Period Type", ["Years", "Months"])
        duration = st.slider("Duration", min_value=1, max_value=50, value=10)
        rate = st.slider("Annual Interest Rate (%)", 0.0, 20.0, 7.0, 0.1)
    with col3:
        freq_label = st.selectbox("Compounding Frequency", ["Daily", "Monthly", "Quarterly", "Annually"])
        drip = st.checkbox("Reinvest Interest (DRIP)", True)

    # Convert to usable values
    freq_map = {"Daily": 365, "Monthly": 12, "Quarterly": 4, "Annually": 1}
    freq = freq_map[freq_label]
    years = duration if period_type == "Years" else duration / 12

    if st.button("📊 Calculate"):
        df = compound_interest(start, rate, int(np.ceil(years)), freq, contrib)
        df_display = df.copy()
        for col in ["Contributions", "Interest", "Ending Balance"]:
            df_display[col] = df_display[col].apply(currency_fmt)
        st.dataframe(df_display, use_container_width=True)

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df["Year"], y=df["Contributions"], name="Contributions"))
        fig.add_trace(go.Bar(x=df["Year"], y=df["Interest"], name="Interest"))
        fig.add_trace(go.Scatter(x=df["Year"], y=df["Ending Balance"], name="Ending Balance", mode="lines+markers"))
        fig.update_layout(barmode="stack", yaxis_title="USD", title="Growth Breakdown")
        st.plotly_chart(fig, use_container_width=True)
