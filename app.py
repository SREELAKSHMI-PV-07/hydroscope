import math
import requests
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium


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
# GLOBAL CSS
# ============================================================

st.markdown(
    """
<style>

html, body, [class*="css"] {
    font-family: Arial, sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(0, 160, 220, 0.14), transparent 30%),
        radial-gradient(circle at 90% 20%, rgba(0, 100, 180, 0.12), transparent 30%),
        linear-gradient(135deg, #03121e 0%, #061b2b 45%, #021019 100%);
    color: #f5f9ff;
}

/* Remove Streamlit top padding */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

/* Main headings */
h1, h2, h3, h4 {
    color: #f5f9ff !important;
}

/* HYDROSCOPE title */
.hero-title {
    font-size: 42px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 2px;
}

.hero-subtitle {
    font-size: 15px;
    color: #9fc5dd;
    letter-spacing: 1px;
    margin-bottom: 20px;
}

/* Navigation buttons */
div.stButton > button {
    width: 100%;
    min-height: 46px;
    border-radius: 14px;
    border: 1px solid rgba(100, 190, 240, 0.28);
    background: rgba(10, 39, 58, 0.72);
    color: #dff5ff;
    font-weight: 700;
    transition: all 0.18s ease;
    box-shadow: 0 4px 16px rgba(0,0,0,0.18);
}

div.stButton > button:hover {
    transform: translateY(-2px);
    border-color: rgba(100, 210, 255, 0.8);
    background: rgba(15, 75, 105, 0.85);
    box-shadow:
        0 0 18px rgba(0, 190, 255, 0.22),
        0 7px 20px rgba(0,0,0,0.25);
}

div.stButton > button:active {
    transform: scale(0.97);
}

/* Cards */
.card {
    background: rgba(9, 39, 57, 0.72);
    border: 1px solid rgba(112, 203, 244, 0.20);
    border-radius: 20px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow:
        0 12px 35px rgba(0,0,0,0.22),
        inset 0 1px 0 rgba(255,255,255,0.04);
}

/* Native Streamlit metric cards */
div[data-testid="stMetric"] {
    background: rgba(10, 40, 58, 0.72);
    border: 1px solid rgba(105, 195, 235, 0.20);
    border-radius: 17px;
    padding: 15px;
}

/* Select boxes */
div[data-baseweb="select"] > div {
    background: rgba(8, 37, 54, 0.85);
    border-color: rgba(100, 190, 230, 0.30);
}

/* Slider */
div[data-testid="stSlider"] {
    padding-top: 10px;
}

/* Info / warning boxes */
div[data-testid="stAlert"] {
    border-radius: 15px;
}

/* Dataframes */
div[data-testid="stDataFrame"] {
    border-radius: 15px;
    overflow: hidden;
}

/* Horizontal line */
hr {
    border-color: rgba(120, 200, 235, 0.14);
}

/* Footer */
.footer {
    text-align: center;
    color: #7195aa;
    font-size: 12px;
    padding-top: 25px;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# DEMO DAM DATABASE
# ============================================================

DAM_DATABASE = {
    "Idukki Dam": {
        "district": "Idukki",
        "lat": 9.8494,
        "lon": 76.9726,
        "water_level": 88.0,
        "inflow": 1800.0,
        "outflow": 600.0,
        "rainfall": 72.0,
        "total_shutters": 8,
        "open_shutters": 2,
        "opening_percent": 20,
        "risk": "Moderate",
        "status": "PROTOTYPE"
    },

    "Idamalayar Dam": {
        "district": "Ernakulam",
        "lat": 10.2068,
        "lon": 76.7032,
        "water_level": 72.0,
        "inflow": 920.0,
        "outflow": 310.0,
        "rainfall": 48.0,
        "total_shutters": 4,
        "open_shutters": 1,
        "opening_percent": 15,
        "risk": "Normal",
        "status": "PROTOTYPE"
    },

    "Malankara Dam": {
        "district": "Idukki",
        "lat": 9.7804,
        "lon": 76.8787,
        "water_level": 67.0,
        "inflow": 210.0,
        "outflow": 95.0,
        "rainfall": 41.0,
        "total_shutters": 6,
        "open_shutters": 1,
        "opening_percent": 10,
        "risk": "Normal",
        "status": "PROTOTYPE"
    },

    "Bhoothathankettu": {
        "district": "Ernakulam",
        "lat": 10.1457,
        "lon": 76.6788,
        "water_level": 61.0,
        "inflow": 160.0,
        "outflow": 80.0,
        "rainfall": 36.0,
        "total_shutters": 5,
        "open_shutters": 1,
        "opening_percent": 10,
        "risk": "Normal",
        "status": "PROTOTYPE"
    },

    "Pamba Dam": {
        "district": "Pathanamthitta",
        "lat": 9.3805,
        "lon": 76.9275,
        "water_level": 64.0,
        "inflow": 450.0,
        "outflow": 170.0,
        "rainfall": 39.0,
        "total_shutters": 6,
        "open_shutters": 1,
        "opening_percent": 12,
        "risk": "Normal",
        "status": "PROTOTYPE"
    },

    "Kakki Dam": {
        "district": "Pathanamthitta",
        "lat": 9.3500,
        "lon": 77.0000,
        "water_level": 70.0,
        "inflow": 520.0,
        "outflow": 190.0,
        "rainfall": 44.0,
        "total_shutters": 4,
        "open_shutters": 1,
        "opening_percent": 15,
        "risk": "Normal",
        "status": "PROTOTYPE"
    },

    "Neyyar Dam": {
        "district": "Thiruvananthapuram",
        "lat": 8.5350,
        "lon": 77.1450,
        "water_level": 58.0,
        "inflow": 190.0,
        "outflow": 75.0,
        "rainfall": 31.0,
        "total_shutters": 4,
        "open_shutters": 0,
        "opening_percent": 0,
        "risk": "Normal",
        "status": "PROTOTYPE"
    },

    "Banasura Sagar Dam": {
        "district": "Wayanad",
        "lat": 11.7000,
        "lon": 75.9500,
        "water_level": 63.0,
        "inflow": 330.0,
        "outflow": 120.0,
        "rainfall": 52.0,
        "total_shutters": 4,
        "open_shutters": 1,
        "opening_percent": 10,
        "risk": "Normal",
        "status": "PROTOTYPE"
    }
}


# ============================================================
# LOCATION DATABASE
# ============================================================

LOCATIONS = {
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
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def distance_km(lat1, lon1, lat2, lon2):
    radius = 6371

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)

    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = (
        math.sin(dp / 2) ** 2
        + math.cos(p1)
        * math.cos(p2)
        * math.sin(dl / 2) ** 2
    )

    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def nearby_dams(location_name, radius=120):
    lat, lon = LOCATIONS[location_name]

    result = []

    for name, dam in DAM_DATABASE.items():

        distance = distance_km(
            lat,
            lon,
            dam["lat"],
            dam["lon"]
        )

        if distance <= radius:

            item = dam.copy()
            item["name"] = name
            item["distance"] = distance

            result.append(item)

    return sorted(result, key=lambda x: x["distance"])


def water_level_chart(dam_name):

    dam = DAM_DATABASE[dam_name]

    current = dam["water_level"]

    hours = np.arange(-12, 1)

    trend = np.linspace(
        current - np.random.uniform(1.5, 4.0),
        current,
        len(hours)
    )

    return hours, trend


def predict_level(dam_name, rainfall_factor):

    dam = DAM_DATABASE[dam_name]

    current = dam["water_level"]

    net_flow = dam["inflow"] - dam["outflow"]

    increase = (
        net_flow / 1000
        * 1.8
        * rainfall_factor
    )

    return current + increase


def release_probability(dam_name):

    dam = DAM_DATABASE[dam_name]

    level_score = max(
        0,
        min(100, dam["water_level"])
    )

    rain_score = max(
        0,
        min(100, dam["rainfall"])
    )

    flow_score = max(
        0,
        min(100, dam["inflow"] / 20)
    )

    probability = (
        level_score * 0.45
        + rain_score * 0.25
        + flow_score * 0.30
    )

    return min(99, round(probability))


@st.cache_data(ttl=600)
def get_weather(lat, lon):

    try:

        api_key = st.secrets["OPENWEATHER_API_KEY"]

    except Exception:

        return {
            "success": False,
            "error": "OPENWEATHER_API_KEY is not configured in Streamlit Secrets."
        }

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code == 401:

            return {
                "success": False,
                "error": "OpenWeather API key is not active yet."
            }

        if response.status_code == 429:

            return {
                "success": False,
                "error": "OpenWeather API request limit reached."
            }

        response.raise_for_status()

        data = response.json()

        rainfall = 0.0

        if "rain" in data:

            rainfall = data["rain"].get(
                "1h",
                data["rain"].get("3h", 0.0)
            )

        return {
            "success": True,
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind": data["wind"]["speed"],
            "rainfall": rainfall,
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],
            "city": data.get("name", "Unknown")
        }

    except requests.exceptions.RequestException as error:

        return {
            "success": False,
            "error": f"Weather service unavailable: {error}"
        }

    except Exception as error:

        return {
            "success": False,
            "error": str(error)
        }


def create_dam_map(location_name):

    lat, lon = LOCATIONS[location_name]

    map_object = folium.Map(
        location=[lat, lon],
        zoom_start=8,
        tiles="CartoDB dark_matter"
    )

    folium.Circle(
        location=[lat, lon],
        radius=120000,
        color="#25b9ff",
        fill=True,
        fill_opacity=0.05,
        weight=2
    ).add_to(map_object)

    folium.Marker(
        [lat, lon],
        tooltip=f"📍 {location_name}",
        popup=f"Monitoring Location: {location_name}",
        icon=folium.Icon(
            color="blue",
            icon="map-marker"
        )
    ).add_to(map_object)

    for name, dam in DAM_DATABASE.items():

        distance = distance_km(
            lat,
            lon,
            dam["lat"],
            dam["lon"]
        )

        if distance <= 120:

            if dam["risk"] == "Moderate":
                marker_color = "orange"
            elif dam["risk"] == "High":
                marker_color = "red"
            else:
                marker_color = "green"

            popup = f"""
            <b>{name}</b><br>
            Water Level: {dam['water_level']}<br>
            Inflow: {dam['inflow']} m³/s<br>
            Outflow: {dam['outflow']} m³/s<br>
            Distance: {distance:.1f} km<br>
            Status: {dam['status']}
            """

            folium.Marker(
                [dam["lat"], dam["lon"]],
                tooltip=name,
                popup=folium.Popup(
                    popup,
                    max_width=300
                ),
                icon=folium.Icon(
                    color=marker_color,
                    icon="tint"
                )
            ).add_to(map_object)

    return map_object


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="hero-title">💧 HYDROSCOPE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hero-subtitle">'
    'INTELLIGENT DAM MONITORING • WATER PREDICTION • '
    'FLOOD SIMULATION • EMERGENCY DECISION SUPPORT'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# NAVIGATION
# ============================================================

pages = [
    ("🏠", "Dashboard"),
    ("🏗️", "Dam Monitoring"),
    ("🌦️", "Prediction"),
    ("🌊", "Flood Simulation"),
    ("🚨", "Emergency Center")
]

nav_columns = st.columns(len(pages))

for column, (icon, page_name) in zip(nav_columns, pages):

    with column:

        if st.button(
            f"{icon}  {page_name}",
            key=f"nav_{page_name}"
        ):

            st.session_state.page = page_name
            st.rerun()


st.divider()


# ============================================================
# DASHBOARD
# ============================================================

if st.session_state.page == "Dashboard":

    st.header("📊 System Dashboard")

    st.write(
        "Monitor nearby dams, rainfall and reservoir conditions "
        "from one unified decision-support interface."
    )

    location = st.selectbox(
        "📍 Select Monitoring Location",
        list(LOCATIONS.keys())
    )

    lat, lon = LOCATIONS[location]

    nearby = nearby_dams(location)

    st.markdown(
        f"""
        <div class="card">
        <b>📍 {location}</b><br><br>
        Coordinates: {lat:.4f}, {lon:.4f}<br>
        Monitoring radius: 120 km
        </div>
        """,
        unsafe_allow_html=True
    )

    # Weather
    st.subheader("🌦️ Live Weather")

    weather = get_weather(lat, lon)

    if weather["success"]:

        weather_cols = st.columns(5)

        weather_cols[0].metric(
            "🌡️ Temperature",
            f"{weather['temperature']:.1f} °C"
        )

        weather_cols[1].metric(
            "🌧️ Rainfall",
            f"{weather['rainfall']:.1f} mm"
        )

        weather_cols[2].metric(
            "💧 Humidity",
            f"{weather['humidity']}%"
        )

        weather_cols[3].metric(
            "💨 Wind",
            f"{weather['wind']:.1f} m/s"
        )

        weather_cols[4].metric(
            "🔵 Pressure",
            f"{weather['pressure']} hPa"
        )

        st.caption(
            f"Weather condition: {weather['description'].title()} • "
            "Weather data provided by OpenWeather"
        )

    else:

        st.warning(
            f"🌦️ Weather data unavailable: {weather['error']}"
        )

    # Nearby dams
    st.subheader("🏗️ Nearby Dams")

    if nearby:

        dam_columns = st.columns(3)

        for index, dam in enumerate(nearby):

            with dam_columns[index % 3]:

                st.markdown(
                    f"""
                    <div class="card">
                    <h4>🏗️ {dam['name']}</h4>
                    <b>Water Level:</b> {dam['water_level']:.1f}<br>
                    <b>Inflow:</b> {dam['inflow']:.0f} m³/s<br>
                    <b>Outflow:</b> {dam['outflow']:.0f} m³/s<br>
                    <b>Rainfall:</b> {dam['rainfall']:.0f} mm<br>
                    <b>Risk:</b> {dam['risk']}<br><br>
                    <small>⚠️ {dam['status']} DATA</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # Map
    st.subheader("🗺️ Dam Monitoring Map")

    map_object = create_dam_map(location)

    st_folium(
        map_object,
        width=None,
        height=500,
        returned_objects=[]
    )

    # Network chart
    st.subheader("📈 Nearby Reservoir Levels")

    if nearby:

        chart_df = pd.DataFrame({
            "Dam": [d["name"] for d in nearby],
            "Water Level": [d["water_level"] for d in nearby]
        })

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=chart_df["Dam"],
                y=chart_df["Water Level"],
                name="Water Level"
            )
        )

        fig.update_layout(
            height=400,
            template="plotly_dark",
            title="Current Water Level Comparison",
            xaxis_title="Dam",
            yaxis_title="Water Level"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# DAM MONITORING
# ============================================================

elif st.session_state.page == "Dam Monitoring":

    st.header("🏗️ Dam Monitoring")

    dam_name = st.selectbox(
        "Select Dam",
        list(DAM_DATABASE.keys())
    )

    dam = DAM_DATABASE[dam_name]

    st.info(
        f"⚠️ Current reservoir figures are {dam['status'].lower()} "
        "values for the prototype. They are not being presented as "
        "live operational control data."
    )

    cols = st.columns(4)

    cols[0].metric(
        "💧 Water Level",
        f"{dam['water_level']:.1f}"
    )

    cols[1].metric(
        "⬆️ Inflow",
        f"{dam['inflow']:.0f} m³/s"
    )

    cols[2].metric(
        "⬇️ Outflow",
        f"{dam['outflow']:.0f} m³/s"
    )

    cols[3].metric(
        "🌧️ Rainfall",
        f"{dam['rainfall']:.0f} mm"
    )

    st.subheader("🚪 Shutter Status")

    shutter_cols = st.columns(dam["total_shutters"])

    for i in range(dam["total_shutters"]):

        if i < dam["open_shutters"]:

            shutter_cols[i].success(
                f"OPEN\n\n{dam['opening_percent']}%"
            )

        else:

            shutter_cols[i].info(
                "CLOSED"
            )

    st.subheader("📈 Water-Level Trend")

    hours, levels = water_level_chart(dam_name)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=hours,
            y=levels,
            mode="lines+markers",
            name="Water Level"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        height=420,
        xaxis_title="Hours",
        yaxis_title="Water Level"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("📊 Flow Balance")

    balance = dam["inflow"] - dam["outflow"]

    if balance > 0:

        st.warning(
            f"⬆️ Net positive flow: {balance:.0f} m³/s"
        )

    else:

        st.success(
            f"⬇️ Net negative flow: {abs(balance):.0f} m³/s"
        )

    st.markdown(
        f"""
        <div class="card">
        <b>Data Status:</b> {dam['status']}<br>
        <b>District:</b> {dam['district']}<br>
        <b>Coordinates:</b> {dam['lat']:.4f}, {dam['lon']:.4f}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PREDICTION
# ============================================================

elif st.session_state.page == "Prediction":

    st.header("🌦️ Water-Level Prediction")

    st.write(
        "Estimate short-term reservoir behaviour using current "
        "water level, inflow, outflow and rainfall conditions."
    )

    dam_name = st.selectbox(
        "Select Dam",
        list(DAM_DATABASE.keys())
    )

    dam = DAM_DATABASE[dam_name]

    rainfall_factor = st.slider(
        "🌧️ Expected Rainfall Factor",
        min_value=0.5,
        max_value=3.0,
        value=1.0,
        step=0.1
    )

    predicted = predict_level(
        dam_name,
        rainfall_factor
    )

    probability = release_probability(
        dam_name
    )

    cols = st.columns(3)

    cols[0].metric(
        "Current Level",
        f"{dam['water_level']:.1f}"
    )

    cols[1].metric(
        "Predicted Level",
        f"{predicted:.1f}"
    )

    cols[2].metric(
        "Release Probability",
        f"{probability}%"
    )

    if probability >= 70:

        st.error(
            "🚨 HIGH POSSIBILITY OF CONTROLLED RELEASE"
        )

    elif probability >= 45:

        st.warning(
            "⚠️ MODERATE POSSIBILITY OF CONTROLLED RELEASE"
        )

    else:

        st.success(
            "🟢 LOW POSSIBILITY OF CONTROLLED RELEASE"
        )

    st.subheader("📈 Forecast")

    forecast_hours = np.arange(0, 13)

    forecast_levels = np.linspace(
        dam["water_level"],
        predicted,
        len(forecast_hours)
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=forecast_hours,
            y=forecast_levels,
            mode="lines+markers",
            name="Predicted Level"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        height=430,
        title=f"12-Hour Forecast — {dam_name}",
        xaxis_title="Forecast Hours",
        yaxis_title="Water Level"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        "Prototype prediction model. It is intended for decision "
        "support and must not be used as an autonomous dam-control system."
    )


# ============================================================
# FLOOD SIMULATION
# ============================================================

elif st.session_state.page == "Flood Simulation":

    st.header("🌊 Dam-Break & Downstream Flood Simulation")

    st.write(
        "Explore a simplified breach scenario and estimate "
        "downstream flood propagation."
    )

    dam_name = st.selectbox(
        "Select Dam",
        list(DAM_DATABASE.keys())
    )

    dam = DAM_DATABASE[dam_name]

    severity = st.slider(
        "💥 Breach Severity",
        10,
        100,
        50
    )

    rainfall_factor = st.slider(
        "🌧️ Rainfall Multiplier",
        0.5,
        3.0,
        1.0,
        0.1
    )

    breach_duration = st.slider(
        "⏱️ Breach Duration (minutes)",
        5,
        120,
        30,
        5
    )

    peak_flow = (
        dam["outflow"]
        * (severity / 25)
        * rainfall_factor
        + dam["inflow"] * 0.25
    )

    arrival_time = max(
        10,
        120 - severity + breach_duration * 0.15
    )

    affected_population = int(
        5000
        * (severity / 100)
        * rainfall_factor
    )

    cols = st.columns(4)

    cols[0].metric(
        "🌊 Estimated Peak Flow",
        f"{peak_flow:.0f} m³/s"
    )

    cols[1].metric(
        "⏱️ First Arrival",
        f"{arrival_time:.0f} min"
    )

    cols[2].metric(
        "👥 Potentially Affected",
        f"{affected_population:,}"
    )

    cols[3].metric(
        "⚠️ Severity",
        f"{severity}%"
    )

    st.subheader("🗺️ Downstream Impact Zones")

    zones = pd.DataFrame({
        "Zone": [
            "Immediate Downstream",
            "Near Downstream",
            "Extended Downstream",
            "Low-Lying Areas"
        ],
        "Estimated Arrival (min)": [
            arrival_time,
            arrival_time + 20,
            arrival_time + 45,
            arrival_time + 70
        ],
        "Risk": [
            "CRITICAL",
            "HIGH",
            "MODERATE",
            "WATCH"
        ]
    })

    st.dataframe(
        zones,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("📈 Flood Propagation")

    times = np.arange(
        0,
        max(121, int(arrival_time + 100)),
        5
    )

    flow = np.zeros(len(times))

    for i, t in enumerate(times):

        if t >= arrival_time:

            elapsed = t - arrival_time

            flow[i] = peak_flow * math.exp(
                -elapsed / 40
            )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=times,
            y=flow,
            mode="lines",
            fill="tozeroy",
            name="Flood Flow"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        height=430,
        title="Estimated Flood Wave",
        xaxis_title="Time (minutes)",
        yaxis_title="Flow (m³/s)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.warning(
        "⚠️ This is a simplified prototype simulation. "
        "A production system should use DEM/topography, "
        "hydraulic modelling, river networks and validated "
        "dam-break parameters."
    )


# ============================================================
# EMERGENCY CENTER
# ============================================================

elif st.session_state.page == "Emergency Center":

    st.header("🚨 Emergency Decision Center")

    st.error(
        "🚨 EMERGENCY DECISION-SUPPORT MODE"
    )

    st.subheader("⚠️ Immediate Response Checklist")

    checklist = [
        "Verify reservoir and rainfall observations.",
        "Check current gate/shutter status.",
        "Assess downstream river level.",
        "Identify vulnerable settlements.",
        "Check roads and bridge accessibility.",
        "Coordinate with district disaster-management authorities.",
        "Issue evacuation warnings through authorised channels.",
        "Continue monitoring water-level changes."
    ]

    for item in checklist:

        st.checkbox(
            item,
            key=f"emergency_{item}"
        )

    st.subheader("📡 System Status")

    status_cols = st.columns(4)

    status_cols[0].success(
        "🟢 Weather Service"
    )

    status_cols[1].warning(
        "🟡 Dam Data"
    )

    status_cols[2].success(
        "🟢 Prediction Engine"
    )

    status_cols[3].success(
        "🟢 Flood Model"
    )

    st.subheader("📢 Alert Classification")

    alert_level = st.select_slider(
        "Select current alert level",
        options=[
            "NORMAL",
            "WATCH",
            "ADVISORY",
            "WARNING",
            "CRITICAL"
        ],
        value="WATCH"
    )

    if alert_level == "NORMAL":

        st.success("🟢 NORMAL — Continue routine monitoring.")

    elif alert_level == "WATCH":

        st.info("🔵 WATCH — Increase monitoring frequency.")

    elif alert_level == "ADVISORY":

        st.warning(
            "🟡 ADVISORY — Prepare response teams and verify downstream conditions."
        )

    elif alert_level == "WARNING":

        st.warning(
            "🟠 WARNING — Authorities should evaluate protective and evacuation actions."
        )

    else:

        st.error(
            "🔴 CRITICAL — Immediate coordination with authorised emergency authorities is required."
        )

    st.subheader("🛡️ HYDROSCOPE Safety Principle")

    st.markdown(
        """
        HYDROSCOPE is a **decision-support system**.

        It does not autonomously operate dam gates or issue
        official evacuation orders.

        Final operational decisions must remain with authorised
        dam-management and disaster-management authorities.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer">
    💧 HYDROSCOPE • Intelligent Dam & Flood Decision Support System<br>
    Smart India Hackathon Prototype • Kerala
    </div>
    """,
    unsafe_allow_html=True
)
