import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from math import radians, sin, cos, sqrt, atan2

# ============================================================
# HYDROSCOPE
# ============================================================

st.set_page_config(
    page_title="HYDROSCOPE",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# GLOBAL STYLE
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 15% 10%, rgba(0,160,220,0.08), transparent 30%),
        radial-gradient(circle at 85% 80%, rgba(0,90,180,0.07), transparent 30%),
        #080c13 !important;
    color: #eaf7ff !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stToolbar"] {
    visibility: hidden;
}

section[data-testid="stSidebar"] {
    display: none;
}

.block-container {
    max-width: 1450px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
}

/* HEADER */

.hydro-header {
    text-align: center;
    padding: 12px 0 20px 0;
}

.hydro-title {
    font-size: 43px;
    font-weight: 800;
    letter-spacing: 7px;
    color: #effbff;
}

.hydro-subtitle {
    margin-top: 5px;
    font-size: 12px;
    letter-spacing: 4px;
    color: #68dcff;
}

/* GLASS */

.glass-card {
    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,0.065),
            rgba(255,255,255,0.025)
        );
    border: 1px solid rgba(150,220,255,0.10);
    border-radius: 22px;
    padding: 24px;
    margin-bottom: 18px;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    box-shadow:
        0 15px 40px rgba(0,0,0,0.22),
        inset 0 1px 0 rgba(255,255,255,0.03);
    transition: 0.25s ease;
}

.glass-card:hover {
    border-color: rgba(70,210,255,0.22);
    box-shadow:
        0 18px 45px rgba(0,0,0,0.25),
        0 0 30px rgba(40,180,240,0.05);
}

/* TITLES */

.section-title {
    font-size: 21px;
    font-weight: 700;
    color: #effaff;
}

.section-description {
    font-size: 13px;
    color: #8196a6;
    margin-top: 5px;
    margin-bottom: 18px;
}

/* NAVIGATION */

.nav-label {
    text-align: center;
    color: #6f8999;
    font-size: 11px;
    margin-top: 5px;
}

/* METRICS */

.metric-card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 19px;
    min-height: 125px;
    transition: 0.25s ease;
}

.metric-card:hover {
    transform: translateY(-3px);
    border-color: rgba(80,210,255,0.25);
}

.metric-label {
    color: #8296a5;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

.metric-value {
    color: #effaff;
    font-size: 30px;
    font-weight: 700;
    margin-top: 8px;
}

.metric-unit {
    color: #708696;
    font-size: 12px;
}

.metric-status {
    font-size: 11px;
    margin-top: 7px;
}

.status-normal {
    color: #55dfa4;
}

.status-warning {
    color: #ffc857;
}

.status-danger {
    color: #ff7171;
}

.status-critical {
    color: #ff405d;
}

/* BUTTONS */

.stButton > button {
    width: 100%;
    min-height: 43px;
    border-radius: 13px !important;
    border: 1px solid rgba(100,220,255,0.16) !important;
    background: rgba(255,255,255,0.045) !important;
    color: #eafaff !important;
    font-weight: 600 !important;
    transition: 0.2s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px);
    border-color: rgba(80,215,255,0.55) !important;
    background: rgba(50,190,240,0.10) !important;
    box-shadow: 0 8px 25px rgba(30,180,240,0.12);
}

.stButton > button:active {
    transform: scale(0.97);
}

/* INPUT */

.stSelectbox > div > div {
    background: rgba(255,255,255,0.035) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 12px !important;
}

/* LOCATION */

.location-card {
    background:
        radial-gradient(
            circle at 80% 20%,
            rgba(45,200,255,0.10),
            transparent 40%
        ),
        rgba(255,255,255,0.035);
    border: 1px solid rgba(90,210,255,0.14);
    border-radius: 22px;
    padding: 24px;
    margin-bottom: 20px;
}

.location-title {
    font-size: 20px;
    font-weight: 700;
}

.location-subtitle {
    color: #8297a7;
    font-size: 13px;
    margin-top: 5px;
}

/* DAM CARD */

.dam-card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 12px;
    transition: 0.25s ease;
}

.dam-card:hover {
    border-color: rgba(70,210,255,0.25);
    transform: translateY(-2px);
}

.dam-name {
    font-size: 17px;
    font-weight: 700;
    color: #edfaff;
}

.dam-location {
    color: #718899;
    font-size: 12px;
    margin-top: 3px;
}

.dam-distance {
    color: #67dcff;
    font-size: 12px;
    margin-top: 10px;
}

.dam-level {
    font-size: 25px;
    font-weight: 700;
    margin-top: 12px;
}

.dam-small {
    color: #7f94a4;
    font-size: 11px;
}

/* ALERTS */

.alert-card {
    border-radius: 17px;
    padding: 17px;
    margin-bottom: 12px;
}

.alert-normal {
    background: rgba(50,210,150,0.06);
    border: 1px solid rgba(50,210,150,0.18);
}

.alert-warning {
    background: rgba(255,190,60,0.06);
    border: 1px solid rgba(255,190,60,0.18);
}

.alert-danger {
    background: rgba(255,70,70,0.06);
    border: 1px solid rgba(255,70,70,0.20);
}

/* SHUTTERS */

.shutter {
    display: inline-block;
    width: 32px;
    height: 95px;
    margin: 4px;
    border-radius: 7px;
    background: linear-gradient(
        90deg,
        #17232d,
        #435766,
        #17232d
    );
    border: 1px solid rgba(200,230,240,0.15);
}

.shutter.open {
    background: linear-gradient(
        180deg,
        #5be4ff,
        #176d9c
    );
    box-shadow: 0 0 15px rgba(50,210,255,0.22);
}

/* FOOTER */

.hydro-footer {
    text-align: center;
    padding: 35px 0 10px 0;
    color: #526675;
    font-size: 11px;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# RIPPLE EFFECT
# ============================================================

st.markdown("""
<style>
.hydro-ripple {
    position: fixed;
    width: 10px;
    height: 10px;
    border: 2px solid rgba(80,220,255,0.65);
    border-radius: 50%;
    pointer-events: none;
    transform: translate(-50%, -50%);
    animation: hydroRipple 0.9s ease-out forwards;
    z-index: 999999;
}

@keyframes hydroRipple {
    0% {
        width: 10px;
        height: 10px;
        opacity: 0.9;
    }

    100% {
        width: 180px;
        height: 180px;
        opacity: 0;
    }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="hydro-header">'
    '<div class="hydro-title">💧 HYDROSCOPE</div>'
    '<div class="hydro-subtitle">DAM INTELLIGENCE • FLOOD PREDICTION • SAFETY</div>'
    '</div>',
    unsafe_allow_html=True
)

# ============================================================
# DAM DATABASE
# ============================================================

dams = pd.DataFrame([
    {
        "name": "Idukki Dam",
        "district": "Idukki",
        "lat": 9.8494,
        "lon": 76.9726,
        "level": 88,
        "inflow": 1800,
        "outflow": 600,
        "rainfall": 72,
        "shutters": 8,
        "open_shutters": 2,
        "opening": 20,
        "risk": "Moderate"
    },
    {
        "name": "Idamalayar Dam",
        "district": "Ernakulam",
        "lat": 10.2068,
        "lon": 76.7032,
        "level": 72,
        "inflow": 920,
        "outflow": 310,
        "rainfall": 48,
        "shutters": 4,
        "open_shutters": 1,
        "opening": 15,
        "risk": "Normal"
    },
    {
        "name": "Malankara Dam",
        "district": "Idukki",
        "lat": 9.7804,
        "lon": 76.8787,
        "level": 67,
        "inflow": 210,
        "outflow": 95,
        "rainfall": 41,
        "shutters": 6,
        "open_shutters": 1,
        "opening": 10,
        "risk": "Normal"
    },
    {
        "name": "Bhoothathankettu",
        "district": "Ernakulam",
        "lat": 10.1457,
        "lon": 76.6788,
        "level": 61,
        "inflow": 160,
        "outflow": 80,
        "rainfall": 36,
        "shutters": 5,
        "open_shutters": 1,
        "opening": 10,
        "risk": "Normal"
    },
    {
        "name": "Pamba Dam",
        "district": "Pathanamthitta",
        "lat": 9.3805,
        "lon": 76.9275,
        "level": 64,
        "inflow": 450,
        "outflow": 170,
        "rainfall": 39,
        "shutters": 6,
        "open_shutters": 1,
        "opening": 12,
        "risk": "Normal"
    },
    {
        "name": "Kakki Dam",
        "district": "Pathanamthitta",
        "lat": 9.3500,
        "lon": 77.0000,
        "level": 70,
        "inflow": 520,
        "outflow": 190,
        "rainfall": 44,
        "shutters": 4,
        "open_shutters": 1,
        "opening": 15,
        "risk": "Normal"
    },
    {
        "name": "Neyyar Dam",
        "district": "Thiruvananthapuram",
        "lat": 8.5350,
        "lon": 77.1450,
        "level": 58,
        "inflow": 190,
        "outflow": 75,
        "rainfall": 31,
        "shutters": 4,
        "open_shutters": 0,
        "opening": 0,
        "risk": "Normal"
    },
    {
        "name": "Banasura Sagar Dam",
        "district": "Wayanad",
        "lat": 11.7000,
        "lon": 75.9500,
        "level": 63,
        "inflow": 330,
        "outflow": 120,
        "rainfall": 52,
        "shutters": 4,
        "open_shutters": 1,
        "opening": 10,
        "risk": "Normal"
    }
])

# ============================================================
# LOCATION DATABASE
# ============================================================

locations = {
    "Kochi": {
        "lat": 9.9312,
        "lon": 76.2673
    },
    "Idukki": {
        "lat": 9.8500,
        "lon": 76.9700
    },
    "Munnar": {
        "lat": 10.0889,
        "lon": 77.0595
    },
    "Kothamangalam": {
        "lat": 10.0580,
        "lon": 76.6290
    },
    "Thodupuzha": {
        "lat": 9.8950,
        "lon": 76.7180
    },
    "Kottayam": {
        "lat": 9.5916,
        "lon": 76.5222
    },
    "Pathanamthitta": {
        "lat": 9.2648,
        "lon": 76.7870
    },
    "Alappuzha": {
        "lat": 9.4981,
        "lon": 76.3388
    },
    "Thiruvananthapuram": {
        "lat": 8.5241,
        "lon": 76.9366
    },
    "Wayanad": {
        "lat": 11.6854,
        "lon": 76.1320
    }
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def distance_km(lat1, lon1, lat2, lon2):
    earth_radius = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius * c


def get_nearby_dams(location_name, radius=120):

    location = locations[location_name]

    result = dams.copy()

    result["distance"] = result.apply(
        lambda row: distance_km(
            location["lat"],
            location["lon"],
            row["lat"],
            row["lon"]
        ),
        axis=1
    )

    result = result[
        result["distance"] <= radius
    ].sort_values("distance")

    return result


def metric_card(label, value, unit="", status="", status_class="status-normal"):

    return (
        '<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value} '
        f'<span class="metric-unit">{unit}</span></div>'
        f'<div class="metric-status {status_class}">{status}</div>'
        '</div>'
    )


def water_chart():

    levels = [
        81.2,
        81.5,
        82.0,
        82.4,
        83.0,
        83.8,
        84.5,
        85.4,
        86.1,
        86.7,
        87.3,
        87.7,
        88.0
    ]

    hours = list(range(13))

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=hours,
            y=levels,
            mode="lines+markers",
            line=dict(width=3),
            fill="tozeroy",
            fillcolor="rgba(50,190,240,0.08)",
            name="Water Level"
        )
    )

    fig.add_hline(
        y=90,
        line_dash="dash",
        annotation_text="Alert"
    )

    fig.add_hline(
        y=95,
        line_dash="dash",
        annotation_text="Critical"
    )

    fig.update_layout(
        height=330,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#b8cad5"),
        xaxis=dict(
            title="Hours",
            showgrid=False
        ),
        yaxis=dict(
            title="Storage Level (%)",
            gridcolor="rgba(255,255,255,0.06)"
        )
    )

    return fig

# ============================================================
# NAVIGATION
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

nav_cols = st.columns(5)

nav_items = [
    ("🏠", "Dashboard"),
    ("💧", "Dam Monitoring"),
    ("📈", "Prediction"),
    ("🌊", "Flood Simulation"),
    ("🚨", "Emergency Center")
]

for col, item in zip(nav_cols, nav_items):

    icon, name = item

    with col:

        if st.button(
            f"{icon}  {name}",
            key=f"nav_{name}"
        ):
            st.session_state.page = name
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# DASHBOARD
# ============================================================

def dashboard():

    # --------------------------------------------------------
    # LOCATION SELECTOR
    # --------------------------------------------------------

    st.markdown(
        '<div class="location-card">'
        '<div class="location-title">📍 Find Dams Near You</div>'
        '<div class="location-subtitle">'
        'Select your location and HYDROSCOPE will identify nearby '
        'monitored dams and display their current status.'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    location_names = list(locations.keys())

    selected_location = st.selectbox(
        "Select your location",
        location_names,
        index=0,
        key="location_selector"
    )

    nearby = get_nearby_dams(
        selected_location,
        radius=120
    )

    # --------------------------------------------------------
    # LOCATION RESULT
    # --------------------------------------------------------

    loc = locations[selected_location]

    st.markdown(
        '<div class="glass-card">'
        f'<div class="section-title">📍 {selected_location}</div>'
        '<div class="section-description">'
        f'Latitude: {loc["lat"]:.4f} &nbsp;&nbsp; '
        f'Longitude: {loc["lon"]:.4f}'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # MAP + NEARBY DAMS
    # --------------------------------------------------------

    map_col, dams_col = st.columns([1.45, 1])

    with map_col:

        st.markdown(
            '<div class="glass-card">'
            '<div class="section-title">🗺️ Nearby Dam Network</div>'
            '<div class="section-description">'
            'Dams within 120 km of the selected location.'
            '</div>',
            unsafe_allow_html=True
        )

        m = folium.Map(
            location=[
                loc["lat"],
                loc["lon"]
            ],
            zoom_start=9,
            tiles="CartoDB dark_matter"
        )

        # USER LOCATION

        folium.Marker(
            location=[
                loc["lat"],
                loc["lon"]
            ],
            tooltip=f"📍 {selected_location}",
            popup=f"Selected location: {selected_location}",
            icon=folium.Icon(
                color="blue",
                icon="user",
                prefix="fa"
            )
        ).add_to(m)

        # RADIUS

        folium.Circle(
            location=[
                loc["lat"],
                loc["lon"]
            ],
            radius=120000,
            color="#4bdcff",
            fill=True,
            fill_opacity=0.025,
            weight=1
        ).add_to(m)

        # DAMS

        for _, dam in nearby.iterrows():

            if dam["risk"] == "Critical":
                marker_color = "red"

            elif dam["risk"] == "Moderate":
                marker_color = "orange"

            else:
                marker_color = "green"

            popup = (
                f"<b>{dam['name']}</b><br>"
                f"District: {dam['district']}<br>"
                f"Distance: {dam['distance']:.1f} km<br>"
                f"Water Level: {dam['level']}%<br>"
                f"Risk: {dam['risk']}"
            )

            folium.Marker(
                location=[
                    dam["lat"],
                    dam["lon"]
                ],
                tooltip=dam["name"],
                popup=popup,
                icon=folium.Icon(
                    color=marker_color,
                    icon="tint",
                    prefix="fa"
                )
            ).add_to(m)

        st_folium(
            m,
            width=None,
            height=500
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # NEARBY DAM LIST
    # --------------------------------------------------------

    with dams_col:

        st.markdown(
            '<div class="glass-card">'
            '<div class="section-title">'
            f'💧 Dams Near {selected_location}'
            '</div>'
            '<div class="section-description">'
            f'{len(nearby)} monitored dam(s) found nearby.'
            '</div>',
            unsafe_allow_html=True
        )

        if len(nearby) == 0:

            st.info(
                "No monitored dams found within 120 km."
            )

        else:

            for _, dam in nearby.iterrows():

                risk_class_name = (
                    "status-warning"
                    if dam["risk"] == "Moderate"
                    else
                    "status-danger"
                    if dam["risk"] == "High"
                    else
                    "status-normal"
                )

                st.markdown(
                    '<div class="dam-card">'
                    f'<div class="dam-name">💧 {dam["name"]}</div>'
                    f'<div class="dam-location">'
                    f'{dam["district"]}, Kerala'
                    '</div>'
                    f'<div class="dam-distance">'
                    f'📍 {dam["distance"]:.1f} km away'
                    '</div>'
                    f'<div class="dam-level">'
                    f'{dam["level"]}%'
                    '</div>'
                    '<div class="dam-small">Current water level</div>'
                    f'<div class="{risk_class_name}" '
                    'style="margin-top:8px;">'
                    f'● {dam["risk"]} Risk'
                    '</div>'
                    '</div>',
                    unsafe_allow_html=True
                )

                if st.button(
                    f"View {dam['name']}",
                    key=f"view_{dam['name']}"
                ):

                    st.session_state.selected_dam = dam["name"]
                    st.session_state.page = "Dam Monitoring"
                    st.rerun()

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # SYSTEM OVERVIEW
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">System Overview</div>'
        '<div class="section-description">'
        'Current network-level monitoring status.'
        '</div>',
        unsafe_allow_html=True
    )

    total_dams = len(dams)

    avg_level = dams["level"].mean()

    total_inflow = dams["inflow"].sum()

    attention = len(
        dams[
            dams["risk"].isin(
                ["Moderate", "High", "Critical"]
            )
        ]
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            metric_card(
                "Dams Monitored",
                total_dams,
                "",
                "● System online",
                "status-normal"
            ),
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            metric_card(
                "Average Storage",
                f"{avg_level:.1f}",
                "%",
                "● Network average",
                "status-normal"
            ),
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            metric_card(
                "Total Inflow",
                f"{total_inflow:,}",
                "m³/s",
                "● Monitoring active",
                "status-normal"
            ),
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            metric_card(
                "Attention Required",
                attention,
                "",
                "● Requires monitoring",
                "status-warning"
            ),
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([1.5, 1])

    with left:

        st.markdown(
            '<div class="glass-card">'
            '<div class="section-title">'
            '📈 Network Water-Level Trend'
            '</div>'
            '<div class="section-description">'
            'Demonstration monitoring data.'
            '</div>',
            unsafe_allow_html=True
        )

        st.plotly_chart(
            water_chart(),
            use_container_width=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    with right:

        st.markdown(
            '<div class="glass-card">'
            '<div class="section-title">'
            '⚠️ Monitoring Status'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="alert-card alert-normal">'
            '<b>🟢 Monitoring Network</b><br>'
            '<span style="color:#849aaa;">'
            'All prototype monitoring modules are operational.'
            '</span>'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="alert-card alert-warning">'
            '<b>🟡 Idukki Dam</b><br>'
            '<span style="color:#849aaa;">'
            'Storage requires continued monitoring.'
            '</span>'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="alert-card alert-normal">'
            '<b>🟢 Rainfall Network</b><br>'
            '<span style="color:#849aaa;">'
            'Monitoring data available.'
            '</span>'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


# ============================================================
# DAM MONITORING
# ============================================================

def dam_monitoring():

    st.markdown(
        '<div class="section-title">💧 Dam Monitoring</div>'
        '<div class="section-description">'
        'Detailed monitoring of water level, rainfall, inflow, '
        'outflow and shutter configuration.'
        '</div>',
        unsafe_allow_html=True
    )

    if "selected_dam" in st.session_state:
        default_dam = st.session_state.selected_dam
    else:
        default_dam = dams.iloc[0]["name"]

    dam_names = dams["name"].tolist()

    selected_index = (
        dam_names.index(default_dam)
        if default_dam in dam_names
        else 0
    )

    selected = st.selectbox(
        "Select Dam",
        dam_names,
        index=selected_index
    )

    dam = dams[dams["name"] == selected].iloc[0]

    left, right = st.columns([1.2, 1])

    with left:

        st.markdown(
            '<div class="glass-card">'
            '<div class="section-title">📍 Dam Location</div>',
            unsafe_allow_html=True
        )

        m = folium.Map(
            location=[
                dam["lat"],
                dam["lon"]
            ],
            zoom_start=11,
            tiles="CartoDB dark_matter"
        )

        folium.Marker(
            location=[
                dam["lat"],
                dam["lon"]
            ],
            tooltip=dam["name"],
            popup=dam["name"],
            icon=folium.Icon(
                color="blue",
                icon="tint",
                prefix="fa"
            )
        ).add_to(m)

        st_folium(
            m,
            width=None,
            height=430
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    with right:

        st.markdown(
            '<div class="glass-card">'
            '<div class="section-title">'
            '📊 Current Condition'
            '</div>',
            unsafe_allow_html=True
        )

        a, b = st.columns(2)

        with a:

            st.markdown(
                metric_card(
                    "Water Level",
                    dam["level"],
                    "%",
                    "Current storage",
                    "status-warning"
                    if dam["level"] >= 85
                    else "status-normal"
                ),
                unsafe_allow_html=True
            )

        with b:

            st.markdown(
                metric_card(
                    "Rainfall",
                    dam["rainfall"],
                    "mm/hr",
                    "Current intensity",
                    "status-warning"
                    if dam["rainfall"] >= 60
                    else "status-normal"
                ),
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        a, b = st.columns(2)

        with a:

            st.markdown(
                metric_card(
                    "Inflow",
                    f"{dam['inflow']:,}",
                    "m³/s",
                    "Incoming flow",
                    "status-normal"
                ),
                unsafe_allow_html=True
            )

        with b:

            st.markdown(
                metric_card(
                    "Outflow",
                    f"{dam['outflow']:,}",
                    "m³/s",
                    "Released flow",
                    "status-normal"
                ),
                unsafe_allow_html=True
            )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="glass-card">'
            '<div class="section-title">'
            '🚪 Shutter Configuration'
            '</div>'
            '<div class="section-description">'
            'Current prototype gate configuration.'
            '</div>',
            unsafe_allow_html=True
        )

        shutters_html = ""

        for i in range(int(dam["shutters"])):

            if i < int(dam["open_shutters"]):
                shutters_html += '<div class="shutter open"></div>'
            else:
                shutters_html += '<div class="shutter"></div>'

        st.markdown(
            '<div style="text-align:center;">'
            + shutters_html
            + '</div>'
            + '<div style="text-align:center;'
            'margin-top:12px;color:#849aaa;font-size:13px;">'
            f'{int(dam["open_shutters"])} of '
            f'{int(dam["shutters"])} shutters open • '
            f'{dam["opening"]}% opening'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="glass-card">'
        '<div class="section-title">'
        '📈 Water-Level History'
        '</div>',
        unsafe_allow_html=True
    )

    st.plotly_chart(
        water_chart(),
        use_container_width=True
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# PREDICTION
# ============================================================

def prediction():

    st.markdown(
        '<div class="section-title">📈 Prediction Center</div>'
        '<div class="section-description">'
        'Estimate future water levels and controlled-release probability.'
        '</div>',
        unsafe_allow_html=True
    )

    selected = st.selectbox(
        "Prediction Dam",
        dams["name"].tolist()
    )

    dam = dams[dams["name"] == selected].iloc[0]

    probability = min(
        95,
        max(
            10,
            int(
                dam["level"] * 0.65
                + dam["rainfall"] * 0.25
            )
        )
    )

    predicted = min(
        99,
        dam["level"] + int(dam["rainfall"] / 20)
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            metric_card(
                "Current Level",
                dam["level"],
                "%",
                "Baseline",
                "status-normal"
            ),
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            metric_card(
                "Release Probability",
                probability,
                "%",
                "Decision-support estimate",
                "status-warning"
            ),
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            metric_card(
                "Predicted Level",
                predicted,
                "%",
                "Next prediction window",
                "status-warning"
            ),
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([1.5, 1])

    with left:

        st.markdown(
            '<div class="glass-card">'
            '<div class="section-title">'
            '🔮 Water-Level Forecast'
            '</div>',
            unsafe_allow_html=True
        )

        future = list(range(13))

        values = []

        for hour in future:

            value = (
                dam["level"]
                + hour * 0.35
                + np.sin(hour / 2) * 0.35
            )

            values.append(
                min(100, value)
            )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=future,
                y=values,
                mode="lines+markers",
                line=dict(width=3),
                name="Predicted Level"
            )
        )

        fig.add_hline(
            y=90,
            line_dash="dash",
            annotation_text="Alert"
        )

        fig.add_hline(
            y=95,
            line_dash="dash",
            annotation_text="Critical"
        )

        fig.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#b8cad5"),
            xaxis=dict(
                title="Forecast Hours",
                showgrid=False
            ),
            yaxis=dict(
                title="Water Level (%)",
                gridcolor="rgba(255,255,255,0.06)"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    with right:

        st.markdown(
            '<div class="glass-card">'
            '<div class="section-title">'
            '🧠 Decision Support'
            '</div>',
            unsafe_allow_html=True
        )

        if probability >= 75:

            st.markdown(
                '<div class="alert-card alert-warning">'
                '<b>🟡 Elevated Release Probability</b><br><br>'
                '<span style="color:#849aaa;">'
                'Current prototype conditions indicate increased '
                'probability of controlled release.'
                '</span>'
                '</div>',
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                '<div class="alert-card alert-normal">'
                '<b>🟢 Normal Release Probability</b><br><br>'
                '<span style="color:#849aaa;">'
                'Current prototype conditions do not indicate '
                'high release probability.'
                '</span>'
                '</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            '<div style="margin-top:15px;padding:15px;'
            'border-radius:14px;background:rgba(255,255,255,0.025);'
            'color:#7f94a3;font-size:12px;">'
            '⚠️ Prototype decision-support output. '
            'This is not an autonomous dam-operation command.'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


# ============================================================
# FLOOD SIMULATION
# ============================================================

def flood_simulation():

    st.markdown(
        '<div class="section-title">🌊 Flood Simulation</div>'
        '<div class="section-description">'
        'Simulate downstream flood propagation and potential impact.'
        '</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns([1, 1.5])

    with left:

        st.markdown(
            '<div class="glass-card">'
            '<div class="section-title">'
            '⚙️ Simulation Parameters'
            '</div>',
            unsafe_allow_html=True
        )

        selected = st.selectbox(
            "Source Dam",
            dams["name"].tolist()
        )

        dam = dams[dams["name"] == selected].iloc[0]

        breach = st.slider(
            "Breach Severity",
            10,
            100,
            40
        )

        rainfall_factor = st.slider(
            "Rainfall Factor",
            0.5,
            2.0,
            1.0,
            0.1
        )

        duration = st.slider(
            "Simulation Duration",
            1,
            24,
            12
        )

        simulate = st.button(
            "🌊 RUN FLOOD SIMULATION"
        )

        st.markdown(
            '<div style="margin-top:15px;color:#627584;'
            'font-size:11px;">'
            'Simplified prototype flood model for demonstration.'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    with right:

        st.markdown(
            '<div class="glass-card">'
            '<div class="section-title">'
            '📊 Simulated Impact'
            '</div>',
            unsafe_allow_html=True
        )

        if simulate:

            peak_flow = (
                dam["outflow"]
                * (1 + breach / 100)
                * rainfall_factor
            )

            arrival = max(
                0.5,
                6 - breach / 20
            )

            affected = int(
                15000
                * (breach / 100)
                * rainfall_factor
            )

            st.markdown(
                metric_card(
                    "Peak Simulated Flow",
                    f"{peak_flow:,.0f}",
                    "m³/s",
                    "Model output",
                    "status-danger"
                ),
                unsafe_allow_html=True
            )

            st.markdown("<br>", unsafe_allow_html=True)

            a, b = st.columns(2)

            with a:

                st.markdown(
                    metric_card(
                        "Estimated Arrival",
                        f"{arrival:.1f}",
                        "hours",
                        "Downstream estimate",
                        "status-warning"
                    ),
                    unsafe_allow_html=True
                )

            with b:

                st.markdown(
                    metric_card(
                        "Potentially Affected",
                        f"{affected:,}",
                        "people",
                        "Prototype estimate",
                        "status-danger"
                    ),
                    unsafe_allow_html=True
                )

        else:

            st.markdown(
                '<div style="padding:70px 20px;text-align:center;'
                'color:#657b8b;">'
                '🌊<br><br>'
                'Configure the scenario and run the simulation.'
                '</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


# ============================================================
# EMERGENCY CENTER
# ============================================================

def emergency_center():

    st.markdown(
        '<div class="section-title">🚨 Emergency Center</div>'
        '<div class="section-description">'
        'Emergency intelligence, alerts and evacuation-support information.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="alert-card alert-warning">'
        '<b>🟡 DEMONSTRATION ALERT</b><br><br>'
        'Idukki demonstration scenario is being monitored '
        'due to elevated water-level conditions.'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            metric_card(
                "Active Alerts",
                1,
                "",
                "Monitoring alert",
                "status-warning"
            ),
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            metric_card(
                "Impact Zones",
                3,
                "",
                "Prototype zones",
                "status-warning"
            ),
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            metric_card(
                "Critical Assets",
                7,
                "",
                "Prototype assets",
                "status-warning"
            ),
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div class="glass-card">'
        '<div class="section-title">'
        '🆘 Emergency Response'
        '</div>'
        '<div class="section-description">'
        'Prototype emergency-response controls.'
        '</div>',
        unsafe_allow_html=True
    )

    a, b = st.columns(2)

    with a:

        if st.button("📢 Issue Warning Alert"):

            st.warning(
                "Prototype warning alert generated."
            )

        if st.button("📍 View Evacuation Zones"):

            st.info(
                "Evacuation-zone visualization will be connected "
                "to the GIS flood model."
            )

    with b:

        if st.button("🏘️ View Affected Settlements"):

            st.info(
                "Settlement-impact analysis will be connected "
                "to downstream GIS data."
            )

        if st.button("🚑 Emergency Response Mode"):

            st.error(
                "Emergency response mode activated — prototype."
            )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="glass-card">'
        '<div class="section-title">'
        '📋 Emergency Checklist'
        '</div><br>'
        '<div style="line-height:2;color:#a9bbc7;">'
        '✓ Verify dam water level<br>'
        '✓ Verify rainfall intensity<br>'
        '✓ Verify inflow and outflow<br>'
        '✓ Verify shutter configuration<br>'
        '✓ Run downstream flood scenario<br>'
        '✓ Identify affected settlements<br>'
        '✓ Identify critical infrastructure<br>'
        '✓ Issue appropriate warning<br>'
        '✓ Coordinate evacuation response'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# ROUTER
# ============================================================

if st.session_state.page == "Dashboard":

    dashboard()

elif st.session_state.page == "Dam Monitoring":

    dam_monitoring()

elif st.session_state.page == "Prediction":

    prediction()

elif st.session_state.page == "Flood Simulation":

    flood_simulation()

elif st.session_state.page == "Emergency Center":

    emergency_center()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="hydro-footer">'
    'HYDROSCOPE • SMART INDIA HACKATHON PROTOTYPE<br><br>'
    'Monitor → Predict → Simulate → Assess Impact → Alert<br><br>'
    'Prototype data and model outputs are for demonstration purposes.'
    '</div>',
    unsafe_allow_html=True
)
