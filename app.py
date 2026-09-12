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
        radial-gradient(
            circle at 10% 10%,
            rgba(0, 150, 220, 0.14),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 20%,
            rgba(0, 100, 180, 0.12),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #03121e 0%,
            #061b2b 50%,
            #021019 100%
        );
    color: #f5f9ff;
}

.block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4 {
    color: #f5f9ff !important;
}

p, label {
    color: #e7f3fa !important;
}

/* HYDROSCOPE HEADER */

.hero-title {
    font-size: 42px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 2px;
}

.hero-subtitle {
    color: #9fc5dd;
    font-size: 15px;
    letter-spacing: 1px;
    margin-bottom: 18px;
}

/* NAVIGATION BUTTONS */

div.stButton > button {
    width: 100%;
    min-height: 46px;
    border-radius: 14px;
    border: 1px solid rgba(100, 190, 240, 0.28);
    background: rgba(10, 39, 58, 0.75);
    color: #dff5ff;
    font-weight: 700;
    transition: all 0.18s ease;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    border-color: rgba(100, 210, 255, 0.85);
    background: rgba(15, 75, 105, 0.9);
    box-shadow:
        0 0 18px rgba(0, 190, 255, 0.22),
        0 7px 20px rgba(0, 0, 0, 0.25);
}

div.stButton > button:active {
    transform: scale(0.97);
}

/* METRIC CARDS */

div[data-testid="stMetric"] {
    background: rgba(9, 39, 57, 0.72);
    border: 1px solid rgba(112, 203, 244, 0.20);
    border-radius: 17px;
    padding: 15px;
}

/* SELECT BOX */

div[data-baseweb="select"] > div {
    background: rgba(8, 37, 54, 0.90);
    border-color: rgba(100, 190, 230, 0.30);
}

/* FOOTER */

.footer {
    text-align: center;
    color: #7195aa;
    font-size: 12px;
    padding-top: 20px;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# DEMO DAM DATABASE
# ============================================================
#
# IMPORTANT:
# These reservoir values are prototype/demo values.
# They are NOT live operational dam-control values.
#
# Later these can be replaced by verified official data.
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
# MONITORING LOCATIONS
# ============================================================

LOCATIONS = {

    "Kochi": (
        9.9312,
        76.2673
    ),

    "Idukki": (
        9.8500,
        76.9700
    ),

    "Munnar": (
        10.0889,
        77.0595
    ),

    "Kothamangalam": (
        10.0580,
        76.6290
    ),

    "Thodupuzha": (
        9.8950,
        76.7180
    ),

    "Kottayam": (
        9.5916,
        76.5222
    ),

    "Pathanamthitta": (
        9.2648,
        76.7870
    ),

    "Alappuzha": (
        9.4981,
        76.3388
    ),

    "Thiruvananthapuram": (
        8.5241,
        76.9366
    ),

    "Wayanad": (
        11.6854,
        76.1320
    )
}


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


# ============================================================
# DISTANCE CALCULATION
# ============================================================

def distance_km(
    lat1,
    lon1,
    lat2,
    lon2
):

    earth_radius = 6371

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    delta_lat = math.radians(
        lat2 - lat1
    )

    delta_lon = math.radians(
        lon2 - lon1
    )

    a = (
        math.sin(delta_lat / 2) ** 2
        +
        math.cos(lat1_rad)
        *
        math.cos(lat2_rad)
        *
        math.sin(delta_lon / 2) ** 2
    )

    return (
        earth_radius
        * 2
        * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a)
        )
    )


# ============================================================
# NEARBY DAMS
# ============================================================

def nearby_dams(
    location_name,
    radius=120
):

    lat, lon = LOCATIONS[
        location_name
    ]

    results = []

    for name, dam in DAM_DATABASE.items():

        distance = distance_km(
            lat,
            lon,
            dam["lat"],
            dam["lon"]
        )

        if distance <= radius:

            result = dam.copy()

            result["name"] = name
            result["distance"] = distance

            results.append(result)

    return sorted(
        results,
        key=lambda x: x["distance"]
    )


# ============================================================
# OPENWEATHER CURRENT WEATHER
# ============================================================

@st.cache_data(ttl=600)
def get_current_weather(
    lat,
    lon
):

    try:

        api_key = st.secrets[
            "OPENWEATHER_API_KEY"
        ]

    except Exception:

        return {
            "success": False,
            "error":
                "OPENWEATHER_API_KEY is not configured."
        }

    url = (
        "https://api.openweathermap.org/"
        "data/2.5/weather"
    )

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
                "error":
                    "OpenWeather API key is not active yet."
            }

        if response.status_code == 429:

            return {
                "success": False,
                "error":
                    "OpenWeather API request limit reached."
            }

        response.raise_for_status()

        data = response.json()

        rainfall = 0.0

        if "rain" in data:

            rainfall = data[
                "rain"
            ].get(
                "1h",
                0.0
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

            "city":
                data.get(
                    "name",
                    "Unknown"
                )
        }

    except requests.exceptions.RequestException as error:

        return {
            "success": False,
            "error": str(error)
        }


# ============================================================
# OPENWEATHER FORECAST
# ============================================================

@st.cache_data(ttl=600)
def get_forecast(
    lat,
    lon
):

    try:

        api_key = st.secrets[
            "OPENWEATHER_API_KEY"
        ]

    except Exception:

        return {
            "success": False,
            "error":
                "OPENWEATHER_API_KEY is not configured."
        }

    url = (
        "https://api.openweathermap.org/"
        "data/2.5/forecast"
    )

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
                "error":
                    "OpenWeather API key is not active yet."
            }

        if response.status_code == 429:

            return {
                "success": False,
                "error":
                    "OpenWeather API request limit reached."
            }

        response.raise_for_status()

        data = response.json()

        rows = []

        for item in data.get(
            "list",
            []
        ):

            rainfall = 0.0

            if "rain" in item:

                rainfall = item[
                    "rain"
                ].get(
                    "3h",
                    0.0
                )

            rows.append({

                "datetime":
                    pd.to_datetime(
                        item["dt"],
                        unit="s"
                    ),

                "rainfall":
                    rainfall,

                "temperature":
                    item["main"]["temp"],

                "description":
                    item["weather"][0]["description"]
            })

        return {
            "success": True,
            "data": pd.DataFrame(rows)
        }

    except requests.exceptions.RequestException as error:

        return {
            "success": False,
            "error": str(error)
        }


# ============================================================
# RAINFALL ANALYSIS
# ============================================================

def analyse_rainfall(
    forecast_df
):

    if forecast_df.empty:

        return {
            "rain_6h": 0.0,
            "rain_12h": 0.0,
            "rain_24h": 0.0,
            "peak_3h": 0.0,
            "trend": "Unknown",
            "intensity": "Unknown"
        }

    start_time = forecast_df[
        "datetime"
    ].min()

    six_hours = (
        forecast_df[
            forecast_df["datetime"]
            <= start_time
            + pd.Timedelta(hours=6)
        ]["rainfall"]
        .sum()
    )

    twelve_hours = (
        forecast_df[
            forecast_df["datetime"]
            <= start_time
            + pd.Timedelta(hours=12)
        ]["rainfall"]
        .sum()
    )

    twenty_four_hours = (
        forecast_df[
            forecast_df["datetime"]
            <= start_time
            + pd.Timedelta(hours=24)
        ]["rainfall"]
        .sum()
    )

    peak_3h = forecast_df[
        "rainfall"
    ].max()

    first_half = forecast_df.head(
        max(
            1,
            len(forecast_df) // 3
        )
    )["rainfall"].mean()

    second_half = forecast_df.tail(
        max(
            1,
            len(forecast_df) // 3
        )
    )["rainfall"].mean()

    if second_half > first_half * 1.25:

        trend = "Increasing"

    elif second_half < first_half * 0.75:

        trend = "Decreasing"

    else:

        trend = "Stable"

    if peak_3h >= 20:

        intensity = "Very Heavy"

    elif peak_3h >= 10:

        intensity = "Heavy"

    elif peak_3h >= 2.5:

        intensity = "Moderate"

    elif peak_3h > 0:

        intensity = "Light"

    else:

        intensity = "No Significant Rain"

    return {

        "rain_6h":
            round(
                six_hours,
                1
            ),

        "rain_12h":
            round(
                twelve_hours,
                1
            ),

        "rain_24h":
            round(
                twenty_four_hours,
                1
            ),

        "peak_3h":
            round(
                peak_3h,
                1
            ),

        "trend":
            trend,

        "intensity":
            intensity
    }


# ============================================================
# WATER LEVEL PREDICTION
# ============================================================

def predict_water_level(
    dam,
    rainfall_24h
):

    current_level = dam[
        "water_level"
    ]

    net_flow = max(
        0,
        dam["inflow"]
        -
        dam["outflow"]
    )

    flow_component = (
        net_flow / 1000
    ) * 0.75

    rainfall_component = (
        rainfall_24h / 100
    ) * 2.5

    predicted_level = (
        current_level
        +
        flow_component
        +
        rainfall_component
    )

    return round(
        predicted_level,
        2
    )


# ============================================================
# RELEASE PROBABILITY
# ============================================================

def calculate_release_probability(
    dam,
    predicted_level
):

    level_score = min(
        100,
        predicted_level
    )

    inflow_score = min(
        100,
        dam["inflow"] / 20
    )

    current_score = min(
        100,
        dam["water_level"]
    )

    probability = (
        current_score * 0.35
        +
        level_score * 0.35
        +
        inflow_score * 0.30
    )

    return min(
        99,
        round(probability)
    )


# ============================================================
# AUTOMATIC FLOOD SCENARIO
# ============================================================

def generate_flood_scenario(
    dam
):

    water_level = dam[
        "water_level"
    ]

    inflow = dam[
        "inflow"
    ]

    outflow = dam[
        "outflow"
    ]

    net_flow = max(
        0,
        inflow - outflow
    )

    level_factor = min(
        water_level / 100,
        1.0
    )

    inflow_factor = min(
        inflow / 2000,
        1.0
    )

    scenario_score = (
        level_factor * 0.60
        +
        inflow_factor * 0.40
    )

    if scenario_score >= 0.80:

        scenario_class = "SEVERE"

        breach_fraction = 0.75

        development_time = 25

    elif scenario_score >= 0.60:

        scenario_class = "HIGH"

        breach_fraction = 0.55

        development_time = 40

    elif scenario_score >= 0.40:

        scenario_class = "MODERATE"

        breach_fraction = 0.35

        development_time = 60

    else:

        scenario_class = "LOW"

        breach_fraction = 0.20

        development_time = 90

    peak_flow = (
        outflow
        +
        inflow * breach_fraction
        +
        net_flow * 0.50
    )

    arrival_time = max(
        15,
        120 - breach_fraction * 70
    )

    population_factor = (
        0.30
        +
        scenario_score * 0.70
    )

    affected_population = int(
        5000
        *
        population_factor
    )

    return {

        "score":
            scenario_score,

        "class":
            scenario_class,

        "breach_fraction":
            breach_fraction,

        "development_time":
            development_time,

        "peak_flow":
            peak_flow,

        "arrival_time":
            arrival_time,

        "affected_population":
            affected_population
    }


# ============================================================
# MAP
# ============================================================

def create_dam_map(
    location_name
):

    lat, lon = LOCATIONS[
        location_name
    ]

    # ========================================================
    # OPENSTREETMAP
    # ========================================================
    #
    # This replaces CartoDB.
    # No map API key is required.
    #
    map_object = folium.Map(
        location=[
            lat,
            lon
        ],
        zoom_start=8,
        tiles="OpenStreetMap",
        control_scale=True
    )

    # ========================================================
    # 120 KM MONITORING RADIUS
    # ========================================================

    folium.Circle(
        location=[
            lat,
            lon
        ],
        radius=120000,
        color="#25b9ff",
        fill=True,
        fill_opacity=0.06,
        weight=2,
        tooltip=(
            "💧 HYDROSCOPE "
            "120 km Monitoring Zone"
        )
    ).add_to(
        map_object
    )

    # ========================================================
    # SELECTED MONITORING LOCATION
    # ========================================================

    folium.Marker(
        [
            lat,
            lon
        ],
        tooltip=f"📍 {location_name}",
        popup=folium.Popup(
            f"""
            <b>📍 HYDROSCOPE Monitoring Location</b><br><br>
            Location: {location_name}<br>
            Latitude: {lat:.4f}<br>
            Longitude: {lon:.4f}<br>
            Monitoring Radius: 120 km
            """,
            max_width=300
        ),
        icon=folium.Icon(
            color="blue",
            icon="info-sign"
        )
    ).add_to(
        map_object
    )

    # ========================================================
    # DAM MARKERS
    # ========================================================

    for name, dam in DAM_DATABASE.items():

        distance = distance_km(
            lat,
            lon,
            dam["lat"],
            dam["lon"]
        )

        if distance <= 120:

            if dam["risk"] == "High":

                marker_color = "red"

            elif dam["risk"] == "Moderate":

                marker_color = "orange"

            else:

                marker_color = "green"

            popup_text = f"""
            <div style="
                font-family: Arial;
                width: 240px;
            ">

                <h4>
                    💧 {name}
                </h4>

                <b>District:</b>
                {dam["district"]}<br><br>

                <b>Water Level:</b>
                {dam["water_level"]:.1f}<br>

                <b>Inflow:</b>
                {dam["inflow"]:.0f} m³/s<br>

                <b>Outflow:</b>
                {dam["outflow"]:.0f} m³/s<br>

                <b>Open Shutters:</b>
                {dam["open_shutters"]}/
                {dam["total_shutters"]}<br>

                <b>Risk:</b>
                {dam["risk"]}<br>

                <b>Distance:</b>
                {distance:.1f} km<br>

                <b>Data:</b>
                {dam["status"]}

            </div>
            """

            folium.Marker(
                [
                    dam["lat"],
                    dam["lon"]
                ],
                tooltip=f"💧 {name}",
                popup=folium.Popup(
                    popup_text,
                    max_width=300
                ),
                icon=folium.Icon(
                    color=marker_color,
                    icon="tint"
                )
            ).add_to(
                map_object
            )

            # Small risk circle around dam

            folium.Circle(
                location=[
                    dam["lat"],
                    dam["lon"]
                ],
                radius=3000,
                color=marker_color,
                fill=True,
                fill_opacity=0.12,
                weight=1
            ).add_to(
                map_object
            )

    # ========================================================
    # MAP LEGEND
    # ========================================================

    legend_html = """
    <div style="
        position: fixed;
        bottom: 30px;
        left: 30px;
        z-index: 9999;
        background: rgba(5,25,40,0.94);
        padding: 12px 16px;
        border-radius: 12px;
        color: white;
        font-family: Arial;
        font-size: 13px;
        border: 1px solid rgba(100,200,255,0.4);
    ">

        <b>💧 HYDROSCOPE Map</b>
        <br><br>

        <span style="color:#22c55e;">
            ●
        </span>
        Normal
        <br>

        <span style="color:#f59e0b;">
            ●
        </span>
        Moderate Risk
        <br>

        <span style="color:#ef4444;">
            ●
        </span>
        High Risk
        <br>

        <span style="color:#25b9ff;">
            ●
        </span>
        Monitoring Location

    </div>
    """

    map_object.get_root().html.add_child(
        folium.Element(
            legend_html
        )
    )

    return map_object


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="hero-title">'
    '💧 HYDROSCOPE'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hero-subtitle">'
    'INTELLIGENT DAM MONITORING • '
    'WATER PREDICTION • '
    'FLOOD SIMULATION • '
    'EMERGENCY DECISION SUPPORT'
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


navigation_columns = st.columns(
    len(pages)
)


for column, page_info in zip(
    navigation_columns,
    pages
):

    icon, page_name = page_info

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

    st.header(
        "📊 System Dashboard"
    )

    st.write(
        "Unified monitoring of reservoir conditions, "
        "weather and nearby dams."
    )

    location = st.selectbox(
        "📍 Select Monitoring Location",
        list(LOCATIONS.keys())
    )

    lat, lon = LOCATIONS[
        location
    ]

    nearby = nearby_dams(
        location
    )

    st.info(
        f"📍 Monitoring: {location}  •  "
        f"Coordinates: {lat:.4f}, {lon:.4f}  •  "
        f"Radius: 120 km"
    )

    # ========================================================
    # WEATHER
    # ========================================================

    st.subheader(
        "🌦️ Live Weather"
    )

    weather = get_current_weather(
        lat,
        lon
    )

    if weather["success"]:

        weather_columns = st.columns(
            5
        )

        weather_columns[0].metric(
            "🌡️ Temperature",
            f"{weather['temperature']:.1f} °C"
        )

        weather_columns[1].metric(
            "🌧️ Rainfall",
            f"{weather['rainfall']:.1f} mm"
        )

        weather_columns[2].metric(
            "💧 Humidity",
            f"{weather['humidity']}%"
        )

        weather_columns[3].metric(
            "💨 Wind",
            f"{weather['wind']:.1f} m/s"
        )

        weather_columns[4].metric(
            "🔵 Pressure",
            f"{weather['pressure']} hPa"
        )

        st.caption(
            f"Condition: "
            f"{weather['description'].title()}  •  "
            "Weather data provided by OpenWeather"
        )

    else:

        st.warning(
            f"🌦️ Weather unavailable: "
            f"{weather['error']}"
        )

    # ========================================================
    # NEARBY DAMS
    # ========================================================

    st.subheader(
        "🏗️ Nearby Dams"
    )

    if nearby:

        dam_columns = st.columns(
            3
        )

        for index, dam in enumerate(
            nearby
        ):

            with dam_columns[
                index % 3
            ]:

                st.metric(
                    f"🏗️ {dam['name']}",
                    f"{dam['water_level']:.1f}",
                    f"{dam['distance']:.1f} km away"
                )

                st.caption(
                    f"Inflow: "
                    f"{dam['inflow']:.0f} m³/s  •  "
                    f"Outflow: "
                    f"{dam['outflow']:.0f} m³/s"
                )

                st.caption(
                    f"Risk: {dam['risk']}  •  "
                    f"Data: {dam['status']}"
                )

    # ========================================================
    # MAP
    # ========================================================

    st.subheader(
        "🗺️ Dam Monitoring Map"
    )

    st_folium(
        create_dam_map(
            location
        ),
        width=None,
        height=500,
        returned_objects=[]
    )

    # ========================================================
    # LEVEL COMPARISON
    # ========================================================

    st.subheader(
        "📈 Reservoir Level Comparison"
    )

    if nearby:

        chart_df = pd.DataFrame({

            "Dam": [
                dam["name"]
                for dam in nearby
            ],

            "Water Level": [
                dam["water_level"]
                for dam in nearby
            ]
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
            template="plotly_dark",
            height=400,
            title="Current Reservoir Levels",
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

    st.header(
        "🏗️ Dam Monitoring"
    )

    dam_name = st.selectbox(
        "🏗️ Select Dam",
        list(DAM_DATABASE.keys())
    )

    dam = DAM_DATABASE[
        dam_name
    ]

    st.warning(
        "⚠️ Reservoir level, inflow, outflow and shutter "
        "values are currently prototype data. They are "
        "not live operational control values."
    )

    monitoring_columns = st.columns(
        4
    )

    monitoring_columns[0].metric(
        "💧 Water Level",
        f"{dam['water_level']:.1f}"
    )

    monitoring_columns[1].metric(
        "⬆️ Inflow",
        f"{dam['inflow']:.0f} m³/s"
    )

    monitoring_columns[2].metric(
        "⬇️ Outflow",
        f"{dam['outflow']:.0f} m³/s"
    )

    monitoring_columns[3].metric(
        "🌧️ Rainfall",
        f"{dam['rainfall']:.0f} mm"
    )

    # ========================================================
    # SHUTTERS
    # ========================================================

    st.subheader(
        "🚪 Shutter Status"
    )

    shutter_columns = st.columns(
        dam["total_shutters"]
    )

    for i in range(
        dam["total_shutters"]
    ):

        with shutter_columns[i]:

            if i < dam["open_shutters"]:

                st.success(
                    f"OPEN\n\n"
                    f"{dam['opening_percent']}%"
                )

            else:

                st.info(
                    "CLOSED"
                )

    # ========================================================
    # TREND
    # ========================================================

    st.subheader(
        "📈 Water-Level Trend"
    )

    hours = np.arange(
        -12,
        1
    )

    levels = np.linspace(
        dam["water_level"] - 3,
        dam["water_level"],
        len(hours)
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
        height=400,
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

    st.header(
        "🌧️ Water-Level Prediction"
    )

    st.write(
        "HYDROSCOPE automatically analyses current weather "
        "and forecast rainfall before estimating future "
        "reservoir behaviour."
    )

    dam_name = st.selectbox(
        "🏗️ Select Dam",
        list(DAM_DATABASE.keys())
    )

    dam = DAM_DATABASE[
        dam_name
    ]

    # ========================================================
    # AUTOMATIC FORECAST
    # ========================================================

    forecast = get_forecast(
        dam["lat"],
        dam["lon"]
    )

    if not forecast["success"]:

        st.error(
            f"Unable to obtain automatic rainfall forecast: "
            f"{forecast['error']}"
        )

        st.stop()

    forecast_df = forecast[
        "data"
    ]

    rainfall = analyse_rainfall(
        forecast_df
    )

    # ========================================================
    # AUTOMATIC RAINFALL PREDICTION
    # ========================================================

    st.subheader(
        "🤖 System-Predicted Rainfall"
    )

    rainfall_columns = st.columns(
        4
    )

    rainfall_columns[0].metric(
        "Next 6 Hours",
        f"{rainfall['rain_6h']} mm"
    )

    rainfall_columns[1].metric(
        "Next 12 Hours",
        f"{rainfall['rain_12h']} mm"
    )

    rainfall_columns[2].metric(
        "Next 24 Hours",
        f"{rainfall['rain_24h']} mm"
    )

    rainfall_columns[3].metric(
        "Peak 3-Hour Rain",
        f"{rainfall['peak_3h']} mm"
    )

    st.info(
        f"🌧️ Predicted rainfall intensity: "
        f"**{rainfall['intensity']}**  •  "
        f"Trend: **{rainfall['trend']}**"
    )

    # ========================================================
    # RAINFALL FORECAST GRAPH
    # ========================================================

    st.subheader(
        "📈 Automatic Rainfall Forecast"
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
        xaxis_title="Forecast Time",
        yaxis_title="Rainfall (mm / 3h)"
    )

    st.plotly_chart(
        rain_fig,
        use_container_width=True
    )

    # ========================================================
    # WATER LEVEL PREDICTION
    # ========================================================

    predicted_level = predict_water_level(
        dam,
        rainfall["rain_24h"]
    )

    release_probability = (
        calculate_release_probability(
            dam,
            predicted_level
        )
    )

    st.subheader(
        "🔮 System Water-Level Prediction"
    )

    prediction_columns = st.columns(
        3
    )

    prediction_columns[0].metric(
        "💧 Current Level",
        f"{dam['water_level']:.1f}"
    )

    prediction_columns[1].metric(
        "🔮 Predicted Level",
        f"{predicted_level:.1f}"
    )

    prediction_columns[2].metric(
        "🚪 Release Probability",
        f"{release_probability}%"
    )

    if release_probability >= 70:

        st.error(
            "🚨 HIGH RELEASE POSSIBILITY"
        )

    elif release_probability >= 45:

        st.warning(
            "⚠️ MODERATE RELEASE POSSIBILITY"
        )

    else:

        st.success(
            "🟢 LOW RELEASE POSSIBILITY"
        )

    # ========================================================
    # 24-HOUR WATER LEVEL FORECAST
    # ========================================================

    st.subheader(
        "📊 24-Hour Reservoir Prediction"
    )

    prediction_hours = np.arange(
        0,
        25,
        3
    )

    predicted_levels = np.linspace(
        dam["water_level"],
        predicted_level,
        len(prediction_hours)
    )

    level_fig = go.Figure()

    level_fig.add_trace(
        go.Scatter(
            x=prediction_hours,
            y=predicted_levels,
            mode="lines+markers",
            name="Predicted Level"
        )
    )

    level_fig.update_layout(
        template="plotly_dark",
        height=420,
        title=(
            f"24-Hour Prediction — "
            f"{dam_name}"
        ),
        xaxis_title="Forecast Time (hours)",
        yaxis_title="Water Level"
    )

    st.plotly_chart(
        level_fig,
        use_container_width=True
    )

    # ========================================================
    # DECISION PIPELINE
    # ========================================================

    st.subheader(
        "🧠 HYDROSCOPE Decision Pipeline"
    )

    st.write(
        "🌦️ Weather forecast"
    )

    st.write("↓")

    st.write(
        "🌧️ Automatic rainfall prediction"
    )

    st.write("↓")

    st.write(
        "💧 Current reservoir condition"
    )

    st.write("↓")

    st.write(
        "⬆️ Inflow + ⬇️ Outflow"
    )

    st.write("↓")

    st.write(
        "🤖 Water-level prediction"
    )

    st.write("↓")

    st.write(
        "🚪 Release-risk assessment"
    )

    st.warning(
        "⚠️ The current water-level model is a prototype "
        "calculation. The production version should use "
        "historical reservoir, rainfall and inflow data "
        "with a validated hydrological/ML model."
    )

    st.caption(
        "🌧️ Forecast data provided by OpenWeather."
    )


# ============================================================
# FLOOD SIMULATION
# ============================================================

elif st.session_state.page == "Flood Simulation":

    st.header(
        "🌊 Dam-Break & Downstream Flood Simulation"
    )

    st.write(
        "HYDROSCOPE automatically generates a hypothetical "
        "failure scenario from reservoir conditions and "
        "estimates downstream flood propagation."
    )

    # ========================================================
    # ONLY DAM SELECTION
    # ========================================================

    dam_name = st.selectbox(
        "🏗️ Select Dam",
        list(DAM_DATABASE.keys())
    )

    dam = DAM_DATABASE[
        dam_name
    ]

    # ========================================================
    # AUTOMATIC SCENARIO
    # ========================================================

    scenario = generate_flood_scenario(
        dam
    )

    st.subheader(
        "🤖 Automatically Generated Scenario"
    )

    st.info(
        "No breach severity or breach duration is entered "
        "manually. HYDROSCOPE generates a hypothetical "
        "scenario from the reservoir conditions."
    )

    scenario_columns = st.columns(
        4
    )

    scenario_columns[0].metric(
        "🤖 Scenario",
        scenario["class"]
    )

    scenario_columns[1].metric(
        "💧 Reservoir Level",
        f"{dam['water_level']:.1f}"
    )

    scenario_columns[2].metric(
        "🌊 Estimated Peak Flow",
        f"{scenario['peak_flow']:.0f} m³/s"
    )

    scenario_columns[3].metric(
        "⏱️ First Arrival",
        f"{scenario['arrival_time']:.0f} min"
    )

    # ========================================================
    # AUTOMATIC PARAMETERS
    # ========================================================

    st.subheader(
        "🔎 System-Generated Parameters"
    )

    parameter_columns = st.columns(
        4
    )

    parameter_columns[0].metric(
        "⚠️ Scenario Class",
        scenario["class"]
    )

    parameter_columns[1].metric(
        "🌊 Breach Fraction",
        f"{scenario['breach_fraction'] * 100:.0f}%"
    )

    parameter_columns[2].metric(
        "⏱️ Development Time",
        f"{scenario['development_time']} min"
    )

    parameter_columns[3].metric(
        "👥 Potentially Affected",
        f"{scenario['affected_population']:,}"
    )

    # ========================================================
    # RISK
    # ========================================================

    st.subheader(
        "🚨 Downstream Risk Assessment"
    )

    if scenario["class"] == "SEVERE":

        st.error(
            "🔴 CRITICAL — Severe hypothetical "
            "failure scenario."
        )

    elif scenario["class"] == "HIGH":

        st.warning(
            "🟠 HIGH — Significant hypothetical "
            "flood wave may propagate downstream."
        )

    elif scenario["class"] == "MODERATE":

        st.warning(
            "🟡 MODERATE — Downstream areas require "
            "continued monitoring."
        )

    else:

        st.success(
            "🟢 LOW — Lower-intensity hypothetical "
            "failure scenario."
        )

    # ========================================================
    # DOWNSTREAM ZONES
    # ========================================================

    st.subheader(
        "🗺️ Estimated Downstream Impact"
    )

    arrival = scenario[
        "arrival_time"
    ]

    zones = pd.DataFrame({

        "Zone": [

            "Immediate Downstream",

            "Near Downstream",

            "Extended Downstream",

            "Low-Lying Areas"
        ],

        "Estimated Arrival": [

            f"{arrival:.0f} min",

            f"{arrival + 20:.0f} min",

            f"{arrival + 45:.0f} min",

            f"{arrival + 70:.0f} min"
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

    # ========================================================
    # FLOOD WAVE
    # ========================================================

    st.subheader(
        "📈 Estimated Flood-Wave Propagation"
    )

    times = np.arange(
        0,
        int(
            arrival + 120
        ),
        5
    )

    flow = np.zeros(
        len(times)
    )

    for index, time in enumerate(
        times
    ):

        if time >= arrival:

            elapsed = (
                time - arrival
            )

            flow[index] = (
                scenario["peak_flow"]
                *
                math.exp(
                    -elapsed / 40
                )
            )

    flood_fig = go.Figure()

    flood_fig.add_trace(
        go.Scatter(
            x=times,
            y=flow,
            mode="lines",
            fill="tozeroy",
            name="Estimated Flood Wave"
        )
    )

    flood_fig.update_layout(
        template="plotly_dark",
        height=430,
        title=(
            f"Estimated Flood Wave — "
            f"{dam_name}"
        ),
        xaxis_title="Time After Failure (minutes)",
        yaxis_title="Discharge (m³/s)"
    )

    st.plotly_chart(
        flood_fig,
        use_container_width=True
    )

    # ========================================================
    # PRODUCTION PIPELINE
    # ========================================================

    st.subheader(
        "🧠 Production Flood-Modelling Pipeline"
    )

    st.write(
        "💧 Reservoir storage and water level"
    )

    st.write("↓")

    st.write(
        "🏗️ Dam geometry and engineering parameters"
    )

    st.write("↓")

    st.write(
        "🌊 Breach hydraulics"
    )

    st.write("↓")

    st.write(
        "🗺️ DEM / terrain elevation"
    )

    st.write("↓")

    st.write(
        "🌊 River-network routing"
    )

    st.write("↓")

    st.write(
        "🏘️ Villages + roads + bridges"
    )

    st.write("↓")

    st.write(
        "🚨 Flood depth + arrival time + risk"
    )

    st.warning(
        "⚠️ This is a simplified prototype simulation. "
        "It does NOT predict actual dam failure. A production "
        "version requires validated dam-engineering data, "
        "terrain/elevation data and hydraulic modelling."
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
        "⚠️ Response Checklist"
    )

    checklist = [

        "Verify reservoir and rainfall observations.",

        "Check current gate/shutter status.",

        "Assess downstream river conditions.",

        "Identify vulnerable settlements.",

        "Check roads and bridges.",

        "Coordinate with disaster-management authorities.",

        "Prepare authorised warning and evacuation procedures.",

        "Continue monitoring reservoir conditions."
    ]

    for index, item in enumerate(
        checklist
    ):

        st.checkbox(
            item,
            key=f"checklist_{index}"
        )

    # ========================================================
    # SYSTEM STATUS
    # ========================================================

    st.subheader(
        "📡 System Status"
    )

    status_columns = st.columns(
        4
    )

    status_columns[0].success(
        "🟢 Weather Service"
    )

    status_columns[1].warning(
        "🟡 Dam Data"
    )

    status_columns[2].success(
        "🟢 Prediction Engine"
    )

    status_columns[3].success(
        "🟢 Flood Model"
    )

    # ========================================================
    # ALERT CLASSIFICATION
    # ========================================================

    st.subheader(
        "📢 Alert Classification"
    )

    alert_level = st.selectbox(
        "System alert level",
        [
            "NORMAL",
            "WATCH",
            "ADVISORY",
            "WARNING",
            "CRITICAL"
        ]
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

    # ========================================================
    # SAFETY
    # ========================================================

    st.subheader(
        "🛡️ HYDROSCOPE Safety Principle"
    )

    st.write(
        "HYDROSCOPE is a decision-support system."
    )

    st.write(
        "It does not autonomously operate dam gates "
        "or issue official evacuation orders."
    )

    st.write(
        "Final operational decisions remain with "
        "authorised dam-management and disaster-management "
        "authorities."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    '<div class="footer">'
    '💧 HYDROSCOPE • '
    'Intelligent Dam & Flood Decision Support System'
    '<br>'
    'Smart India Hackathon Prototype • Kerala'
    '</div>',
    unsafe_allow_html=True
)
