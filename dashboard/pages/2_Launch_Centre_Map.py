
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Launch Centre Map",
    page_icon="🌍",
    layout="wide"
)

# ---------------- DATA LOADING ----------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "space_missions_dashboard.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load dataset: {e}")
    st.stop()

# ---------------- LAUNCH CENTRE COORDINATES ----------------
# Coordinates are approximate launch-site locations.
# Unmatched locations will be excluded from the map.

LOCATION_COORDINATES = {
    "Kennedy Space Center": (28.5729, -80.6490),
    "Cape Canaveral": (28.3922, -80.6077),
    "Vandenberg": (34.7420, -120.5724),
    "Baikonur": (45.9646, 63.3052),
    "Plesetsk": (62.9271, 40.5777),
    "Kourou": (5.2360, -52.7680),
    "Jiuquan": (40.9606, 100.2983),
    "Xichang": (28.2460, 102.0260),
    "Taiyuan": (38.8490, 111.6080),
    "Wenchang": (19.6145, 110.9510),
    "Satish Dhawan Space Centre": (13.7199, 80.2304),
    "Sriharikota": (13.7199, 80.2304),
    "Tanegashima": (30.3750, 130.9570),
    "Uchinoura": (31.2510, 131.0820),
    "Mahia": (-39.2610, 177.8640),
    "Rocket Lab": (-39.2610, 177.8640),
    "Wallops": (37.9402, -75.4664),
    "Kodiak": (57.4353, -152.3378),
    "Palmachim": (31.8928, 34.6907),
    "Naro": (34.4310, 127.5350),
}

def get_coordinates(location):
    if pd.isna(location):
        return None

    location = str(location).strip().lower()

    for site, coordinates in LOCATION_COORDINATES.items():
        if site.lower() in location:
            return coordinates

    # Do not guess coordinates for unknown locations.
    return None

# ---------------- PAGE HEADER ----------------

st.title("🌍 Global Space Launch Centres")
st.caption(
    "Explore worldwide launch activity, mission performance "
    "and geographical distribution."
)

# ---------------- FILTERS ----------------

col1, col2 = st.columns(2)

with col1:
    companies = ["All"] + sorted(df["Company"].dropna().unique().tolist())
    selected_company = st.selectbox("Company", companies)

with col2:
    years = df["Date"].dropna().dt.year
    if not years.empty:
        min_year = int(years.min())
        max_year = int(years.max())
        selected_years = st.slider(
            "Launch year range",
            min_year,
            max_year,
            (min_year, max_year)
        )
    else:
        selected_years = None

filtered = df.copy()

if selected_company != "All":
    filtered = filtered[filtered["Company"] == selected_company]

if selected_years:
    filtered = filtered[
        filtered["Date"].dt.year.between(
            selected_years[0], selected_years[1]
        )
    ]

# ---------------- MAP DATA ----------------

filtered["Coordinates"] = filtered["Location"].apply(get_coordinates)

map_df = filtered[filtered["Coordinates"].notna()].copy()

if not map_df.empty:
    map_df["Latitude"] = map_df["Coordinates"].apply(lambda x: x[0])
    map_df["Longitude"] = map_df["Coordinates"].apply(lambda x: x[1])

    site_summary = (
        map_df.groupby(
            ["Location", "Latitude", "Longitude"],
            as_index=False
        )
        .agg(
            Missions=("Mission", "count"),
            Companies=("Company", "nunique")
        )
    )

    # ---------------- METRICS ----------------

    m1, m2, m3 = st.columns(3)

    m1.metric("Filtered Missions", f"{len(filtered):,}")
    m2.metric("Mapped Missions", f"{len(map_df):,}")
    m3.metric("Mapped Launch Sites", f"{len(site_summary):,}")

    # ---------------- WORLD MAP ----------------

    st.subheader("Launch Centre Locations")

    fig = px.scatter_geo(
        site_summary,
        lat="Latitude",
        lon="Longitude",
        size="Missions",
        color="Missions",
        hover_name="Location",
        hover_data={
            "Latitude": False,
            "Longitude": False,
            "Missions": True,
            "Companies": True
        },
        projection="natural earth",
        color_continuous_scale="Teal",
        title="Global Distribution of Space Launch Activity"
    )

    fig.update_layout(
        height=600,
        paper_bgcolor="#0B0F14",
        plot_bgcolor="#0B0F14",
        font_color="#F3F4F6",
        geo=dict(
            bgcolor="#0B0F14",
            showland=True,
            landcolor="#222B35",
            showocean=True,
            oceancolor="#101923",
            showcountries=True,
            countrycolor="#536170",
            showcoastlines=True,
            coastlinecolor="#536170"
        ),
        margin=dict(l=10, r=10, t=60, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------------- SITE SUMMARY ----------------

    st.subheader("Launch Site Summary")

    st.dataframe(
        site_summary.sort_values(
            "Missions", ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning(
        "No launch locations matched the currently supported coordinates."
    )

# ---------------- UNMAPPED LOCATIONS ----------------

unmapped = filtered[filtered["Coordinates"].isna()]

with st.expander("View locations not yet mapped"):
    if not unmapped.empty:
        st.write(
            "These locations need coordinate verification before being added:"
        )
        st.dataframe(
            unmapped["Location"].value_counts().reset_index(),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("All filtered locations were mapped.")
