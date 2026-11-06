
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Space Mission Control",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# SPACE-THEME STYLING
# --------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #080D1B;
        color: #E5EAF5;
    }

    [data-testid="stSidebar"] {
        background-color: #0D1528;
        border-right: 1px solid #23324A;
    }

    h1, h2, h3 {
        color: #E5EAF5;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #111D34, #15172E);
        border: 1px solid #263957;
        padding: 18px;
        border-radius: 12px;
    }

    [data-testid="stMetricLabel"] {
        color: #A8B7D1;
    }

    [data-testid="stMetricValue"] {
        color: #67E8F9;
    }

    div[data-testid="stPlotlyChart"] {
        background-color: #0D1528;
        border: 1px solid #23324A;
        border-radius: 12px;
        padding: 8px;
    }

    div.stButton > button,
    div.stDownloadButton > button {
        background-color: #172844;
        color: #67E8F9;
        border: 1px solid #36577B;
        border-radius: 8px;
    }

    hr {
        border-color: #263957;
    }

    .hero {
        background: linear-gradient(120deg, #111D34, #21183D);
        border: 1px solid #33446A;
        border-radius: 16px;
        padding: 26px;
        margin-bottom: 22px;
    }

    .hero-label {
        color: #67E8F9;
        letter-spacing: 3px;
        font-size: 12px;
        font-weight: 700;
    }

    .hero-title {
        color: #F0F5FF;
        font-size: 32px;
        font-weight: 750;
        margin-top: 8px;
    }

    .hero-subtitle {
        color: #B8C5DC;
        font-size: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "processed"
    / "space_missions_dashboard.csv"
)


@st.cache_data
def load_data(path):
    data = pd.read_csv(path)

    data["Date"] = pd.to_datetime(
        data["Date"], errors="coerce"
    )

    data["Price"] = pd.to_numeric(
        data["Price"], errors="coerce"
    )

    data["Year"] = data["Date"].dt.year
    data["Month"] = data["Date"].dt.month

    return data


st.sidebar.markdown("## 🚀 MISSION CONTROL")
st.sidebar.caption("SPACE DATA INTELLIGENCE")
st.sidebar.divider()

if not DATA_PATH.exists():
    st.error(f"Dataset not found: {DATA_PATH}")
    st.info(
        "Check that your CSV exists in "
        "data/processed/space_missions_dashboard.csv."
    )
    st.stop()

df = load_data(str(DATA_PATH))

if df.empty or df["Year"].dropna().empty:
    st.error("The dataset contains no usable launch dates.")
    st.stop()

# --------------------------------------------------
# GLOBAL FILTERS
# --------------------------------------------------
st.sidebar.subheader("Mission Filters")

min_year = int(df["Year"].min())
max_year = int(df["Year"].max())

if min_year == max_year:
    selected_years = (min_year, max_year)
    st.sidebar.info(f"Launch year: {min_year}")
else:
    selected_years = st.sidebar.slider(
        "Launch year range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
    )

company_options = sorted(df["Company"].dropna().unique())

selected_companies = st.sidebar.multiselect(
    "Companies",
    options=company_options,
    placeholder="All companies",
)

status_options = sorted(
    df["MissionStatus"].dropna().unique()
)

selected_statuses = st.sidebar.multiselect(
    "Mission outcomes",
    options=status_options,
    placeholder="All outcomes",
)

# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------
filtered = df[
    df["Year"].between(
        selected_years[0],
        selected_years[1],
    )
].copy()

if selected_companies:
    filtered = filtered[
        filtered["Company"].isin(selected_companies)
    ]

if selected_statuses:
    filtered = filtered[
        filtered["MissionStatus"].isin(selected_statuses)
    ]

st.sidebar.divider()
st.sidebar.caption("Historical mission records")
st.sidebar.caption("Data coverage depends on the source dataset.")

# --------------------------------------------------
# HERO HEADER
# --------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="hero-label">SPACE DATA INTELLIGENCE PLATFORM</div>
        <div class="hero-title">🚀 Space Mission Control</div>
        <div class="hero-subtitle">
            Explore launch history, mission outcomes,
            organizations and recorded rocket costs.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning(
        "No missions match your filters. "
        "Change the selections in the sidebar."
    )
    st.stop()

# --------------------------------------------------
# KEY PERFORMANCE INDICATORS
# --------------------------------------------------
st.subheader("Mission Overview")

total_missions = len(filtered)

successful = (
    filtered["MissionStatus"] == "Success"
).sum()

classified = filtered["MissionStatus"].notna().sum()

success_rate = (
    successful / classified * 100
    if classified
    else 0
)

company_count = filtered["Company"].nunique()

priced = filtered["Price"].dropna()

k1, k2, k3, k4 = st.columns(4)

k1.metric("TOTAL LAUNCH RECORDS", f"{total_missions:,}")
k2.metric("SUCCESSFUL MISSIONS", f"{successful:,}")
k3.metric("EXACT SUCCESS RATE", f"{success_rate:.1f}%")
k4.metric("COMPANIES REPRESENTED", f"{company_count:,}")

st.caption(
    "Success rate counts only records labeled exactly "
    "'Success'. Partial successes are not counted as full successes."
)

# --------------------------------------------------
# YEARLY LAUNCH TREND
# --------------------------------------------------
st.divider()
st.subheader("📈 Launch Activity Timeline")

yearly = (
    filtered.dropna(subset=["Year"])
    .groupby("Year")
    .size()
    .reset_index(name="Launches")
)

fig_year = px.area(
    yearly,
    x="Year",
    y="Launches",
    markers=True,
    template="plotly_dark",
    color_discrete_sequence=["#22D3EE"],
)

fig_year.update_layout(
    paper_bgcolor="#0D1528",
    plot_bgcolor="#0D1528",
    font_color="#E5EAF5",
    margin=dict(l=15, r=15, t=25, b=15),
    xaxis_title="Launch year",
    yaxis_title="Number of launch records",
)

st.plotly_chart(fig_year, use_container_width=True)

# --------------------------------------------------
# MISSION OUTCOMES AND COMPANY RANKINGS
# --------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("🛰️ Mission Outcomes")

    outcome_data = (
        filtered["MissionStatus"]
        .value_counts()
        .rename_axis("Status")
        .reset_index(name="Missions")
    )

    if not outcome_data.empty:
        fig_outcomes = px.pie(
            outcome_data,
            names="Status",
            values="Missions",
            hole=0.58,
            template="plotly_dark",
            color_discrete_sequence=[
                "#22D3EE",
                "#A78BFA",
                "#F59E0B",
                "#F87171",
                "#94A3B8",
            ],
        )

        fig_outcomes.update_layout(
            paper_bgcolor="#0D1528",
            plot_bgcolor="#0D1528",
            font_color="#E5EAF5",
            margin=dict(l=10, r=10, t=20, b=10),
        )

        st.plotly_chart(
            fig_outcomes,
            use_container_width=True,
        )

with right:
    st.subheader("🏢 Leading Companies")

    company_data = (
        filtered["Company"]
        .value_counts()
        .head(10)
        .sort_values()
        .reset_index()
    )

    company_data.columns = ["Company", "Launches"]

    if not company_data.empty:
        fig_companies = px.bar(
            company_data,
            x="Launches",
            y="Company",
            orientation="h",
            template="plotly_dark",
            color="Launches",
            color_continuous_scale=[
                "#164E63",
                "#22D3EE",
                "#A78BFA",
            ],
        )

        fig_companies.update_layout(
            paper_bgcolor="#0D1528",
            plot_bgcolor="#0D1528",
            font_color="#E5EAF5",
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=20, b=10),
        )

        st.plotly_chart(
            fig_companies,
            use_container_width=True,
        )

# --------------------------------------------------
# COST SUMMARY
# --------------------------------------------------
st.divider()
st.subheader("💰 Recorded Rocket Costs")

c1, c2, c3 = st.columns(3)

c1.metric("MISSIONS WITH RECORDED COST", f"{len(priced):,}")

if priced.empty:
    c2.metric("MEDIAN RECORDED PRICE", "Unavailable")
    c3.metric("AVERAGE RECORDED PRICE", "Unavailable")
else:
    c2.metric(
        "MEDIAN RECORDED PRICE",
        f"${priced.median():,.2f}M",
    )
    c3.metric(
        "AVERAGE RECORDED PRICE",
        f"${priced.mean():,.2f}M",
    )

st.caption(
    "Costs are in millions of USD as described by the dataset. "
    "Missing prices are not estimated."
)

# --------------------------------------------------
# RECENT MISSION RECORDS
# --------------------------------------------------
st.divider()
st.subheader("📡 Mission Records")

recent = (
    filtered.sort_values("Date", ascending=False)
    .head(10)
)

st.dataframe(
    recent[
        [
            "Date",
            "Company",
            "Location",
            "Rocket",
            "Mission",
            "MissionStatus",
            "Price",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

download_data = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Download filtered mission data",
    data=download_data,
    file_name="space_missions_filtered.csv",
    mime="text/csv",
)

st.divider()
st.caption(
    "SPACE MISSION CONTROL  |  Historical analytics prototype"
)
