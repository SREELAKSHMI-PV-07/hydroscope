import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import math

# ============================================================
# HYDROSCOPE
# Dam Intelligence • Flood Prediction • Safety
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

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 20% 10%, rgba(0, 150, 220, 0.08), transparent 30%),
        radial-gradient(circle at 80% 80%, rgba(0, 90, 180, 0.08), transparent 30%),
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

/* Main container */

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1450px !important;
}

/* ============================================================
   HEADER
   ============================================================ */

.hydro-header {
    text-align: center;
    padding: 12px 0 20px 0;
}

.hydro-title {
    font-size: 43px;
    font-weight: 800;
    letter-spacing: 7px;
    color: #f1fbff;
    margin-bottom: 4px;
}

.hydro-subtitle {
    font-size: 12px;
    letter-spacing: 4px;
    color: #67dfff;
    font-weight: 500;
}

/* ============================================================
   NAVIGATION
   ============================================================ */

.nav-wrapper {
    padding: 6px;
    margin: 0 auto 25px auto;
    border-radius: 18px;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(130,220,255,0.10);
    backdrop-filter: blur(20px);
    box-shadow: 0 10px 35px rgba(0,0,0,0.20);
}

/* ============================================================
   GLASS CARDS
   ============================================================ */

.glass-card {
    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,0.065),
            rgba(255,255,255,0.025)
        );
    border: 1px solid rgba(170,230,255,0.10);
    border-radius: 22px;
    padding: 24px;
    margin-bottom: 18px;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    box-shadow:
        0 15px 40px rgba(0,0,0,0.20),
        inset 0 1px 0 rgba(255,255,255,0.035);
    transition: all 0.25s ease;
}

.glass-card:hover {
    border-color: rgba(90,210,255,0.22);
    box-shadow:
        0 18px 45px rgba(0,0,0,0.25),
        0 0 30px rgba(40,180,240,0.045);
}

/* ============================================================
   TITLES
   ============================================================ */

.section-title {
    font-size: 21px;
    font-weight: 700;
    color: #eefaff;
    margin-bottom: 4px;
}

.section-description {
    font-size: 13px;
    color: #849aaa;
    margin-bottom: 18px;
}

/* ============================================================
   METRICS
   ============================================================ */

.metric-card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 20px;
    min-height: 130px;
    transition: all 0.25s ease;
}

.metric-card:hover {
    transform: translateY(-3px);
    border-color: rgba(80,210,255,0.25);
    background: rgba(80,210,255,0.045);
}

.metric-label {
    color: #8295a5;
    font-size: 12px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}

.metric-value {
    color: #effbff;
    font-size: 31px;
    font-weight: 700;
    margin-top: 7px;
}

.metric-unit {
    color: #6f8798;
    font-size: 12px;
}

.metric-status {
    font-size: 12px;
    margin-top: 7px;
}

/* ============================================================
   STATUS
   ============================================================ */

.status-normal {
    color: #53e0a3;
}

.status-warning {
    color: #ffc857;
}

.status-danger {
    color: #ff6b6b;
}

.status-critical {
    color: #ff3f5f;
}

/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {
    width: 100%;
    border-radius: 13px !important;
    border: 1px solid rgba(100,220,255,0.16) !important;
    background: rgba(255,255,255,0.045) !important;
    color: #eafaff !important;
    font-weight: 600 !important;
    transition: all 0.20s ease !important;
    min-height: 42px;
}

.stButton > button:hover {
    border-color: rgba(80,215,255,0.55) !important;
    background: rgba(50,190,240,0.10) !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(30,180,240,0.12);
}

.stButton > button:active {
    transform: scale(0.97);
}

/* ============================================================
   INPUTS
   ============================================================ */

.stSelectbox > div > div,
.stTextInput > div > div,
.stNumberInput > div > div {
    background: rgba(255,255,255,0.035) !important;
    border-color: rgba(255,255,255,0.10) !important;
    color: white !important;
    border-radius: 12px !important;
}

/* ============================================================
   ALERTS
   ============================================================ */

.alert-card {
    border-radius: 18px;
    padding: 18px 20px;
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
    background: rgba(255,80,80,0.06);
    border: 1px solid rgba(255,80,80,0.20);
}

/* ============================================================
   WATER LEVEL
   ============================================================ */

.water-container {
    position: relative;
    height: 220px;
    border-radius: 20px;
    overflow: hidden;
    background: linear-gradient(
        to bottom,
        rgba(255,255,255,0.025),
        rgba(20,120,170,0.10)
    );
    border: 1px solid rgba(100,220,255,0.12);
}

.water-fill {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    background:
        linear-gradient(
            180deg,
            rgba(55,210,245,0.48),
            rgba(15,100,170,0.38)
        );
    transition: height 1s ease;
}

.water-wave {
    position: absolute;
    top: -12px;
    left: -10%;
    width: 120%;
    height: 30px;
    border-radius: 50%;
    background: rgba(100,225,255,0.25);
}

/* ============================================================
   SHUTTERS
   ============================================================ */

.shutter {
    display: inline-block;
    width: 35px;
    height: 105px;
    margin: 5px;
    border-radius: 7px;
    background:
        linear-gradient(
            90deg,
            #182631,
            #405565,
            #17242e
        );
    border: 1px solid rgba(200,230,240,0.15);
    box-shadow: inset 0 0 12px rgba(0,0,0,0.5);
}

.shutter.open {
    background:
        linear-gradient(
            180deg,
            #54e2ff,
            #176d9c
        );
    box-shadow:
        0 0 15px rgba(50,210,255,0.22);
}

/* ============================================================
   RIPPLE
   ============================================================ */

.hydro-ripple {
    position: fixed;
    width: 12px;
    height: 12px;
    border: 2px solid rgba(80,220,255,0.65);
    border-radius: 50%;
    pointer-events: none;
    transform: translate(-50%, -50%);
    animation: hydroRipple 0.9s ease-out forwards;
    z-index: 999999;
}

.hydro-ripple::after {
    content: "";
    position: absolute;
    inset: -10px;
    border: 1px solid rgba(80,220,255,0.25);
    border-radius: 50%;
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

/* ============================================================
   FOOTER
   ============================================================ */

.hydro-footer {
    text-align: center;
    padding: 35px 0 10px 0;
    color: #526575;
    font-size: 11px;
    letter-spacing: 1px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# WATER RIPPLE EFFECT
# ============================================================

st.markdown("""
<script>

document.addEventListener("pointerdown", function(event) {

    const ripple = document.createElement("div");

    ripple.className = "hydro-ripple";

    ripple.style.left = event.clientX + "px";
    ripple.style.top = event.clientY + "px";

    document.body.appendChild(ripple);

    setTimeout(function() {
        ripple.remove();
    }, 1000);

});

</script>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hydro-header">

    <div class="hydro-title">
        💧 HYDROSCOPE
    </div>

    <div class="hydro-subtitle">
        DAM INTELLIGENCE • FLOOD PREDICTION • SAFETY
    </div>

</div>
""", unsafe_allow_html=True)


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

for col, (icon, name) in zip(nav_cols, nav_items):

    with col:

        if st.button(
            f"{icon}  {name}",
            key=f"nav_{name}"
        ):
            st.session_state.page = name
            st.rerun()


st.markdown("---")


# ============================================================
# DEMO DAM DATABASE
# ============================================================

dams = pd.DataFrame([
    {
        "name": "Idukki Dam",
        "district": "Idukki",
        "lat": 9.8494,
        "lon": 76.9726,
        "capacity": 2403,
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
        "capacity": 1088,
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
        "capacity": 37,
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
        "capacity": 24,
        "level": 61,
        "inflow": 160,
        "outflow": 80,
        "rainfall": 36,
        "shutters": 5,
        "open_shutters": 1,
        "opening": 10,
        "risk": "Normal"
    }
])


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def metric_card(label, value, unit="", status="", status_class="status-normal"):
    return f"""
    <div class="metric-card">

        <div class="metric-label">
            {label}
        </div>

        <div class="metric-value">
            {value}
            <span class="metric-unit">{unit}</span>
        </div>

        <div class="metric-status {status_class}">
            {status}
        </div>

    </div>
    """


def risk_class(risk):

    if risk == "Critical":
        return "status-critical"

    if risk == "High":
        return "status-danger"

    if risk == "Moderate":
        return "status-warning"

    return "status-normal"


def create_water_chart():

    hours = pd.date_range(
        datetime.now() - timedelta(hours=12),
        periods=13,
        freq="h"
    )

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

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=hours,
            y=levels,
            mode="lines+markers",
            line=dict(width=3),
            fill="tozeroy",
            fillcolor="rgba(50,190,240,0.08)",
            marker=dict(size=6),
            name="Water Level"
        )
    )

    fig.add_hline(
        y=90,
        line_dash="dash",
        annotation_text="Alert Threshold"
    )

    fig.add_hline(
        y=95,
        line_dash="dash",
        annotation_text="Critical Threshold"
    )

    fig.update_layout(
        height=330,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#b8cad5"),
        xaxis=dict(
            showgrid=False
        ),
        yaxis=dict(
            title="Storage Level (%)",
            gridcolor="rgba(255,255,255,0.06)"
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)"
        )
    )

    return fig


# ============================================================
# DASHBOARD
# ============================================================

def dashboard():

    st.markdown("""
    <div class="section-title">
        System Overview
    </div>

    <div class="section-description">
        Real-time dam intelligence and downstream flood-risk overview.
    </div>
    """, unsafe_allow_html=True)

    total_dams = len(dams)

    moderate = len(dams[dams["risk"] == "Moderate"])

    avg_level = dams["level"].mean()

    total_inflow = dams["inflow"].sum()

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
                "● Within monitored range",
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
                "● Live monitoring",
                "status-normal"
            ),
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            metric_card(
                "Attention Required",
                moderate,
                "",
                "● Requires monitoring",
                "status-warning"
            ),
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([1.6, 1])

    with left:

        st.markdown("""
        <div class="glass-card">

        <div class="section-title">
            💧 Water-Level Trend
        </div>

        <div class="section-description">
            Idukki demonstration dataset
        </div>

        """, unsafe_allow_html=True)

        st.plotly_chart(
            create_water_chart(),
            use_container_width=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with right:

        st.markdown("""
        <div class="glass-card">

        <div class="section-title">
            ⚠️ System Status
        </div>

        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="alert-card alert-normal">
            <b>🟢 Monitoring System</b><br>
            <span style="color:#849aaa;">
            All connected monitoring modules operational.
            </span>
        </div>

        <div class="alert-card alert-warning">
            <b>🟡 Idukki Dam</b><br>
            <span style="color:#849aaa;">
            Storage approaching monitoring threshold.
            </span>
        </div>

        <div class="alert-card alert-normal">
            <b>🟢 Rainfall Network</b><br>
            <span style="color:#849aaa;">
            Rainfall data available for monitored locations.
            </span>
        </div>

        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">

        <div class="section-title">
            🗺️ Monitored Dams
        </div>

        <div class="section-description">
            Current prototype monitoring status
        </div>

    """, unsafe_allow_html=True)

    display_df = dams[
        [
            "name",
            "district",
            "level",
            "inflow",
            "outflow",
            "rainfall",
            "open_shutters",
            "risk"
        ]
    ].copy()

    display_df.columns = [
        "Dam",
        "District",
        "Water Level %",
        "Inflow m³/s",
        "Outflow m³/s",
        "Rainfall mm/hr",
        "Open Shutters",
        "Risk"
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# DAM MONITORING
# ============================================================

def dam_monitoring():

    st.markdown("""
    <div class="section-title">
        💧 Dam Monitoring
    </div>

    <div class="section-description">
        Monitor water level, rainfall, inflow, outflow and shutter status.
    </div>
    """, unsafe_allow_html=True)

    selected = st.selectbox(
        "Select Dam",
        dams["name"].tolist()
    )

    dam = dams[dams["name"] == selected].iloc[0]

    left, right = st.columns([1.2, 1])

    with left:

        st.markdown("""
        <div class="glass-card">

        <div class="section-title">
            📍 Dam Location
        </div>

        """, unsafe_allow_html=True)

        m = folium.Map(
            location=[
                dam["lat"],
                dam["lon"]
            ],
            zoom_start=10,
            tiles="CartoDB dark_matter"
        )

        for _, row in dams.iterrows():

            color = "red" if row["risk"] == "Critical" else (
                "orange" if row["risk"] == "Moderate" else "green"
            )

            folium.Marker(
                location=[
                    row["lat"],
                    row["lon"]
                ],
                popup=row["name"],
                tooltip=row["name"],
                icon=folium.Icon(
                    color=color,
                    icon="tint",
                    prefix="fa"
                )
            ).add_to(m)

        st_folium(
            m,
            width=None,
            height=440
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with right:

        st.markdown("""
        <div class="glass-card">

        <div class="section-title">
            📊 Current Condition
        </div>

        """, unsafe_allow_html=True)

        a, b = st.columns(2)

        with a:
            st.markdown(
                metric_card(
                    "Water Level",
                    dam["level"],
                    "%",
                    "Current storage",
                    "status-warning" if dam["level"] >= 85 else "status-normal"
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
                    "status-warning" if dam["rainfall"] >= 60 else "status-normal"
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

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card">

        <div class="section-title">
            🚪 Shutter Configuration
        </div>

        <div class="section-description">
            Current gate configuration
        </div>

        """, unsafe_allow_html=True)

        shutters_html = ""

        for i in range(int(dam["shutters"])):

            if i < int(dam["open_shutters"]):
                shutters_html += '<div class="shutter open"></div>'
            else:
                shutters_html += '<div class="shutter"></div>'

        st.markdown(
            f"""
            <div style="text-align:center;">
                {shutters_html}
            </div>

            <div style="
                text-align:center;
                margin-top:12px;
                color:#849aaa;
                font-size:13px;
            ">
                {int(dam["open_shutters"])} of {int(dam["shutters"])}
                shutters open • {dam["opening"]}% opening
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">

        <div class="section-title">
            📈 Water-Level History
        </div>

    """, unsafe_allow_html=True)

    st.plotly_chart(
        create_water_chart(),
        use_container_width=True
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# PREDICTION
# ============================================================

def prediction():

    st.markdown("""
    <div class="section-title">
        📈 Prediction Center
    </div>

    <div class="section-description">
        Estimate future water levels and controlled-release probability.
    </div>
    """, unsafe_allow_html=True)

    selected = st.selectbox(
        "Prediction Dam",
        dams["name"].tolist()
    )

    dam = dams[dams["name"] == selected].iloc[0]

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

        release_probability = min(
            95,
            max(
                10,
                int(
                    dam["level"] * 0.65 +
                    dam["rainfall"] * 0.25
                )
            )
        )

        st.markdown(
            metric_card(
                "Release Probability",
                release_probability,
                "%",
                "Decision-support estimate",
                "status-warning"
            ),
            unsafe_allow_html=True
        )

    with c3:

        predicted = min(
            99,
            dam["level"] +
            int(dam["rainfall"] / 20)
        )

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

        st.markdown("""
        <div class="glass-card">

        <div class="section-title">
            🔮 Water-Level Forecast
        </div>

        """, unsafe_allow_html=True)

        future_hours = list(range(0, 13))

        forecast = []

        for h in future_hours:

            value = (
                dam["level"]
                + h * 0.35
                + math.sin(h / 2) * 0.35
            )

            forecast.append(min(100, value))

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=future_hours,
                y=forecast,
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

        st.markdown("</div>", unsafe_allow_html=True)

    with right:

        st.markdown("""
        <div class="glass-card">

        <div class="section-title">
            🧠 Decision Support
        </div>

        <div class="section-description">
            Prototype analytical output
        </div>

        """, unsafe_allow_html=True)

        if release_probability >= 75:

            st.markdown("""
            <div class="alert-card alert-warning">

            <b>🟡 Elevated Release Probability</b>

            <br><br>

            Current water level and rainfall conditions
            indicate increased probability of a controlled
            release.

            </div>
            """, unsafe_allow_html=True)

        else:

            st.markdown("""
            <div class="alert-card alert-normal">

            <b>🟢 Normal Release Probability</b>

            <br><br>

            Current conditions do not indicate a high
            release probability.

            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="
            margin-top:15px;
            padding:15px;
            border-radius:14px;
            background:rgba(255,255,255,0.025);
            color:#7f94a3;
            font-size:12px;
        ">
        ⚠️ Prototype decision-support output.
        It must not be interpreted as an autonomous
        dam-operation command.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# FLOOD SIMULATION
# ============================================================

def flood_simulation():

    st.markdown("""
    <div class="section-title">
        🌊 Flood Simulation
    </div>

    <div class="section-description">
        Simulate downstream flood propagation and identify potentially
        affected areas.
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1, 1.5])

    with left:

        st.markdown("""
        <div class="glass-card">

        <div class="section-title">
            ⚙️ Simulation Parameters
        </div>

        """, unsafe_allow_html=True)

        selected = st.selectbox(
            "Source Dam",
            dams["name"].tolist()
        )

        dam = dams[dams["name"] == selected].iloc[0]

        breach_size = st.slider(
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
            "Simulation Duration (hours)",
            1,
            24,
            12
        )

        simulate = st.button(
            "🌊 RUN FLOOD SIMULATION"
        )

        st.markdown("""
        <div style="
            margin-top:15px;
            font-size:11px;
            color:#627584;
        ">
        Simulation uses a simplified prototype flood model.
        Results are for demonstration and decision-support only.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with right:

        st.markdown("""
        <div class="glass-card">

        <div class="section-title">
            📊 Simulated Impact
        </div>

        """, unsafe_allow_html=True)

        if simulate:

            peak_flow = (
                dam["outflow"]
                * (1 + breach_size / 100)
                * rainfall_factor
            )

            arrival_time = max(
                0.5,
                6 - breach_size / 20
            )

            affected_population = int(
                15000 *
                (breach_size / 100) *
                rainfall_factor
            )

            risk = (
                "Critical"
                if breach_size >= 75
                else "High"
                if breach_size >= 50
                else "Moderate"
            )

            st.markdown(
                metric_card(
                    "Peak Simulated Flow",
                    f"{peak_flow:,.0f}",
                    "m³/s",
                    "Model output",
                    "status-danger" if peak_flow > 1000 else "status-warning"
                ),
                unsafe_allow_html=True
            )

            st.markdown("<br>", unsafe_allow_html=True)

            a, b = st.columns(2)

            with a:

                st.markdown(
                    metric_card(
                        "Estimated Arrival",
                        f"{arrival_time:.1f}",
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
                        f"{affected_population:,}",
                        "people",
                        "Prototype estimate",
                        "status-danger"
                    ),
                    unsafe_allow_html=True
                )

            st.markdown("<br>", unsafe_allow_html=True)

            risk_cls = risk_class(risk)

            st.markdown(
                f"""
                <div class="alert-card alert-danger">

                    <b>⚠️ Simulated Risk: {risk}</b>

                    <br><br>

                    The simulated scenario indicates potentially
                    significant downstream impact.

                    <br><br>

                    <span class="{risk_cls}">
                    Further hydraulic and GIS analysis required.
                    </span>

                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown("""
            <div style="
                padding:60px 20px;
                text-align:center;
                color:#657b8b;
            ">

            🌊

            <br><br>

            Configure the scenario and run the simulation.

            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    if simulate:

        st.markdown("""
        <div class="glass-card">

        <div class="section-title">
            🗺️ Downstream Impact Zone
        </div>

        """, unsafe_allow_html=True)

        m = folium.Map(
            location=[
                dam["lat"] - 0.05,
                dam["lon"] + 0.01
            ],
            zoom_start=10,
            tiles="CartoDB dark_matter"
        )

        folium.Marker(
            location=[
                dam["lat"],
                dam["lon"]
            ],
            popup=f"{selected} — Source Dam",
            tooltip="Source Dam",
            icon=folium.Icon(
                color="red",
                icon="tint",
                prefix="fa"
            )
        ).add_to(m)

        # Prototype downstream impact circles

        for radius, opacity in [
            (3000, 0.08),
            (6000, 0.06),
            (10000, 0.04)
        ]:

            folium.Circle(
                location=[
                    dam["lat"] - 0.035,
                    dam["lon"] + 0.015
                ],
                radius=radius,
                color="#44dfff",
                fill=True,
                fill_opacity=opacity
            ).add_to(m)

        st_folium(
            m,
            width=None,
            height=500
        )

        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# EMERGENCY CENTER
# ============================================================

def emergency_center():

    st.markdown("""
    <div class="section-title">
        🚨 Emergency Center
    </div>

    <div class="section-description">
        Emergency intelligence, alerts and evacuation-support information.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="alert-card alert-warning">

        <b>🟡 DEMONSTRATION ALERT</b>

        <br><br>

        Idukki demonstration scenario is currently being
        monitored due to elevated water-level conditions.

    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown("""
        <div class="glass-card">

        <div class="section-title">
            📢 Active Alerts
        </div>

        <br>

        <div style="
            font-size:38px;
            font-weight:700;
        ">
        1
        </div>

        <div style="color:#849aaa;">
        monitoring alert
        </div>

        </div>
        """, unsafe_allow_html=True)

    with c2:

        st.markdown("""
        <div class="glass-card">

        <div class="section-title">
            🏘️ Impact Zones
        </div>

        <br>

        <div style="
            font-size:38px;
            font-weight:700;
        ">
        3
        </div>

        <div style="color:#849aaa;">
        prototype zones
        </div>

        </div>
        """, unsafe_allow_html=True)

    with c3:

        st.markdown("""
        <div class="glass-card">

        <div class="section-title">
            🛣️ Critical Infrastructure
        </div>

        <br>

        <div style="
            font-size:38px;
            font-weight:700;
        ">
        7
        </div>

        <div style="color:#849aaa;">
        prototype assets
        </div>

        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">

        <div class="section-title">
            🆘 Emergency Response
        </div>

        <div class="section-description">
            Prototype emergency-response controls
        </div>

    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:

        if st.button("📢 Issue Warning Alert"):
            st.warning(
                "Prototype warning alert generated."
            )

        if st.button("📍 View Evacuation Zones"):
            st.info(
                "Evacuation-zone visualization will be connected "
                "to the GIS flood model."
            )

    with c2:

        if st.button("🏘️ View Affected Settlements"):
            st.info(
                "Settlement-impact analysis will be connected "
                "to downstream GIS data."
            )

        if st.button("🚑 Emergency Response Mode"):
            st.error(
                "Emergency response mode activated — prototype."
            )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">

        <div class="section-title">
            📋 Emergency Checklist
        </div>

        <br>

        <div style="
            line-height:2;
            color:#a9bbc7;
        ">

        ✓ Verify dam water level<br>
        ✓ Verify rainfall intensity<br>
        ✓ Verify inflow and outflow<br>
        ✓ Assess shutter configuration<br>
        ✓ Run downstream flood scenario<br>
        ✓ Identify affected settlements<br>
        ✓ Identify critical infrastructure<br>
        ✓ Issue appropriate warning<br>
        ✓ Coordinate evacuation response

        </div>

    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PAGE ROUTER
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

st.markdown("""
<div class="hydro-footer">

    HYDROSCOPE • SMART INDIA HACKATHON PROTOTYPE

    <br><br>

    Monitor → Predict → Simulate → Assess Impact → Alert

    <br>

    Prototype data and model outputs are for demonstration purposes.

</div>
""", unsafe_allow_html=True)
