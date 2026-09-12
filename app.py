import math
import requests
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="HYDROSCOPE",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# PAGE SELECTION
# ============================================================

page_names = {
    "dashboard": "📊 Dashboard",
    "monitoring": "🏞️ Dam Monitoring",
    "prediction": "🔮 Prediction",
    "flood": "🌊 Flood Simulation",
    "emergency": "🚨 Emergency Center"
}

if "page" not in st.query_params:
    st.query_params["page"] = "dashboard"

current_page = st.query_params.get("page", "dashboard")

if current_page not in page_names:
    current_page = "dashboard"


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
<style>

html, body {
    background: #061522 !important;
}

.stApp {
    background:
        radial-gradient(
            circle at 15% 15%,
            rgba(0, 180, 255, 0.13),
            transparent 30%
        ),
        radial-gradient(
            circle at 85% 80%,
            rgba(0, 110, 255, 0.10),
            transparent 35%
        ),
        linear-gradient(
            135deg,
            #04101c,
            #071b2b 50%,
            #03111d
        );
    color: white;
}

.block-container {
    max-width: 1450px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}


/* ============================================================
   GLASS HEADER
   ============================================================ */

.hydro-header {
    padding: 25px 30px;
    margin-bottom: 18px;

    border-radius: 24px;

    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,0.09),
            rgba(255,255,255,0.035)
        );

    border: 1px solid rgba(255,255,255,0.13);

    backdrop-filter: blur(18px);

    box-shadow:
        0 12px 45px rgba(0,0,0,0.30),
        inset 0 1px 0 rgba(255,255,255,0.08);
}

.hydro-title {
    font-size: 42px;
    font-weight: 850;
    letter-spacing: 4px;
    margin: 0;
}

.hydro-subtitle {
    margin-top: 5px;
    color: #91bad4;
    font-size: 14px;
}


/* ============================================================
   SECTION TITLES
   ============================================================ */

.section-title {
    font-size: 25px;
    font-weight: 750;
    margin: 20px 0 15px 0;
}


/* ============================================================
   GLASS CARDS
   ============================================================ */

.glass-card {
    padding: 22px;

    border-radius: 20px;

    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,0.075),
            rgba(255,255,255,0.035)
        );

    border: 1px solid rgba(255,255,255,0.12);

    backdrop-filter: blur(16px);

    box-shadow:
        0 12px 35px rgba(0,0,0,0.20),
        inset 0 1px 0 rgba(255,255,255,0.06);
}


/* ============================================================
   METRIC CARDS
   ============================================================ */

.metric-card {
    padding: 20px;
    min-height: 125px;

    border-radius: 18px;

    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,0.075),
            rgba(255,255,255,0.035)
        );

    border: 1px solid rgba(255,255,255,0.11);

    box-shadow:
        0 10px 30px rgba(0,0,0,0.18);

    transition:
        transform 0.25s ease,
        border-color 0.25s ease,
        box-shadow 0.25s ease;
}

.metric-card:hover {
    transform: translateY(-4px);

    border-color: rgba(0,190,255,0.35);

    box-shadow:
        0 14px 35px rgba(0,140,255,0.16);
}

.metric-label {
    color: #88aec7;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.metric-value {
    font-size: 29px;
    font-weight: 800;
    margin-top: 8px;
}

.metric-small {
    color: #7898ad;
    font-size: 11px;
    margin-top: 5px;
}


/* ============================================================
   DAM CARDS
   ============================================================ */

.dam-card {
    padding: 18px;
    margin-bottom: 12px;

    border-radius: 18px;

    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,0.065),
            rgba(255,255,255,0.025)
        );

    border: 1px solid rgba(255,255,255,0.10);

    transition:
        transform 0.25s ease,
        border-color 0.25s ease,
        background 0.25s ease;
}

.dam-card:hover {
    transform: translateY(-3px);

    border-color:
        rgba(0,180,255,0.35);

    background:
        rgba(0,150,255,0.08);
}


/* ============================================================
   WEATHER
   ============================================================ */

.weather-box {
    padding: 22px;

    border-radius: 20px;

    background:
        linear-gradient(
            135deg,
            rgba(0,155,255,0.18),
            rgba(0,80,160,0.06)
        );

    border:
        1px solid rgba(70,190,255,0.22);
}

.weather-temp {
    font-size: 42px;
    font-weight: 800;
}


/* ============================================================
   ALERTS
   ============================================================ */

.alert-box {
    padding: 18px;

    border-radius: 16px;

    background:
        rgba(255,70,60,0.10);

    border:
        1px solid rgba(255,80,70,0.28);
}

.info-box {
    padding: 18px;

    border-radius: 16px;

    background:
        rgba(0,160,255,0.08);

    border:
        1px solid rgba(0,170,255,0.20);
}


/* ============================================================
   SHUTTERS
   ============================================================ */

.shutter {
    text-align: center;
    padding: 18px 5px;
    border-radius: 14px;

    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;
}

.shutter:hover {
    transform: translateY(-4px);
}


/* ============================================================
   BUTTONS
   ============================================================ */

div.stButton > button {
    border-radius: 12px;

    border:
        1px solid rgba(255,255,255,0.14);

    background:
        rgba(255,255,255,0.06);

    color: white;

    transition:
        all 0.20s ease;
}

div.stButton > button:hover {
    transform: translateY(-2px);

    border-color:
        rgba(0,190,255,0.55);

    background:
        rgba(0,150,255,0.14);

    box-shadow:
        0 0 18px rgba(0,160,255,0.18);
}

div.stButton > button:active {
    transform: scale(0.96);
}


/* ============================================================
   FOOTER
   ============================================================ */

.footer {
    text-align: center;
    color: #5e8198;
    font-size: 11px;
    padding: 30px 0 10px;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
<div class="hydro-header">

    <div class="hydro-title">
        💧 HYDROSCOPE
    </div>

    <div class="hydro-subtitle">
        Intelligent Dam Monitoring • Water Prediction •
        Flood Simulation • Emergency Decision Support
    </div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# CUSTOM NAVIGATION
# ============================================================

nav_html = f"""
<!DOCTYPE html>

<html>

<head>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    background: transparent;
    font-family: Arial, sans-serif;
}}

.nav {{
    width: 100%;

    display: flex;
    justify-content: center;
    align-items: center;

    gap: 8px;

    padding: 7px;

    border-radius: 18px;

    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,0.075),
            rgba(255,255,255,0.025)
        );

    border:
        1px solid rgba(255,255,255,0.11);

    backdrop-filter: blur(16px);

    box-shadow:
        0 10px 35px rgba(0,0,0,0.22);
}}

.nav-item {{
    position: relative;

    padding: 11px 17px;

    border-radius: 12px;

    color: #a5bfd0;

    font-size: 13px;

    font-weight: 650;

    text-decoration: none;

    white-space: nowrap;

    cursor: pointer;

    overflow: hidden;

    transition:
        color 0.25s ease,
        transform 0.20s ease,
        background 0.25s ease,
        box-shadow 0.25s ease;
}}

.nav-item::before {{
    content: "";

    position: absolute;

    width: 8px;
    height: 8px;

    left: 50%;
    top: 50%;

    border-radius: 50%;

    background:
        rgba(80,210,255,0.75);

    transform:
        translate(-50%, -50%)
        scale(0);

    opacity: 0;
}}

.nav-item:hover {{
    color: white;

    transform:
        translateY(-2px);

    background:
        rgba(0,160,255,0.10);

    box-shadow:
        0 0 18px rgba(0,170,255,0.12);
}}

.nav-item:active {{
    transform:
        scale(0.94);
}}

.nav-item:active::before {{
    animation:
        ripple 0.55s ease-out;
}}

.nav-item.active {{
    color: white;

    background:
        linear-gradient(
            135deg,
            rgba(0,165,255,0.22),
            rgba(0,95,190,0.12)
        );

    border:
        1px solid rgba(0,190,255,0.28);

    box-shadow:
        0 0 22px rgba(0,160,255,0.16),
        inset 0 0 15px rgba(0,170,255,0.06);
}}

.nav-item.active::after {{
    content: "";

    position: absolute;

    left: 20%;
    right: 20%;

    bottom: 3px;

    height: 2px;

    border-radius: 20px;

    background:
        linear-gradient(
            90deg,
            transparent,
            #39c8ff,
            transparent
        );

    box-shadow:
        0 0 8px #20bfff;
}}

@keyframes ripple {{

    0% {{
        transform:
            translate(-50%, -50%)
            scale(0);

        opacity: 0.8;
    }}

    100% {{
        transform:
            translate(-50%, -50%)
            scale(15);

        opacity: 0;
    }}

}}

@media(max-width: 900px) {{

    .nav {{
        flex-wrap: wrap;
    }}

    .nav-item {{
        font-size: 11px;
        padding: 9px 11px;
    }}

}}

</style>

</head>

<body>

<div class="nav">

<a
class="nav-item {'active' if current_page == 'dashboard' else ''}"
href="?page=dashboard"
>
📊 Dashboard
</a>

<a
class="nav-item {'active' if current_page == 'monitoring' else ''}"
href="?page=monitoring"
>
🏞️ Dam Monitoring
</a>

<a
class="nav-item {'active' if current_page == 'prediction' else ''}"
href="?page=prediction"
>
🔮 Prediction
</a>

<a
class="nav-item {'active' if current_page == 'flood' else ''}"
href="?page=flood"
>
🌊 Flood Simulation
</a>

<a
class="nav-item {'active' if current_page == 'emergency' else ''}"
href="?page=emergency"
>
🚨 Emergency Center
</a>

</div>

</body>

</html>
"""

components.html(
    nav_html,
    height=65,
    scrolling=False
)


# ============================================================
# DATA
# ============================================================

dams = {

    "Idukki Dam": {
        "lat": 9.8494,
        "lon": 76.9726,
        "level": 88,
        "inflow": 1800,
        "outflow": 600,
        "rainfall": 72,
        "shutters": 8,
        "open": 2,
        "opening": 20,
        "risk": "Moderate"
    },

    "Idamalayar Dam": {
        "lat": 10.2068,
        "lon": 76.7032,
        "level": 72,
        "inflow": 920,
        "outflow": 310,
        "rainfall": 48,
        "shutters": 4,
        "open": 1,
        "opening": 15,
        "risk": "Normal"
    },

    "Malankara Dam": {
        "lat": 9.7804,
        "lon": 76.8787,
        "level": 67,
        "inflow": 210,
        "outflow": 95,
        "rainfall": 41,
        "shutters": 6,
        "open": 1,
        "opening": 10,
        "risk": "Normal"
    },

    "Bhoothathankettu": {
        "lat": 10.1457,
        "lon": 76.6788,
        "level": 61,
        "inflow": 160,
        "outflow": 80,
        "rainfall": 36,
        "shutters": 5,
        "open": 1,
        "opening": 10,
        "risk": "Normal"
    },

    "Pamba Dam": {
        "lat": 9.3805,
        "lon": 76.9275,
        "level": 64,
        "inflow": 450,
        "outflow": 170,
        "rainfall": 39,
        "shutters": 6,
        "open": 1,
        "opening": 12,
        "risk": "Normal"
    },

    "Kakki Dam": {
        "lat": 9.3500,
        "lon": 77.0000,
        "level": 70,
        "inflow": 520,
        "outflow": 190,
        "rainfall": 44,
        "shutters": 4,
        "open": 1,
        "opening": 15,
        "risk": "Normal"
    },

    "Neyyar Dam": {
        "lat": 8.5350,
        "lon": 77.1450,
        "level": 58,
        "inflow": 190,
        "outflow": 75,
        "rainfall": 31,
        "shutters": 4,
        "open": 0,
        "opening": 0,
        "risk": "Normal"
    },

    "Banasura Sagar Dam": {
        "lat": 11.7000,
        "lon": 75.9500,
        "level": 63,
        "inflow": 330,
        "outflow": 120,
        "rainfall": 52,
        "shutters": 4,
        "open": 1,
        "opening": 10,
        "risk": "Normal"
    }
}


locations = {

    "Kochi": (9.9312, 76.2673),
    "Idukki": (9.8500, 76.9700),
    "Munnar": (10.0889, 77.0595),
    "Kothamangalam": (10.0580, 76.6290),
    "Thodupuzha": (9.8950, 76.7180),
    "Kottayam": (9.5916, 76.5222),
    "Pathanamthitta": (9.2648, 76.7870),
    "Alappuzha": (9.4981, 76.3388),
    "Thiruvananthapuram": (8.5241, 76.9366),
    "Wayanad": (11.6854, 76.1320)
}


# ============================================================
# DISTANCE
# ============================================================

def distance_km(
    lat1,
    lon1,
    lat2,
    lon2
):

    radius = 6371

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        +
        math.cos(p1)
        * math.cos(p2)
        * math.sin(dlon / 2) ** 2
    )

    return (
        radius
        * 2
        * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a)
        )
    )


def get_nearby_dams(
    location_name,
    radius=120
):

    lat, lon = locations[location_name]

    nearby = []

    for name, dam in dams.items():

        distance = distance_km(
            lat,
            lon,
            dam["lat"],
            dam["lon"]
        )

        if distance <= radius:

            nearby.append(
                {
                    "name": name,
                    "distance": distance,
                    **dam
                }
            )

    return sorted(
        nearby,
        key=lambda x: x["distance"]
    )


# ============================================================
# OPENWEATHER
# ============================================================

try:

    OPENWEATHER_API_KEY = st.secrets[
        "OPENWEATHER_API_KEY"
    ]

except Exception:

    OPENWEATHER_API_KEY = None


@st.cache_data(ttl=600)
def get_weather(
    lat,
    lon
):

    if not OPENWEATHER_API_KEY:

        return {
            "success": False,
            "error":
                "OpenWeather API key is not configured."
        }

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
    )

    params = {

        "lat": lat,
        "lon": lon,

        "appid":
            OPENWEATHER_API_KEY,

        "units":
            "metric"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code == 200:

            data = response.json()

            rainfall = (
                data
                .get("rain", {})
                .get("1h", 0)
            )

            return {

                "success": True,

                "temperature":
                    data["main"]["temp"],

                "feels_like":
                    data["main"]["feels_like"],

                "humidity":
                    data["main"]["humidity"],

                "pressure":
                    data["main"]["pressure"],

                "wind":
                    data["wind"]["speed"],

                "rainfall":
                    rainfall,

                "description":
                    data["weather"][0]["description"],

                "main":
                    data["weather"][0]["main"],

                "icon":
                    data["weather"][0]["icon"],

                "city":
                    data.get(
                        "name",
                        "Unknown"
                    )
            }

        if response.status_code == 401:

            return {
                "success": False,
                "error":
                    "Invalid OpenWeather API key."
            }

        if response.status_code == 429:

            return {
                "success": False,
                "error":
                    "OpenWeather rate limit reached."
            }

        return {
            "success": False,
            "error":
                f"Weather API error: {response.status_code}"
        }

    except requests.exceptions.RequestException:

        return {
            "success": False,
            "error":
                "Unable to connect to OpenWeather."
        }


# ============================================================
# HELPERS
# ============================================================

def metric_card(
    label,
    value,
    small=""
):

    st.markdown(
        f"""
<div class="metric-card">

    <div class="metric-label">
        {label}
    </div>

    <div class="metric-value">
        {value}
    </div>

    <div class="metric-small">
        {small}
    </div>

</div>
""",
        unsafe_allow_html=True
    )


def risk_class(
    risk
):

    if risk == "Normal":
        return "status-normal"

    if risk == "Moderate":
        return "status-moderate"

    if risk == "High":
        return "status-high"

    return "status-critical"


def water_chart(
    level
):

    hours = np.arange(0, 13)

    values = (
        level
        + np.sin(hours / 2) * 0.7
        + np.linspace(
            0,
            2.5,
            len(hours)
        )
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=hours,
            y=values,
            mode="lines+markers",
            name="Water Level"
        )
    )

    fig.update_layout(
        title="Water-Level Trend",
        xaxis_title="Forecast Hour",
        yaxis_title="Water Level (%)",
        template="plotly_dark",
        height=350,
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        )
    )

    return fig


# ============================================================
# DASHBOARD
# ============================================================

if current_page == "dashboard":

    st.markdown(
        '<div class="section-title">📍 Select Monitoring Location</div>',
        unsafe_allow_html=True
    )

    selected_location = st.selectbox(
        "Location",
        list(locations.keys())
    )

    lat, lon = locations[
        selected_location
    ]

    st.markdown(
        f"""
<div class="info-box">

<b>{selected_location}</b>

<br>

Coordinates:
{lat:.4f}, {lon:.4f}

<br>

Monitoring radius:
120 km

</div>
""",
        unsafe_allow_html=True
    )


    # ========================================================
    # WEATHER
    # ========================================================

    st.markdown(
        '<div class="section-title">🌦️ Live Weather</div>',
        unsafe_allow_html=True
    )

    weather = get_weather(
        lat,
        lon
    )

    if weather["success"]:

        w1, w2, w3, w4, w5 = st.columns(5)

        with w1:

            metric_card(
                "Temperature",
                f'{weather["temperature"]:.1f} °C',
                weather["description"]
            )

        with w2:

            metric_card(
                "Rainfall",
                f'{weather["rainfall"]:.1f} mm/h',
                "Last 1 hour"
            )

        with w3:

            metric_card(
                "Humidity",
                f'{weather["humidity"]}%',
                "Relative humidity"
            )

        with w4:

            metric_card(
                "Wind",
                f'{weather["wind"]:.1f} m/s',
                "Current wind"
            )

        with w5:

            metric_card(
                "Pressure",
                f'{weather["pressure"]} hPa',
                "Atmospheric pressure"
            )

    else:

        st.warning(
            "🌦️ "
            + weather["error"]
        )


    # ========================================================
    # MAP
    # ========================================================

    st.markdown(
        '<div class="section-title">🗺️ Dam Network</div>',
        unsafe_allow_html=True
    )

    nearby = get_nearby_dams(
        selected_location
    )

    m = folium.Map(
        location=[
            lat,
            lon
        ],
        zoom_start=8,
        tiles="CartoDB dark_matter"
    )

    folium.Marker(
        [
            lat,
            lon
        ],
        popup=selected_location,
        tooltip="Selected Location",
        icon=folium.Icon(
            color="blue",
            icon="user"
        )
    ).add_to(m)

    folium.Circle(
        [
            lat,
            lon
        ],
        radius=120000,
        color="#00aaff",
        fill=True,
        fill_opacity=0.05
    ).add_to(m)

    for dam in nearby:

        if dam["risk"] == "Normal":

            marker_color = "green"

        elif dam["risk"] == "Moderate":

            marker_color = "orange"

        else:

            marker_color = "red"

        folium.Marker(
            [
                dam["lat"],
                dam["lon"]
            ],
            popup=(
                f'<b>{dam["name"]}</b><br>'
                f'Water: {dam["level"]}%<br>'
                f'Risk: {dam["risk"]}<br>'
                f'Distance: '
                f'{dam["distance"]:.1f} km'
            ),
            tooltip=dam["name"],
            icon=folium.Icon(
                color=marker_color,
                icon="tint"
            )
        ).add_to(m)

    st_folium(
        m,
        width=None,
        height=550
    )


    # ========================================================
    # NEARBY DAMS
    # ========================================================

    st.markdown(
        '<div class="section-title">🏞️ Nearby Dams</div>',
        unsafe_allow_html=True
    )

    for dam in nearby:

        col1, col2, col3, col4 = st.columns(
            [3, 1.5, 1.5, 1]
        )

        with col1:

            st.markdown(
                f"""
<div class="dam-card">

<b>💧 {dam["name"]}</b>

<br>

<span style="color:#8faabd;">
{dam["distance"]:.1f} km from
{selected_location}
</span>

</div>
""",
                unsafe_allow_html=True
            )

        with col2:

            st.metric(
                "Water",
                f'{dam["level"]}%'
            )

        with col3:

            st.markdown(
                f"""
<div style="padding-top:12px;">

Risk:

<b>{dam["risk"]}</b>

</div>
""",
                unsafe_allow_html=True
            )

        with col4:

            if st.button(
                "View",
                key=f"view_{dam['name']}"
            ):

                st.session_state[
                    "selected_dam"
                ] = dam["name"]

                st.query_params[
                    "page"
                ] = "monitoring"

                st.rerun()


    # ========================================================
    # SYSTEM OVERVIEW
    # ========================================================

    st.markdown(
        '<div class="section-title">📡 System Overview</div>',
        unsafe_allow_html=True
    )

    avg_level = np.mean(
        [
            dam["level"]
            for dam in dams.values()
        ]
    )

    total_inflow = sum(
        dam["inflow"]
        for dam in dams.values()
    )

    total_outflow = sum(
        dam["outflow"]
        for dam in dams.values()
    )

    moderate_count = sum(
        1
        for dam in dams.values()
        if dam["risk"] == "Moderate"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        metric_card(
            "Dams Monitored",
            len(dams),
            "Prototype network"
        )

    with c2:

        metric_card(
            "Average Water",
            f"{avg_level:.1f}%",
            "Network average"
        )

    with c3:

        metric_card(
            "Total Inflow",
            f"{total_inflow:,} m³/s",
            "Prototype values"
        )

    with c4:

        metric_card(
            "Attention Required",
            moderate_count,
            "Moderate-risk dams"
        )

    st.markdown(
        '<div class="section-title">📈 Network Water Levels</div>',
        unsafe_allow_html=True
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=list(dams.keys()),
            y=[
                dam["level"]
                for dam in dams.values()
            ],
            name="Water Level"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        height=400,
        yaxis_title="Water Level (%)",
        xaxis_title="Dam"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# DAM MONITORING
# ============================================================

elif current_page == "monitoring":

    st.markdown(
        '<div class="section-title">🏞️ Dam Monitoring</div>',
        unsafe_allow_html=True
    )

    default_dam = st.session_state.get(
        "selected_dam",
        "Idukki Dam"
    )

    dam_name = st.selectbox(
        "Select Dam",
        list(dams.keys()),
        index=list(dams.keys()).index(
            default_dam
        )
    )

    dam = dams[dam_name]

    m = folium.Map(
        location=[
            dam["lat"],
            dam["lon"]
        ],
        zoom_start=10,
        tiles="CartoDB dark_matter"
    )

    folium.Marker(
        [
            dam["lat"],
            dam["lon"]
        ],
        popup=dam_name,
        tooltip=dam_name,
        icon=folium.Icon(
            color="blue",
            icon="tint"
        )
    ).add_to(m)

    st_folium(
        m,
        width=None,
        height=420
    )


    # ========================================================
    # LIVE DAM WEATHER
    # ========================================================

    st.markdown(
        '<div class="section-title">🌧️ Live Conditions at Dam</div>',
        unsafe_allow_html=True
    )

    dam_weather = get_weather(
        dam["lat"],
        dam["lon"]
    )

    if dam_weather["success"]:

        w1, w2, w3, w4 = st.columns(4)

        with w1:

            metric_card(
                "Temperature",
                f'{dam_weather["temperature"]:.1f} °C',
                dam_weather["description"]
            )

        with w2:

            metric_card(
                "Live Rainfall",
                f'{dam_weather["rainfall"]:.1f} mm/h',
                "OpenWeather"
            )

        with w3:

            metric_card(
                "Humidity",
                f'{dam_weather["humidity"]}%',
                "Current"
            )

        with w4:

            metric_card(
                "Wind",
                f'{dam_weather["wind"]:.1f} m/s',
                "Current"
            )

    else:

        st.warning(
            dam_weather["error"]
        )


    # ========================================================
    # STATUS
    # ========================================================

    st.markdown(
        '<div class="section-title">📊 Current Dam Status</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        metric_card(
            "Water Level",
            f'{dam["level"]}%',
            "Prototype value"
        )

    with c2:

        metric_card(
            "Inflow",
            f'{dam["inflow"]:,} m³/s',
            "Prototype value"
        )

    with c3:

        metric_card(
            "Outflow",
            f'{dam["outflow"]:,} m³/s',
            "Prototype value"
        )

    with c4:

        metric_card(
            "Risk",
            dam["risk"],
            "Decision support"
        )


    # ========================================================
    # SHUTTERS
    # ========================================================

    st.markdown(
        '<div class="section-title">🚪 Shutter Status</div>',
        unsafe_allow_html=True
    )

    shutter_cols = st.columns(
        min(
            dam["shutters"],
            8
        )
    )

    for i in range(
        dam["shutters"]
    ):

        with shutter_cols[i]:

            if i < dam["open"]:

                st.markdown(
                    """
<div class="shutter"
style="
background:rgba(0,150,255,0.22);
border:1px solid rgba(0,180,255,0.35);
">

🚪<br>
<b>OPEN</b>

</div>
""",
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    """
<div class="shutter"
style="
background:rgba(255,255,255,0.05);
border:1px solid rgba(255,255,255,0.10);
">

🚪<br>
<b>CLOSED</b>

</div>
""",
                    unsafe_allow_html=True
                )

    st.write(
        f'Current opening: **{dam["opening"]}%**'
    )

    st.plotly_chart(
        water_chart(
            dam["level"]
        ),
        use_container_width=True
    )


# ============================================================
# PREDICTION
# ============================================================

elif current_page == "prediction":

    st.markdown(
        '<div class="section-title">🔮 Water-Level & Release Prediction</div>',
        unsafe_allow_html=True
    )

    dam_name = st.selectbox(
        "Select Dam",
        list(dams.keys())
    )

    dam = dams[dam_name]

    rainfall_factor = st.slider(
        "Rainfall Scenario",
        0.5,
        2.5,
        1.0,
        0.1
    )

    hours = np.arange(
        0,
        25
    )

    predicted_levels = (
        dam["level"]
        +
        (
            dam["inflow"]
            / 1000
        )
        *
        rainfall_factor
        *
        np.sqrt(hours)
        *
        0.55
    )

    final_level = predicted_levels[-1]

    release_probability = min(
        99,
        max(
            5,
            int(
                dam["level"] * 0.7
                +
                rainfall_factor * 15
            )
        )
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        metric_card(
            "Current Level",
            f'{dam["level"]}%',
            dam_name
        )

    with c2:

        metric_card(
            "Predicted Level",
            f"{final_level:.1f}%",
            "24-hour prototype"
        )

    with c3:

        metric_card(
            "Release Probability",
            f"{release_probability}%",
            "Prototype indicator"
        )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=hours,
            y=predicted_levels,
            mode="lines+markers",
            name="Predicted Level"
        )
    )

    fig.add_hline(
        y=90,
        line_dash="dash",
        annotation_text="Illustrative Alert Level"
    )

    fig.update_layout(
        template="plotly_dark",
        height=450,
        xaxis_title="Hours Ahead",
        yaxis_title="Water Level (%)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown(
        """
<div class="info-box">

⚠️ <b>Decision Support Only</b>

<br><br>

This prediction is a prototype demonstration model.
It does not represent an official reservoir rule curve
and does not authorize automatic shutter operation.

</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# FLOOD SIMULATION
# ============================================================

elif current_page == "flood":

    st.markdown(
        '<div class="section-title">🌊 Dam-Break & Downstream Flood Simulation</div>',
        unsafe_allow_html=True
    )

    dam_name = st.selectbox(
        "Select Source Dam",
        list(dams.keys())
    )

    dam = dams[dam_name]

    breach = st.slider(
        "Breach Severity",
        10,
        100,
        50,
        5
    )

    rainfall_factor = st.slider(
        "Rainfall Amplification",
        1.0,
        3.0,
        1.0,
        0.1
    )

    duration = st.slider(
        "Simulation Duration (hours)",
        1,
        24,
        6
    )

    peak_flow = (
        dam["outflow"]
        +
        dam["inflow"]
        *
        (breach / 100)
        *
        rainfall_factor
    )

    arrival_time = max(
        0.5,
        8
        -
        breach / 18
        -
        rainfall_factor
    )

    affected_population = int(
        5000
        +
        peak_flow * 7
        +
        breach * 80
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        metric_card(
            "Estimated Peak Flow",
            f"{peak_flow:,.0f} m³/s",
            "Prototype"
        )

    with c2:

        metric_card(
            "First Arrival",
            f"{arrival_time:.1f} h",
            "Estimated"
        )

    with c3:

        metric_card(
            "Potentially Affected",
            f"{affected_population:,}",
            "Illustrative"
        )

    hours = np.linspace(
        0,
        duration,
        100
    )

    flow = (
        peak_flow
        *
        np.exp(
            -(
                (hours - arrival_time) ** 2
            )
            /
            max(
                0.2,
                duration / 3
            )
        )
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=hours,
            y=flow,
            fill="tozeroy",
            name="Flood Flow"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        height=420,
        xaxis_title="Time (hours)",
        yaxis_title="Flow (m³/s)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown(
        '<div class="section-title">🏘️ Potential Downstream Impact</div>',
        unsafe_allow_html=True
    )

    impact_data = pd.DataFrame(
        {
            "Zone": [
                "Immediate Zone",
                "Downstream Zone 1",
                "Downstream Zone 2",
                "Extended Zone"
            ],

            "Estimated Arrival": [
                f"{arrival_time:.1f} h",
                f"{arrival_time + 1.2:.1f} h",
                f"{arrival_time + 2.5:.1f} h",
                f"{arrival_time + 4.0:.1f} h"
            ],

            "Risk": [
                "Critical",
                "High",
                "Moderate",
                "Low"
            ]
        }
    )

    st.dataframe(
        impact_data,
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        """
<div class="alert-box">

🚨 <b>Simulation Warning</b>

<br><br>

This is a simplified prototype.
Real flood propagation requires terrain elevation,
river geometry, hydraulic modelling, rainfall-runoff
modelling, reservoir bathymetry and validated datasets.

</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# EMERGENCY
# ============================================================

elif current_page == "emergency":

    st.markdown(
        '<div class="section-title">🚨 Emergency Response Center</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
<div class="alert-box">

<b>⚠️ HYDROSCOPE ALERT SYSTEM</b>

<br><br>

This panel supports emergency decision-making during
extreme rainfall, reservoir stress and downstream flood
scenarios.

</div>
""",
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">📢 Active Alerts</div>',
        unsafe_allow_html=True
    )

    alerts = [

        (
            "🌧️ Heavy Rainfall",
            "Monitor reservoir inflow and downstream river levels."
        ),

        (
            "🌊 Rising Water Level",
            "Review reservoir prediction and release scenarios."
        ),

        (
            "🚨 Flood Risk",
            "Review affected zones and estimated arrival times."
        )
    ]

    for title, message in alerts:

        st.markdown(
            f"""
<div class="dam-card">

<b>{title}</b>

<br>

<span style="color:#9bb7ca;">
{message}
</span>

</div>
""",
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="section-title">🧭 Emergency Checklist</div>',
        unsafe_allow_html=True
    )

    checklist = [

        "Verify current rainfall and reservoir conditions",

        "Check official dam operating instructions",

        "Evaluate downstream flood propagation",

        "Identify vulnerable villages and infrastructure",

        "Coordinate with disaster-management authorities",

        "Issue public warnings through authorized channels"
    ]

    for i, item in enumerate(checklist):

        st.checkbox(
            item,
            key=f"check_{i}"
        )

    st.markdown(
        """
<div class="info-box">

🛡️ <b>Important</b>

<br><br>

HYDROSCOPE is a decision-support prototype.
It does not independently operate dam shutters,
issue legally binding evacuation orders, or replace
authorized government control systems.

</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div class="footer">

💧 HYDROSCOPE • SMART INDIA HACKATHON PROTOTYPE

<br>

Weather data provided by OpenWeather

</div>
""",
    unsafe_allow_html=True
)
