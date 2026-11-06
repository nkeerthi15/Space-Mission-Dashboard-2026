    )

    left, right = st.columns(2)

    with left:

        fig = px.bar(
            company_summary.head(15).sort_values("Launches"),
            x="Launches",
            y="Company",
            orientation="h",
            title="Top 15 Companies by Launches",
            color="Launches",
            color_continuous_scale=[
                "#A855F7",
                "#22D3EE"
            ]
        )

        show_chart(fig, 450)


    with right:

        fig = px.scatter(
            company_summary,
            x="Launches",
            y="Rockets",
            hover_name="Company",
            title="Company Launches vs Rocket Variety",
            color="Launches",
            color_continuous_scale=[
                "#14B8A6",
                "#A855F7"
            ],
            size="Launches"
        )

        show_chart(fig, 450)


    st.markdown("#### Company Rankings")

    st.dataframe(
        company_summary,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# TAB 5: ROCKETS
# =========================================================

with tabs[5]:

    st.markdown("### 🚀 Rocket Intelligence")

    rocket_summary = (
        filtered_df.groupby("Rocket")
        .agg(
            Launches=("Mission", "size"),
            Companies=("Company", "nunique")
        )
        .reset_index()
        .sort_values("Launches", ascending=False)
    )

    left, right = st.columns(2)

    with left:

        fig = px.bar(
            rocket_summary.head(15).sort_values("Launches"),
            x="Launches",
            y="Rocket",
            orientation="h",
            title="Most Frequently Used Rockets",
            color="Launches",
            color_continuous_scale=[
                "#9333EA",
                "#14B8A6"
            ]
        )

        show_chart(fig, 450)


    with right:

        rocket_status = (
            filtered_df.groupby("RocketStatus")
            .size()
            .reset_index(name="Count")
        )

        fig = px.pie(
            rocket_status,
            names="RocketStatus",
            values="Count",
            hole=0.6,
            title="Rocket Status Distribution",
            color_discrete_sequence=[
                PURPLE,
                CYAN,
                CORAL
            ]
        )

        show_chart(fig, 450)


    st.markdown("#### Rocket Rankings")

    st.dataframe(
        rocket_summary,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# TAB 6: COSTS
# =========================================================

with tabs[6]:

    st.markdown("### 💰 Space Mission Cost Analysis")

    cost_df = filtered_df.dropna(
        subset=["Price"]
    ).copy()

    if cost_df.empty:

        st.info(
            "No recorded mission cost data is available for these filters."
        )

    else:

        cost1, cost2, cost3 = st.columns(3)

        cost1.metric(
            "Missions With Recorded Cost",
            f"{len(cost_df):,}"
        )

        cost2.metric(
            "Average Mission Cost",
            format_money(cost_df["Price"].mean())
        )

        cost3.metric(
            "Median Mission Cost",
            format_money(cost_df["Price"].median())
        )

        left, right = st.columns(2)
