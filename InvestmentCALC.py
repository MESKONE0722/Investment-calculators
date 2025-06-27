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

def dividend_income(amount, yield_pct, payout, drip):
    annual_income = amount * (yield_pct / 100)
    monthly_income = annual_income / 12
    return annual_income, monthly_income

def sip_calculator(monthly, rate, years):
    schedule = []
    r = rate / 100 / 12
    balance = 0
    for m in range(1, years * 12 + 1):
        balance = balance * (1 + r) + monthly
        schedule.append([m // 12, m, monthly * m, balance])
    return pd.DataFrame(schedule, columns=["Year", "Month", "Contributed", "Balance"])

def fire_calc(income, expenses, rate, withdrawal):
    savings_rate = (income - expenses) / income
    annual_savings = income * savings_rate
    net_needed = expenses / (withdrawal / 100)
    balance = 0
    year = 0
    r = rate / 100
    results = []
    while balance < net_needed:
        balance = balance * (1 + r) + annual_savings
        results.append([year, balance])
        year += 1
    return pd.DataFrame(results, columns=["Year", "Savings"])

def loan_payoff(amount, rate, payment, extra):
    balance = amount
    r = rate / 100 / 12
    results = []
    month = 0
    while balance > 0 and month < 600:
        interest = balance * r
        principal = min(payment + extra - interest, balance)
        balance -= principal
        results.append([month + 1, interest, principal, balance])
        month += 1
    return pd.DataFrame(results, columns=["Month", "Interest", "Principal", "Balance"])

def roi_calc(initial, final, years):
    profit = final - initial
    roi_pct = (profit / initial) * 100
    return profit, roi_pct

st.title("📊 Investment Calculators")
tabs = st.tabs([
    "Compound Interest", "Dividend Income", "SIP / DCA", 
    "FIRE", "Loan Payoff", "ROI Calculator"
])

with tabs[0]:
    st.header("🧮 Compound Interest")
    start = st.number_input("Starting Amount", value=10000.0)
    rate = st.number_input("Annual Interest Rate (%)", value=7.0)
    years = st.number_input("Years", value=10, step=1)
    freq = st.selectbox("Compounding Frequency", [1, 4, 12], index=2)
    contrib = st.number_input("Annual Contribution", value=12000.0)

    df = compound_interest(start, rate, years, freq, contrib)
    df_display = df.copy()
    for col in ["Contributions", "Interest", "Ending Balance"]:
        df_display[col] = df_display[col].apply(currency_fmt)
    st.dataframe(df_display)

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Contributions", x=df["Year"], y=df["Contributions"]))
    fig.add_trace(go.Bar(name="Interest", x=df["Year"], y=df["Interest"]))
    fig.update_layout(barmode="stack", title="Accumulation Over Time", yaxis_title="USD")
    st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    st.header("💰 Dividend Income")
    inv = st.number_input("Investment Amount", value=50000.0)
    yield_pct = st.number_input("Dividend Yield (%)", value=4.5)
    payout = st.selectbox("Payout Frequency", ["Monthly", "Quarterly"])
    drip = st.checkbox("DRIP (Reinvest Dividends)", value=False)

    annual, monthly = dividend_income(inv, yield_pct, payout, drip)
    st.metric("📆 Estimated Annual Income", currency_fmt(annual))
    st.metric("📅 Monthly Equivalent", currency_fmt(monthly))

with tabs[2]:
    st.header("📊 SIP / DCA Calculator")
    monthly = st.number_input("Monthly Investment", value=1000.0)
    sip_rate = st.number_input("Expected Annual Return (%)", value=8.0)
    sip_years = st.number_input("Years", value=10)

    df_sip = sip_calculator(monthly, sip_rate, sip_years)
    df_sip["Balance"] = df_sip["Balance"].apply(currency_fmt)
    st.dataframe(df_sip.tail(12))

    st.plotly_chart(go.Figure([
        go.Scatter(x=df_sip["Month"], y=df_sip["Balance"], mode="lines", name="Portfolio Value")
    ]), use_container_width=True)

with tabs[3]:
    st.header("📆 FIRE Calculator")
    income = st.number_input("Annual Income", value=80000.0)
    expenses = st.number_input("Annual Expenses", value=40000.0)
    fire_rate = st.number_input("Expected Return (%)", value=7.0)
    withdrawal = st.number_input("Safe Withdrawal Rate (%)", value=4.0)

    df_fire = fire_calc(income, expenses, fire_rate, withdrawal)
    st.metric("🔥 Years to FIRE", df_fire["Year"].iloc[-1])
    st.plotly_chart(go.Figure([
        go.Scatter(x=df_fire["Year"], y=df_fire["Savings"], mode="lines", name="Savings")
    ]), use_container_width=True)

with tabs[4]:
    st.header("🔁 Loan Payoff Calculator")
    loan_amt = st.number_input("Loan Amount", value=25000.0)
    loan_rate = st.number_input("Interest Rate (%)", value=6.0)
    loan_pay = st.number_input("Monthly Payment", value=500.0)
    extra = st.number_input("Extra Monthly Payment", value=0.0)

    df_loan = loan_payoff(loan_amt, loan_rate, loan_pay, extra)
    df_loan["Balance"] = df_loan["Balance"].apply(lambda x: max(x, 0))
    df_loan["Balance"] = df_loan["Balance"].apply(currency_fmt)
    st.dataframe(df_loan.head(24))

    st.plotly_chart(go.Figure([
        go.Scatter(x=df_loan["Month"], y=df_loan["Balance"], mode="lines", name="Balance")
    ]), use_container_width=True)

with tabs[5]:
    st.header("💹 ROI Calculator")
    initial = st.number_input("Initial Investment", value=10000.0)
    final = st.number_input("Final Value", value=15000.0)
    time_held = st.number_input("Time Held (Years)", value=2.0)

    profit, roi_pct = roi_calc(initial, final, time_held)
    st.metric("💵 Profit", currency_fmt(profit))
    st.metric("📈 ROI (%)", f"{roi_pct:.2f}%")
