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

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(0,160,220,0.14), transparent 30%),
        radial-gradient(circle at 90% 20%, rgba(0,100,180,0.12), transparent 30%),
        linear-gradient(135deg, #03121e 0%, #061b2b 45%, #021019 100%);
    color: #f5f9ff;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

h1, h2, h3, h4 {
    color: #f5f9ff !important;
}

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

div.stButton > button {
    width: 100%;
    min-height: 46px;
    border-radius: 14px;
    border: 1px solid rgba(100,190,240,0.28);
    background: rgba(10,39,58,0.72);
    color: #dff5ff;
    font-weight: 700;
    transition: all 0.18s ease;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    border-color: rgba(100,210,255,0.8);
    background: rgba(15,75,105,0.85);
    box-shadow:
        0 0 18px rgba(0,190,255,0.22),
        0 7px 20px rgba(0,0,0,0.25);
}

div.stButton > button:active {
    transform: scale(0.97);
}

.card {
    background: rgba(9,39,57,0.72);
    border: 1px solid rgba(112,203,244,0.20);
    border-radius: 20px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow:
        0 12px 35px rgba(0,0,0,0.22),
        inset 0 1px 0 rgba(255,255,255,0.04);
}

div[data-testid="stMetric"] {
    background: rgba(10,40,58,0.72);
    border: 1px solid rgba(105,195,235,0.20);
    border-radius: 17px;
    padding: 15px;
}

div[data-baseweb="select"] > div {
    background: rgba(8,37,54,0.85);
    border-color: rgba(100,190,230,0.30);
}

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
# DAM DATABASE
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
# BASIC FUNCTIONS
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

    return radius * 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )


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

    return sorted(
        result,
        key=lambda x: x["distance"]
    )


# ============================================================
# OPENWEATHER CURRENT WEATHER
# ============================================================

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
                0.0
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
            "error": str(error)
        }


# ============================================================
# OPENWEATHER RAINFALL FORECAST
# ============================================================

@st.cache_data(ttl=600)
def get_rainfall_forecast(lat, lon):

    try:

        api_key = st.secrets["OPENWEATHER_API_KEY"]

    except Exception:

        return {
            "success": False,
            "error": "OPENWEATHER_API_KEY is not configured."
        }

    url = "https://api.openweathermap.org/data/2.5/forecast"

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

        forecast_rows = []

        for item in data.get("list", []):

            rainfall = 0.0

            if "rain" in item:

                rainfall = item["rain"].get(
                    "3h",
                    0.0
                )

            forecast_rows.append(
                {
                    "datetime": pd.to_datetime(
                        item["dt"],
                        unit="s"
                    ),
                    "rainfall": rainfall,
                    "temperature": item["main"]["temp"],
                    "description": item["weather"][0]["description"]
                }
            )

        forecast_df = pd.DataFrame(
            forecast_rows
        )

        return {
            "success": True,
            "data": forecast_df
        }

    except requests.exceptions.RequestException as error:

        return {
            "success": False,
            "error": str(error)
        }


# ============================================================
# AUTOMATIC RAINFALL SUMMARY
# ============================================================

def rainfall_summary(forecast_df):

    if forecast_df.empty:

        return {
            "rain_6h": 0,
            "rain_12h": 0,
            "rain_24h": 0,
            "peak_3h": 0,
            "trend": "Unknown"
        }

    now = forecast_df["datetime"].min()

    six_hour = forecast_df[
        forecast_df["datetime"]
        <= now + pd.Timedelta(hours=6)
    ]["rainfall"].sum()

    twelve_hour = forecast_df[
        forecast_df["datetime"]
        <= now + pd.Timedelta(hours=12)
    ]["rainfall"].sum()

    twenty_four_hour = forecast_df[
        forecast_df["datetime"]
        <= now + pd.Timedelta(hours=24)
    ]["rainfall"].sum()

    peak_3h = forecast_df["rainfall"].max()

    first_half = forecast_df.head(
        max(1, len(forecast_df) // 3)
    )["rainfall"].mean()

    second_half = forecast_df.tail(
        max(1, len(forecast_df) // 3)
    )["rainfall"].mean()

    if second_half > first_half * 1.25:
        trend = "Increasing"

    elif second_half < first_half * 0.75:
        trend = "Decreasing"

    else:
        trend = "Stable"

    return {
        "rain_6h": round(six_hour, 1),
        "rain_12h": round(twelve_hour, 1),
        "rain_24h": round(twenty_four_hour, 1),
        "peak_3h": round(peak_3h, 1),
        "trend": trend
    }


# ============================================================
# WATER-LEVEL PREDICTION
# ============================================================

def predict_water_level(
    dam,
    rainfall_24h
):

    current_level = dam["water_level"]

    net_flow = (
        dam["inflow"]
        - dam["outflow"]
    )

    # Prototype conversion factor.
    # This will later be replaced by a trained
    # hydrological/ML model using historical data.

    flow_component = (
        net_flow / 1000
    ) * 0.75

    rainfall_component = (
        rainfall_24h / 100
    ) * 2.5

    predicted = (
        current_level
        + flow_component
        + rainfall_component
    )

    return round(
        predicted,
        2
    )


# ============================================================
# RELEASE PROBABILITY
# ============================================================

def release_probability(
    dam,
    predicted_level
):

    current_score = min(
        100,
        dam["water_level"]
    )

    predicted_score = min(
        100,
        predicted_level
    )

    inflow_score = min(
        100,
        dam["inflow"] / 20
    )

    probability = (
        current_score * 0.35
        + predicted_score * 0.35
        + inflow_score * 0.30
    )

    return min(
        99,
        round(probability)
    )


# ============================================================
# WATER LEVEL TREND
# ============================================================

def water_level_chart(dam_name):

    dam = DAM_DATABASE[dam_name]

    current = dam["water_level"]

    hours = np.arange(-12, 1)

    levels = np.linspace(
        current - 3.0,
        current,
        len(hours)
    )

    return hours, levels


# ============================================================
# MAP
# ============================================================

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

nav_columns = st.columns(
    len(pages)
)

for column, (icon, page_name) in zip(
    nav_columns,
    pages
):

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

    nearby = nearby_dams(
        location
    )

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

    st.subheader("🌦️ Live Weather")

    weather = get_weather(
        lat,
        lon
    )

    if weather["success"]:

        cols = st.columns(5)

        cols[0].metric(
            "🌡️ Temperature",
            f"{weather['temperature']:.1f} °C"
        )

        cols[1].metric(
            "🌧️ Rainfall",
            f"{weather['rainfall']:.1f} mm"
        )

        cols[2].metric(
            "💧 Humidity",
            f"{weather['humidity']}%"
        )

        cols[3].metric(
            "💨 Wind",
            f"{weather['wind']:.1f} m/s"
        )

        cols[4].metric(
            "🔵 Pressure",
            f"{weather['pressure']} hPa"
        )

        st.caption(
            f"Condition: {weather['description'].title()} • "
            "Weather data provided by OpenWeather"
        )

    else:

        st.warning(
            f"🌦️ Weather unavailable: {weather['error']}"
        )

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

    st.subheader("🗺️ Dam Monitoring Map")

    st_folium(
        create_dam_map(location),
        width=None,
        height=500,
        returned_objects=[]
    )

    st.subheader("📈 Nearby Reservoir Levels")

    if nearby:

        chart_df = pd.DataFrame({
            "Dam": [
                d["name"]
                for d in nearby
            ],
            "Water Level": [
                d["water_level"]
                for d in nearby
            ]
        })

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=chart_df["Dam"],
                y=chart_df["Water Level"]
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
        f"⚠️ Current reservoir figures are "
        f"{dam['status'].lower()} values for the prototype. "
        "They are not being presented as live operational control data."
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

    shutter_cols = st.columns(
        dam["total_shutters"]
    )

    for i in range(
        dam["total_shutters"]
    ):

        if i < dam["open_shutters"]:

            shutter_cols[i].success(
                f"OPEN\n\n{dam['opening_percent']}%"
            )

        else:

            shutter_cols[i].info(
                "CLOSED"
            )

    st.subheader("📈 Water-Level Trend")

    hours, levels = water_level_chart(
        dam_name
    )

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


# ============================================================
# PREDICTION
# ============================================================

elif st.session_state.page == "Prediction":

    st.header("🌧️ Water-Level Prediction")

    st.write(
        "HYDROSCOPE automatically analyses current weather "
        "and forecast rainfall to estimate future reservoir behaviour."
    )

    dam_name = st.selectbox(
        "🏗️ Select Dam",
        list(DAM_DATABASE.keys())
    )

    dam = DAM_DATABASE[dam_name]

    forecast = get_rainfall_forecast(
        dam["lat"],
        dam["lon"]
    )

    if not forecast["success"]:

        st.error(
            f"Unable to obtain rainfall forecast: "
            f"{forecast['error']}"
        )

        st.stop()

    forecast_df = forecast["data"]

    summary = rainfall_summary(
        forecast_df
    )

    # --------------------------------------------------------
    # AUTOMATIC RAINFALL PREDICTION
    # --------------------------------------------------------

    st.subheader(
        "🌦️ System-Predicted Rainfall"
    )

    rain_cols = st.columns(4)

    rain_cols[0].metric(
        "Next 6 Hours",
        f"{summary['rain_6h']} mm"
    )

    rain_cols[1].metric(
        "Next 12 Hours",
        f"{summary['rain_12h']} mm"
    )

    rain_cols[2].metric(
        "Next 24 Hours",
        f"{summary['rain_24h']} mm"
    )

    rain_cols[3].metric(
        "Peak 3-Hour Rain",
        f"{summary['peak_3h']} mm"
    )

    if summary["trend"] == "Increasing":

        st.warning(
            "⬆️ Rainfall trend detected: INCREASING"
        )

    elif summary["trend"] == "Decreasing":

        st.success(
            "⬇️ Rainfall trend detected: DECREASING"
        )

    else:

        st.info(
            "➡️ Rainfall trend detected: STABLE"
        )

    # --------------------------------------------------------
    # RAINFALL FORECAST GRAPH
    # --------------------------------------------------------

    st.subheader(
        "📈 Rainfall Forecast"
    )

    rain_fig = go.Figure()

    rain_fig.add_trace(
        go.Bar(
            x=forecast_df["datetime"],
            y=forecast_df["rainfall"],
            name="Forecast Rainfall"
        )
    )

    rain_fig.update_layout(
        template="plotly_dark",
        height=380,
        title="Automatic Rainfall Forecast",
        xaxis_title="Time",
        yaxis_title="Rainfall (mm / 3h)"
    )

    st.plotly_chart(
        rain_fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # WATER LEVEL PREDICTION
    # --------------------------------------------------------

    predicted_level = predict_water_level(
        dam,
        summary["rain_24h"]
    )

    probability = release_probability(
        dam,
        predicted_level
    )

    st.subheader(
        "🤖 HYDROSCOPE Prediction Engine"
    )

    prediction_cols = st.columns(3)

    prediction_cols[0].metric(
        "💧 Current Level",
        f"{dam['water_level']:.1f}"
    )

    prediction_cols[1].metric(
        "🔮 Predicted Level",
        f"{predicted_level:.1f}"
    )

    prediction_cols[2].metric(
        "🚪 Release Probability",
        f"{probability}%"
    )

    if probability >= 70:

        st.error(
            "🚨 HIGH RELEASE POSSIBILITY"
        )

    elif probability >= 45:

        st.warning(
            "⚠️ MODERATE RELEASE POSSIBILITY"
        )

    else:

        st.success(
            "🟢 LOW RELEASE POSSIBILITY"
        )

    # --------------------------------------------------------
    # PREDICTED WATER LEVEL GRAPH
    # --------------------------------------------------------

    st.subheader(
        "📊 Predicted Reservoir Level"
    )

    hours = np.arange(
        0,
        25,
        3
    )

    predicted_levels = np.linspace(
        dam["water_level"],
        predicted_level,
        len(hours)
    )

    level_fig = go.Figure()

    level_fig.add_trace(
        go.Scatter(
            x=hours,
            y=predicted_levels,
            mode="lines+markers",
            name="Predicted Water Level"
        )
    )

    level_fig.update_layout(
        template="plotly_dark",
        height=420,
        title=f"24-Hour Water-Level Prediction — {dam_name}",
        xaxis_title="Forecast Time (hours)",
        yaxis_title="Water Level"
    )

    st.plotly_chart(
        level_fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # MODEL EXPLANATION
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="card">
        <b>🤖 How HYDROSCOPE generated this prediction</b><br><br>

        🌧️ Automatic weather forecast<br>
        ↓<br>
        🌧️ Predicted rainfall accumulation<br>
        ↓<br>
        💧 Current reservoir level<br>
        ↓<br>
        ⬆️ Inflow + ⬇️ outflow<br>
        ↓<br>
        🤖 Water-level prediction<br>
        ↓<br>
        🚪 Release-risk assessment
        </div>
        """,
        unsafe_allow_html=True
    )

    st.warning(
        "⚠️ The current water-level calculation is a prototype "
        "model. It will later be replaced with a trained "
        "hydrological/ML model using historical reservoir, "
        "rainfall and inflow data."
    )

    st.caption(
        "Rainfall forecast provided by OpenWeather."
    )


# ============================================================
# FLOOD SIMULATION
# ============================================================

elif st.session_state.page == "Flood Simulation":

    st.header(
        "🌊 Dam-Break & Downstream Flood Simulation"
    )

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
        + dam["inflow"] * 0.25
    )

    arrival_time = max(
        10,
        120 - severity + breach_duration * 0.15
    )

    affected_population = int(
        5000 * (severity / 100)
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

    st.subheader(
        "🗺️ Downstream Impact Zones"
    )

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

    st.subheader(
        "📈 Flood Propagation"
    )

    times = np.arange(
        0,
        max(
            121,
            int(arrival_time + 100)
        ),
        5
    )

    flow = np.zeros(
        len(times)
    )

    for i, t in enumerate(times):

        if t >= arrival_time:

            elapsed = t - arrival_time

            flow[i] = (
                peak_flow
                * math.exp(
                    -elapsed / 40
                )
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
        "⚠️ Simplified prototype simulation. Production "
        "implementation requires DEM/topography, river "
        "networks and validated hydraulic modelling."
    )


# ============================================================
# EMERGENCY CENTER
# ============================================================

elif st.session_state.page == "Emergency Center":

    st.header(
        "🚨 Emergency Decision Center"
    )

    st.error(
        "🚨 EMERGENCY DECISION-SUPPORT MODE"
    )

    st.subheader(
        "⚠️ Immediate Response Checklist"
    )

    checklist = [
        "Verify reservoir and rainfall observations.",
        "Check current gate/shutter status.",
        "Assess downstream river level.",
        "Identify vulnerable settlements.",
        "Check roads and bridge accessibility.",
        "Coordinate with disaster-management authorities.",
        "Issue evacuation warnings through authorised channels.",
        "Continue monitoring water-level changes."
    ]

    for item in checklist:

        st.checkbox(
            item,
            key=f"emergency_{item}"
        )

    st.subheader(
        "📡 System Status"
    )

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

    st.subheader(
        "📢 Alert Classification"
    )

    alert_level = st.select_slider(
        "Current alert level",
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

        st.success(
            "🟢 NORMAL — Continue routine monitoring."
        )

    elif alert_level == "WATCH":

        st.info(
            "🔵 WATCH — Increase monitoring frequency."
        )

    elif alert_level == "ADVISORY":

        st.warning(
            "🟡 ADVISORY — Prepare response teams "
            "and verify downstream conditions."
        )

    elif alert_level == "WARNING":

        st.warning(
            "🟠 WARNING — Authorities should evaluate "
            "protective and evacuation actions."
        )

    else:

        st.error(
            "🔴 CRITICAL — Immediate coordination with "
            "authorised emergency authorities is required."
        )

    st.subheader(
        "🛡️ HYDROSCOPE Safety Principle"
    )

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
