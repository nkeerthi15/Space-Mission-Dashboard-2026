
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Launch Analytics",
    page_icon="🚀",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #07111f;
        color: #e8f1ff;
    }
    [data-testid="stMetric"] {
        background: #101f35;
        border: 1px solid #203957;
        padding: 18px;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "space_missions_dashboard.csv"
)

@st.cache_data
def load_data(path):
    data = pd.read_csv(path)
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")

    if "Year" not in data.columns:
        data["Year"] = data["Date"].dt.year

    return data


st.title("🚀 Launch Analytics")
st.caption("SPACE MISSION CONTROL  /  LAUNCH ACTIVITY")

if not DATA_PATH.exists():
    st.error(f"Dataset not found: {DATA_PATH}")
    st.info(
        "Check that the processed CSV exists in "
        "data/processed/space_missions_dashboard.csv."
    )
    st.stop()

df = load_data(DATA_PATH)

df = df.dropna(subset=["Year"]).copy()
df["Year"] = df["Year"].astype(int)

min_year = int(df["Year"].min())
max_year = int(df["Year"].max())

st.sidebar.header("Launch Filters")

year_range = st.sidebar.slider(
    "Select year range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
)

filtered = df[
    df["Year"].between(year_range[0], year_range[1])
].copy()

total = len(filtered)
successes = (
    filtered["MissionStatus"].eq("Success").sum()
)
failures = (
    filtered["MissionStatus"].eq("Failure").sum()
)
success_rate = successes / total * 100 if total else 0

c1, c2, c3, c4 = st.columns(4)

c1.metric("Launch Records", f"{total:,}")
c2.metric("Successful Missions", f"{successes:,}")
c3.metric("Failed Missions", f"{failures:,}")
c4.metric("Success Rate", f"{success_rate:.1f}%")

st.divider()

yearly = (
    filtered.groupby("Year")
    .size()
    .reset_index(name="Launches")
)

fig_year = px.area(
    yearly,
    x="Year",
    y="Launches",
    markers=True,
    title="Launch Activity by Year",
    template="plotly_dark",
)
fig_year.update_traces(
    line_color="#35d5ff",
    fillcolor="rgba(53,213,255,0.18)",
)
fig_year.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)

st.plotly_chart(fig_year, use_container_width=True)

left, right = st.columns(2)

with left:
    outcomes = (
        filtered["MissionStatus"]
        .fillna("Unknown")
        .value_counts()
        .rename_axis("Outcome")
        .reset_index(name="Missions")
    )

    fig_outcomes = px.pie(
        outcomes,
        names="Outcome",
        values="Missions",
        title="Mission Outcomes",
        hole=0.48,
        template="plotly_dark",
    )
    fig_outcomes.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(
        fig_outcomes,
        use_container_width=True,
    )

with right:
    monthly_df = filtered.dropna(subset=["Date"]).copy()
    monthly_df["Month"] = monthly_df["Date"].dt.month

    monthly = (
        monthly_df.groupby("Month")
        .size()
        .reindex(range(1, 13), fill_value=0)
        .rename("Launches")
        .reset_index()
    )

    fig_month = px.bar(
        monthly,
        x="Month",
        y="Launches",
        title="Launches by Calendar Month",
        template="plotly_dark",
    )
    fig_month.update_traces(marker_color="#9b8cff")
    fig_month.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(dtick=1),
    )
    st.plotly_chart(
        fig_month,
        use_container_width=True,
    )

st.subheader("Yearly Launch Summary")

if not filtered.empty:
    summary = (
        filtered.groupby("Year")
        .agg(
            Total_Launches=("Mission", "size"),
            Successful=("MissionStatus",
                        lambda x: x.eq("Success").sum()),
            Companies=("Company", "nunique"),
        )
        .reset_index()
        .sort_values("Year", ascending=False)
    )

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True,
    )

st.download_button(
    "⬇️ Download Filtered Launch Data",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="launch_analytics.csv",
    mime="text/csv",
)

st.caption("SPACE MISSION CONTROL | Launch Analytics")
