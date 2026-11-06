
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Space Mission Control",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# 2. DEEP SPACE AURORA THEME
# =========================================================

st.markdown("""
<style>

/* Main background: rocket and Earth */

.stApp {
    background:
        linear-gradient(
            rgba(8, 13, 35, 0.48),
            rgba(15, 23, 42, 0.58)
        ),
        url("https://images.unsplash.com/photo-1517976487492-5750f3195933?auto=format&fit=crop&w=2200&q=90");

    background-size: cover;
    background-position: center center;
    background-attachment: fixed;
    background-repeat: no-repeat;
}

[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {
    background: transparent;
}


/* Compact page layout */
.block-container {
    max-width: 100%;
    padding-top: 0.7rem;
    padding-bottom: 0.4rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Hide sidebar */
[data-testid="stSidebar"] {
    display: none;
}

/* Typography */
h1, h2, h3, h4 {
    color: #F8FAFC !important;
}

p, label {
    color: #CBD5E1;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: rgba(30, 41, 59, 0.78);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(168, 85, 247, 0.42);
    border-radius: 15px;
    padding: 10px 15px;
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.25);
    transition: all 0.2s ease;
}

[data-testid="stMetric"]:hover {
    border-color: #14B8A6;
    box-shadow: 0 0 18px rgba(20, 184, 166, 0.25);
    transform: translateY(-2px);
}

[data-testid="stMetricLabel"] {
    color: #C4B5FD !important;
    font-size: 13px !important;
}

[data-testid="stMetricValue"] {
    color: #F8FAFC !important;
    font-weight: 750;
    font-size: 25px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(30, 41, 59, 0.82);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 14px;
    padding: 5px;
    gap: 5px;
}

.stTabs [data-baseweb="tab"] {
    color: #CBD5E1;
    border-radius: 10px;
    padding: 8px 12px;
    font-size: 13px;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(168, 85, 247, 0.18);
    color: #FFFFFF;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(110deg, #9333EA, #6D28D9) !important;
    color: #FFFFFF !important;
    box-shadow: 0 0 14px rgba(168, 85, 247, 0.35);
}

/* Input fields */
[data-baseweb="select"] > div {
    background: rgba(30, 41, 59, 0.9);
    border-color: rgba(148, 163, 184, 0.3);
    color: #F8FAFC;
    border-radius: 10px;
}

[data-testid="stSlider"] {
    padding-top: 0;
    padding-bottom: 0;
}

/* Buttons */
.stButton button,
.stDownloadButton button {
    background: linear-gradient(110deg, #9333EA, #0D9488);
    color: #FFFFFF;
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 10px;
    font-weight: 650;
}

.stButton button:hover,
.stDownloadButton button:hover {
    border-color: #14B8A6;
    box-shadow: 0 0 16px rgba(20, 184, 166, 0.3);
    color: #FFFFFF;
}

/* Chart containers */
[data-testid="stPlotlyChart"] {
    background: rgba(15, 23, 42, 0.72);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 15px;
    padding: 4px;
}

/* Tables */
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    background: rgba(30, 41, 59, 0.75);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 13px;
}

/* Compact spacing */
[data-testid="stVerticalBlock"] {
    gap: 0.55rem;
}

hr {
    border-color: rgba(148, 163, 184, 0.2);
}

/* Links */
a {
    color: #22D3EE !important;
    text-decoration: none;
}

a:hover {
    color: #C084FC !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 7px;
}

::-webkit-scrollbar-track {
    background: #0F172A;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(#A855F7, #14B8A6);
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. LOAD DATA
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "space_missions_dashboard.csv"
)


@st.cache_data
def load_data(path):

    data = pd.read_csv(path)

    data["Date"] = pd.to_datetime(
        data["Date"],
        errors="coerce"
    )

    data["Price"] = pd.to_numeric(
        data["Price"],
        errors="coerce"
    )

    data = data.dropna(subset=["Date"]).copy()

    data["Year"] = data["Date"].dt.year.astype(int)
    data["Month"] = data["Date"].dt.month
    data["Decade"] = (data["Year"] // 10) * 10

    return data


if not DATA_PATH.exists():
    st.error(f"Dataset not found: {DATA_PATH}")
    st.stop()

df = load_data(str(DATA_PATH))

required_columns = [
    "Company", "Location", "Date", "Rocket",
    "Mission", "RocketStatus", "Price", "MissionStatus"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(f"Missing dataset columns: {missing_columns}")
    st.stop()


# =========================================================
# 4. COUNTRY CLASSIFICATION
# =========================================================

def identify_country(location):

    if pd.isna(location):
        return "Unknown"

    location = str(location).lower()

    country_keywords = {
        "United States": [
            "usa", "united states", "cape canaveral",
            "kennedy", "vandenberg", "wallops",
            "alaska", "kwajalein"
        ],
        "Kazakhstan": ["kazakhstan", "baikonur"],
        "Russia": ["russia", "plesetsk", "kapustin"],
        "China": ["china", "jiuquan", "xichang", "taiyuan"],
        "India": ["india", "sriharikota"],
        "Japan": ["japan", "tanegashima", "uchinoura"],
        "New Zealand": ["new zealand", "mahia"],
        "French Guiana": ["french guiana", "kourou"],
        "South Korea": ["south korea", "naro"],
        "Israel": ["israel", "palmachim"],
        "Australia": ["australia", "woomera"],
        "Brazil": ["brazil", "alcantara"],
        "Iran": ["iran", "semnan"],
        "North Korea": ["north korea", "sohae"]
    }

    for country, keywords in country_keywords.items():

        if any(keyword in location for keyword in keywords):
            return country

    return "Other / Unclassified"


df["Country"] = df["Location"].apply(identify_country)


# =========================================================
# 5. CHART DESIGN
# =========================================================

PURPLE = "#A855F7"
CYAN = "#14B8A6"
CORAL = "#F97316"
GREEN = "#10B981"
RED = "#F43F5E"
BLUE = "#38BDF8"


def style_chart(fig, height=190):

    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#E2E8F0",
            family="Arial",
            size=11
        ),
        margin=dict(
            l=25,
            r=20,
            t=42,
            b=25
        ),
        title_font=dict(
            size=15,
            color="#F8FAFC"
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=10)
        ),
        xaxis=dict(
            gridcolor="rgba(148,163,184,0.12)",
            zerolinecolor="rgba(148,163,184,0.15)"
        ),
        yaxis=dict(
            gridcolor="rgba(148,163,184,0.12)",
            zerolinecolor="rgba(148,163,184,0.15)"
        )
    )

    return fig


def show_chart(fig, height=190):

    fig = style_chart(fig, height)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )


def format_money(value):

    if pd.isna(value):
        return "N/A"

    return f"${value:,.2f}M"



# =========================================================
# 6. HEADER
# =========================================================

header_left, header_right = st.columns([5, 1])

with header_left:
    st.markdown(
        "<div style='color:#C084FC;font-size:11px;"
        "font-weight:700;letter-spacing:3px;'>"
        "GLOBAL SPACE DATA INTELLIGENCE</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<h1 style='font-size:32px;line-height:1.2;"
        "font-weight:850;color:#E9D5FF;margin:0;'>"
        "SPACE MISSION CONTROL</h1>",
        unsafe_allow_html=True
    )

    st.caption(
        "Explore global launches, mission outcomes, organizations and costs."
    )

with header_right:
    map_page = (
        Path(__file__).resolve().parent
        / "pages"
        / "2_Launch_Centre_Map.py"
    )

    if map_page.exists():
        st.page_link(
            "pages/2_Launch_Centre_Map.py",
            label="🌐 Global Map"
        )



# =========================================================
# 7. TOP FILTERS
# =========================================================

st.markdown("#### 🎛️ Mission Filters")

filter1, filter2, filter3, filter4 = st.columns([1.3, 1, 1, 1])

min_year = int(df["Year"].min())
max_year = int(df["Year"].max())

with filter1:

    year_range = st.slider(
        "Launch Year",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )


with filter2:

    companies = sorted(
        df["Company"].dropna().unique().tolist()
    )

    selected_companies = st.multiselect(
        "Companies",
        companies,
        default=[]
    )


with filter3:

    countries = sorted(
        df["Country"].dropna().unique().tolist()
    )

    selected_countries = st.multiselect(
        "Countries",
        countries,
        default=[]
    )


with filter4:

    outcomes = sorted(
        df["MissionStatus"].dropna().astype(str).unique().tolist()
    )

    selected_outcomes = st.multiselect(
        "Mission Outcomes",
        outcomes,
        default=[]
    )


# =========================================================
# 8. APPLY FILTERS
# =========================================================

filtered_df = df[
    (df["Year"] >= year_range[0]) &
    (df["Year"] <= year_range[1])
].copy()


if selected_companies:

    filtered_df = filtered_df[
        filtered_df["Company"].isin(selected_companies)
    ]


if selected_countries:

    filtered_df = filtered_df[
        filtered_df["Country"].isin(selected_countries)
    ]


if selected_outcomes:

    filtered_df = filtered_df[
        filtered_df["MissionStatus"].astype(str).isin(selected_outcomes)
    ]


if filtered_df.empty:

    st.warning("No missions match the selected filters.")
    st.stop()


# =========================================================
# 9. COMMON METRICS
# =========================================================

total_launches = len(filtered_df)

status_text = (
    filtered_df["MissionStatus"]
    .astype(str)
    .str.lower()
)

successful = status_text.str.contains(
    "success",
    na=False
).sum()

failed = status_text.str.contains(
    "failure",
    na=False
).sum()

partial = status_text.str.contains(
    "partial",
    na=False
).sum()

success_rate = (
    successful / total_launches * 100
    if total_launches else 0
)


# =========================================================
# 10. KPI CARDS
# =========================================================

st.markdown("#### 🚀 Mission Overview")

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        "Total Launches",
        f"{total_launches:,}"
    )

with k2:
    st.metric(
        "Successful Missions",
        f"{successful:,}"
    )

with k3:
    st.metric(
        "Failed Missions",
        f"{failed:,}"
    )

with k4:
    st.metric(
        "Success Rate",
        f"{success_rate:.1f}%"
    )


# =========================================================
# 11. DASHBOARD TABS
# =========================================================

tabs = st.tabs([
    "🌌 Overview",
    "📈 Performance",
    "🌍 Countries",
    "🏢 Companies",
    "🚀 Rockets",
    "💰 Costs",
    "📋 Records"
])


# =========================================================
# TAB 1: OVERVIEW
# Compact 2 x 2 layout
# =========================================================

with tabs[0]:

    left, right = st.columns(2)

    # Mission outcome chart
    with left:

        outcome_data = pd.DataFrame({
            "Outcome": [
                "Success",
                "Failure",
                "Partial Failure",
                "Other"
            ],
            "Count": [
                int(successful),
                int(failed),
                int(partial),
                max(
                    total_launches - successful - failed - partial,
                    0
                )
            ]
        })

        outcome_data = outcome_data[
            outcome_data["Count"] > 0
        ]

        fig = px.pie(
            outcome_data,
            names="Outcome",
            values="Count",
            hole=0.65,
            title="Mission Outcome Distribution",
            color="Outcome",
            color_discrete_map={
                "Success": GREEN,
                "Failure": RED,
                "Partial Failure": CORAL,
                "Other": PURPLE
            }
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent"
        )

        show_chart(fig, 190)


    # Yearly launch activity
    with right:

        yearly = (
            filtered_df.groupby("Year")
            .size()
            .reset_index(name="Launches")
        )

        fig = px.area(
            yearly,
            x="Year",
            y="Launches",
            title="Yearly Launch Activity",
            markers=True
        )

        fig.update_traces(
            line=dict(
                color=CYAN,
                width=3
            ),
            fillcolor="rgba(20,184,166,0.20)"
        )

        show_chart(fig, 190)


    left, right = st.columns(2)


    # Top companies
    with left:

        company_counts = (
            filtered_df["Company"]
            .value_counts()
            .head(8)
            .reset_index()
        )

        company_counts.columns = [
            "Company",
            "Launches"
        ]

        fig = px.bar(
            company_counts.sort_values("Launches"),
            x="Launches",
            y="Company",
            orientation="h",
            title="Leading Launch Companies",
            color="Launches",
            color_continuous_scale=[
                "#9333EA",
                "#14B8A6"
            ]
        )

        show_chart(fig, 190)


    # Top countries
    with right:

        country_counts = (
            filtered_df["Country"]
            .value_counts()
            .head(8)
            .reset_index()
        )

        country_counts.columns = [
            "Country",
            "Launches"
        ]

        fig = px.bar(
            country_counts.sort_values("Launches"),
            x="Launches",
            y="Country",
            orientation="h",
            title="Leading Launch Countries",
            color="Launches",
            color_continuous_scale=[
                "#A855F7",
                "#22D3EE"
            ]
        )

        show_chart(fig, 190)


# =========================================================
# TAB 2: PERFORMANCE
# =========================================================

with tabs[1]:

    st.markdown("### 📈 Mission Performance Analysis")

    left, right = st.columns(2)

    with left:

        yearly_outcomes = (
            filtered_df.groupby(
                ["Year", "MissionStatus"]
            )
            .size()
            .reset_index(name="Missions")
        )

        fig = px.line(
            yearly_outcomes,
            x="Year",
            y="Missions",
            color="MissionStatus",
            title="Mission Outcomes Over Time",
            markers=True,
            color_discrete_sequence=[
                GREEN,
                RED,
                CORAL,
                PURPLE,
                CYAN
            ]
        )

        show_chart(fig, 350)


    with right:

        yearly_success = filtered_df.copy()

        yearly_success["IsSuccessful"] = (
            yearly_success["MissionStatus"]
            .astype(str)
            .str.lower()
            .str.contains("success", na=False)
        )

        success_trend = (
            yearly_success.groupby("Year")
            .agg(
                Total=("Mission", "size"),
                Successful=("IsSuccessful", "sum")
            )
            .reset_index()
        )

        success_trend["Success Rate"] = (
            success_trend["Successful"]
            / success_trend["Total"] * 100
        )

        fig = px.line(
            success_trend,
            x="Year",
            y="Success Rate",
            title="Yearly Mission Success Rate",
            markers=True
        )

        fig.update_traces(
            line=dict(
                color=CYAN,
                width=3
            )
        )

        fig.update_yaxes(range=[0, 100])

        show_chart(fig, 350)


    st.markdown("#### Mission Status Summary")

    status_summary = (
        filtered_df["MissionStatus"]
        .value_counts()
        .reset_index()
    )

    status_summary.columns = [
        "Mission Status",
        "Number of Missions"
    ]

    st.dataframe(
        status_summary,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# TAB 3: COUNTRIES
# =========================================================

with tabs[2]:

    st.markdown("### 🌍 Global Launch Analysis")

    country_summary = (
        filtered_df.groupby("Country")
        .agg(
            Launches=("Company", "size"),
            Companies=("Company", "nunique"),
            Average_Cost=("Price", "mean")
        )
        .reset_index()
        .sort_values("Launches", ascending=False)
    )

    country_summary["Average Cost"] = (
        country_summary["Average_Cost"]
        .apply(format_money)
    )

    left, right = st.columns(2)

    with left:

        fig = px.bar(
            country_summary.head(15).sort_values("Launches"),
            x="Launches",
            y="Country",
            orientation="h",
            title="Countries With Most Launches",
            color="Launches",
            color_continuous_scale=[
                "#9333EA",
                "#14B8A6"
            ]
        )

        show_chart(fig, 400)


    with right:

        least_countries = (
            country_summary[
                country_summary["Country"] != "Other / Unclassified"
            ]
            .sort_values("Launches")
            .head(10)
        )

        fig = px.bar(
            least_countries.sort_values("Launches"),
            x="Launches",
            y="Country",
            orientation="h",
            title="Countries With Fewer Launches",
            color="Launches",
            color_continuous_scale=[
                "#F97316",
                "#A855F7"
            ]
        )

        show_chart(fig, 400)


    st.markdown("#### Country Statistics")

    st.dataframe(
        country_summary[
            [
                "Country",
                "Launches",
                "Companies",
                "Average Cost"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Country classification is inferred from launch-site names "
        "in the Location column. Unclassified locations are grouped separately."
    )


# =========================================================
# TAB 4: COMPANIES
# =========================================================

with tabs[3]:

    st.markdown("### 🏢 Space Organization Analysis")

    company_summary = (
        filtered_df.groupby("Company")
        .agg(
            Launches=("Mission", "size"),
            Rockets=("Rocket", "nunique")
        )
        .reset_index()
        .sort_values("Launches", ascending=False)
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

with tabs[4]:

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

with tabs[5]:

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

        with left:

            fig = px.histogram(
                cost_df,
                x="Price",
                nbins=30,
                title="Distribution of Mission Costs",
                color_discrete_sequence=[PURPLE]
            )

            show_chart(fig, 350)


        with right:

            company_cost = (
                cost_df.groupby("Company")["Price"]
                .mean()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )

            fig = px.bar(
                company_cost.sort_values("Price"),
                x="Price",
                y="Company",
                orientation="h",
                title="Average Cost by Company",
                color="Price",
                color_continuous_scale=[
                    "#14B8A6",
                    "#F97316"
                ]
            )

            show_chart(fig, 350)


        yearly_cost = (
            cost_df.groupby("Year")["Price"]
            .mean()
            .reset_index()
        )

        fig = px.line(
            yearly_cost,
            x="Year",
            y="Price",
            title="Average Mission Cost Over Time",
            markers=True
        )

        fig.update_traces(
            line=dict(
                color=CORAL,
                width=3
            )
        )

        show_chart(fig, 350)

        st.caption(
            "Costs are shown only for missions with recorded price values. "
            "The dataset contains missing cost entries."
        )


# =========================================================
# TAB 7: RECORDS
# =========================================================

with tabs[6]:

    st.markdown("### 📋 Mission Records Explorer")

    st.write(
        f"Showing **{len(filtered_df):,}** missions "
        "matching the selected filters."
    )

    search_text = st.text_input(
        "Search missions, companies, rockets or locations",
        placeholder="Type to search..."
    )

    records_df = filtered_df.copy()

    if search_text:

        search_mask = (
            records_df.astype(str)
            .apply(
                lambda column: column.str.contains(
                    search_text,
                    case=False,
                    na=False
                )
            )
            .any(axis=1)
        )

        records_df = records_df[search_mask]


    display_columns = [
        "Company",
        "Location",
        "Date",
        "Rocket",
        "Mission",
        "RocketStatus",
        "Price",
        "MissionStatus",
        "Country"
    ]

    display_columns = [
        col for col in display_columns
        if col in records_df.columns
    ]

    st.dataframe(
        records_df[display_columns],
        use_container_width=True,
        hide_index=True,
        height=480
    )

    csv_data = records_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download Filtered Mission Data",
        data=csv_data,
        file_name="space_mission_records.csv",
        mime="text/csv"
    )
