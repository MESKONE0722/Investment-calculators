import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Investment Calculator", layout="wide")

def currency_fmt(x):
    return f"${x:,.2f}"

def compound_schedule(principal, annual_contrib, rate, years, freq):
    r = rate / 100 / freq
    balance = principal
    data = []
    for year in range(1, years + 1):
        for _ in range(freq):
            balance = balance * (1 + r) + annual_contrib / freq
        total_contrib = principal + annual_contrib * year
        interest = balance - principal - (annual_contrib * year)
        data.append({
            "Year": year,
            "Deposit": annual_contrib if year > 1 else principal + annual_contrib,
            "Interest": interest,
            "Ending Balance": balance
        })
    return pd.DataFrame(data)

st.title("📈 Compound Interest Calculator")
st.markdown("### Accumulation Schedule")

# Inputs
col1, col2 = st.columns(2)
with col1:
    principal = st.number_input("Initial Investment", value=20000.0, step=1000.0, format="%.2f")
    annual_contrib = st.number_input("Annual Contribution", value=12000.0, step=1000.0, format="%.2f")
    years = st.slider("Years to Grow", 1, 50, 10)
with col2:
    rate = st.slider("Annual Interest Rate (%)", 0.0, 15.0, 8.0, step=0.1)
    freq_label = st.selectbox("Compounding Frequency", ["Annually", "Quarterly", "Monthly"])
    freq_map = {"Annually": 1, "Quarterly": 4, "Monthly": 12}
    freq = freq_map[freq_label]

if st.button("📊 Calculate"):
    df = compound_schedule(principal, annual_contrib, rate, years, freq)

    # Pie chart breakdown
    final = df["Ending Balance"].iloc[-1]
    total_contrib = principal + annual_contrib * years
    total_interest = final - total_contrib

    pie_chart = go.Figure(data=[go.Pie(
        labels=["Starting Amount", "Total Contributions", "Interest"],
        values=[principal, annual_contrib * years, total_interest],
        marker=dict(colors=["#3366cc", "#99cc00", "#cc3333"])
    )])
    st.plotly_chart(pie_chart, use_container_width=True)

    # Bar chart
    st.markdown("### Growth Over Time")
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Starting Amount", x=df["Year"], y=[principal]*years, marker_color="#3366cc"))
    fig.add_trace(go.Bar(name="Contributions", x=df["Year"], y=[annual_contrib]*years, marker_color="#99cc00"))
    fig.add_trace(go.Bar(name="Interest", x=df["Year"], y=df["Interest"], marker_color="#cc3333"))
    fig.update_layout(barmode='stack', yaxis_title="USD", xaxis_title="Year")
    st.plotly_chart(fig, use_container_width=True)

    # Table display
    st.markdown("### Annual Schedule")
    df_display = df.copy()
    df_display["Deposit"] = df_display["Deposit"].apply(currency_fmt)
    df_display["Interest"] = df_display["Interest"].apply(currency_fmt)
    df_display["Ending Balance"] = df_display["Ending Balance"].apply(currency_fmt)
    st.dataframe(df_display, use_container_width=True)
