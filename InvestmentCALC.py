with tabs[0]:
    st.header("🧮 Compound Interest (Enhanced + DRIP + Real Data)")
    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        start = st.number_input("Initial Amount ($)", min_value=0.0, value=10000.0, step=100.0)
        contrib = st.number_input("Contribution Amount ($)", min_value=0.0, value=1000.0, step=100.0)
    with col2:
        period_type = st.selectbox("Period Type", ["Years", "Months"])
        duration = st.slider("Duration", min_value=1, max_value=600, value=120)  # months default
        rate = st.slider("Annual Interest Rate (%)", 0.0, 20.0, 7.0, 0.1)
    with col3:
        freq_label = st.selectbox("Compounding Frequency", ["Daily", "Monthly", "Quarterly", "Annually"])
        drip = st.checkbox("Reinvest Interest (DRIP)", True)

    freq_map = {"Daily":365, "Monthly":12, "Quarterly":4, "Annually":1}
    freq = freq_map[freq_label]

    if period_type == "Years":
        months = duration * 12
    else:
        months = duration

    if st.button("📊 Calculate"):
        periods = months * (freq/12)
        contribution_per_period = contrib * (12/freq) if drip else contrib/(freq)
        df = compound_interest(start, rate, duration if period_type=="Years" else months/12, freq, contrib*duration if not drip else contribution_per_period)
        df_display = df.copy()
        for col in ["Contributions", "Interest", "Ending Balance"]:
            df_display[col] = df_display[col].apply(currency_fmt)
        st.dataframe(df_display)

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df["Year"], y=df["Contributions"], name="Contrib"))
        fig.add_trace(go.Bar(x=df["Year"], y=df["Interest"], name="Interest"))
        fig.add_trace(go.Scatter(x=df["Year"], y=df["Ending Balance"], name="Ending Balance", mode="lines+markers"))
        fig.update_layout(barmode="stack", yaxis_title="USD", title="Growth Breakdown")
        st.plotly_chart(fig, use_container_width=True)
