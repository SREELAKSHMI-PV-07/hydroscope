import streamlit as st

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="HYDROSCOPE",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# SESSION STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


# =========================================================
# GLOBAL CSS
# =========================================================

st.markdown(
    """
    <style>

    /* ---------- MAIN BACKGROUND ---------- */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(14, 165, 233, 0.13),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 20%,
                rgba(56, 189, 248, 0.09),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #020817 0%,
                #061426 45%,
                #03101f 100%
            );

        color: #e6f7ff;
    }


    /* ---------- REMOVE SIDEBAR ---------- */

    [data-testid="stSidebar"] {
        display: none;
    }

    [data-testid="collapsedControl"] {
        display: none;
    }


    /* ---------- TOP HEADER ---------- */

    .hydro-header {
        position: relative;

        width: 100%;

        padding: 18px 26px 16px 26px;

        margin-bottom: 22px;

        border-radius: 0 0 24px 24px;

        background:
            linear-gradient(
                135deg,
                rgba(15, 39, 64, 0.78),
                rgba(5, 25, 45, 0.55)
            );

        border: 1px solid rgba(125, 211, 252, 0.16);

        backdrop-filter: blur(20px);

        box-shadow:
            0 15px 45px rgba(0, 0, 0, 0.28),
            inset 0 1px 0 rgba(255,255,255,0.07);

        overflow: hidden;
    }


    /* ---------- WATER GLOW ---------- */

    .water-glow {
        position: absolute;

        width: 260px;
        height: 260px;

        right: -80px;
        top: -150px;

        border-radius: 50%;

        background:
            radial-gradient(
                circle,
                rgba(56,189,248,0.22),
                transparent 65%
            );

        pointer-events: none;
    }


    /* ---------- BRAND ---------- */

    .brand {
        display: flex;
        align-items: center;
        gap: 13px;
    }

    .brand-icon {

        width: 48px;
        height: 48px;

        border-radius: 15px;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 26px;

        background:
            linear-gradient(
                145deg,
                rgba(56,189,248,0.30),
                rgba(14,116,144,0.18)
            );

        border: 1px solid rgba(125,211,252,0.28);

        box-shadow:
            0 0 25px rgba(56,189,248,0.15),
            inset 0 1px 0 rgba(255,255,255,0.12);
    }

    .brand-name {

        font-size: 26px;

        font-weight: 800;

        letter-spacing: 3px;

        color: #e8f8ff;

        line-height: 1;
    }

    .brand-name span {
        color: #38bdf8;
    }

    .brand-tagline {

        font-size: 11px;

        letter-spacing: 1.5px;

        color: #7dd3fc;

        margin-top: 5px;

        text-transform: uppercase;
    }


    /* ---------- GLASS CARDS ---------- */

    .glass-card {

        background:
            linear-gradient(
                135deg,
                rgba(17, 40, 64, 0.70),
                rgba(5, 25, 43, 0.48)
            );

        border:
            1px solid rgba(125, 211, 252, 0.14);

        border-radius: 20px;

        padding: 22px;

        backdrop-filter: blur(18px);

        box-shadow:
            0 12px 35px rgba(0,0,0,0.22),
            inset 0 1px 0 rgba(255,255,255,0.06);

        transition:
            transform 0.25s ease,
            border 0.25s ease,
            box-shadow 0.25s ease;
    }

    .glass-card:hover {

        transform: translateY(-4px);

        border:
            1px solid rgba(56,189,248,0.35);

        box-shadow:
            0 18px 45px rgba(0,0,0,0.32),
            0 0 25px rgba(56,189,248,0.08);
    }


    /* ---------- METRIC CARDS ---------- */

    .metric-card {

        background:
            linear-gradient(
                145deg,
                rgba(16,45,70,0.72),
                rgba(5,24,42,0.52)
            );

        border: 1px solid rgba(125,211,252,0.14);

        border-radius: 18px;

        padding: 20px;

        min-height: 125px;

        backdrop-filter: blur(16px);

        box-shadow:
            0 10px 30px rgba(0,0,0,0.20);

        transition: all 0.25s ease;
    }

    .metric-card:hover {

        transform: translateY(-5px);

        border-color:
            rgba(56,189,248,0.35);

        box-shadow:
            0 15px 35px rgba(0,0,0,0.28),
            0 0 22px rgba(56,189,248,0.08);
    }

    .metric-label {

        color: #8fb4ca;

        font-size: 12px;

        text-transform: uppercase;

        letter-spacing: 1px;
    }

    .metric-value {

        color: #e9faff;

        font-size: 32px;

        font-weight: 750;

        margin-top: 7px;
    }

    .metric-info {

        color: #38bdf8;

        font-size: 12px;

        margin-top: 5px;
    }


    /* ---------- SECTION TITLE ---------- */

    .section-title {

        color: #e8f8ff;

        font-size: 21px;

        font-weight: 700;

        margin-top: 12px;

        margin-bottom: 12px;
    }

    .section-subtitle {

        color: #7797aa;

        font-size: 13px;

        margin-top: -8px;

        margin-bottom: 18px;
    }


    /* ---------- WATER WAVE ---------- */

    .wave-container {

        position: relative;

        height: 75px;

        overflow: hidden;

        margin-top: 10px;

        border-radius: 0 0 20px 20px;
    }

    .wave {

        position: absolute;

        left: -10%;

        width: 120%;

        height: 70px;

        bottom: -35px;

        border-radius: 50%;

        background:
            linear-gradient(
                180deg,
                rgba(56,189,248,0.18),
                rgba(14,116,144,0.08)
            );

        animation: waveMove 7s ease-in-out infinite;
    }

    .wave.two {

        bottom: -43px;

        opacity: 0.45;

        animation:
            waveMove 9s ease-in-out infinite reverse;
    }

    @keyframes waveMove {

        0%, 100% {
            transform: translateX(-3%);
        }

        50% {
            transform: translateX(3%);
        }
    }


    /* ---------- STATUS DOT ---------- */

    .status-dot {

        display: inline-block;

        width: 9px;
        height: 9px;

        border-radius: 50%;

        margin-right: 7px;

        background: #22c55e;

        box-shadow:
            0 0 12px rgba(34,197,94,0.8);

        animation: pulse 2s infinite;
    }

    @keyframes pulse {

        0%,100% {
            box-shadow:
                0 0 5px rgba(34,197,94,0.4);
        }

        50% {
            box-shadow:
                0 0 16px rgba(34,197,94,0.9);
        }
    }


    /* ---------- STREAMLIT BUTTONS ---------- */

    .stButton > button {

        border-radius: 12px !important;

        border:
            1px solid rgba(125,211,252,0.15) !important;

        background:
            rgba(10,35,55,0.55) !important;

        color: #a9d9ed !important;

        font-weight: 600 !important;

        transition:
            all 0.25s ease !important;

        backdrop-filter: blur(10px);
    }

    .stButton > button:hover {

        border-color:
            rgba(56,189,248,0.50) !important;

        background:
            rgba(14,116,144,0.28) !important;

        color: #e6faff !important;

        transform: translateY(-2px);

        box-shadow:
            0 8px 25px rgba(56,189,248,0.12);
    }


    /* ---------- DIVIDER ---------- */

    hr {

        border-color:
            rgba(125,211,252,0.10) !important;
    }


    /* ---------- FOOTER ---------- */

    .footer {

        text-align: center;

        margin-top: 45px;

        padding: 20px;

        color: #53788e;

        font-size: 11px;

        letter-spacing: 1px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TOP HEADER
# =========================================================

st.markdown(
    """
    <div class="hydro-header">

        <div class="water-glow"></div>

        <div class="brand">

            <div class="brand-icon">
                🌊
            </div>

            <div>
                <div class="brand-name">
                    HYDRO<span>SCOPE</span>
                </div>

                <div class="brand-tagline">
                    Intelligent Water & Flood Risk Platform
                </div>
            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TOP NAVIGATION
# =========================================================

nav_items = [
    ("🏠", "Dashboard"),
    ("💧", "Dam Monitoring"),
    ("📈", "Prediction"),
    ("🌊", "Flood Simulation"),
    ("🚨", "Emergency")
]

cols = st.columns([1, 1, 1, 1, 1, 0.35])

for i, (icon, name) in enumerate(nav_items):

    with cols[i]:

        if st.button(
            f"{icon}  {name}",
            key=f"nav_{name}",
            use_container_width=True
        ):
            st.session_state.page = name
            st.rerun()


# =========================================================
# STATUS BAR
# =========================================================

st.markdown(
    """
    <div style="
        margin-top:10px;
        margin-bottom:20px;
        color:#7194a8;
        font-size:12px;
        letter-spacing:0.5px;
    ">

        <span class="status-dot"></span>

        HYDROSCOPE SYSTEM ONLINE

        <span style="margin-left:20px;">
            ● Prototype Data
        </span>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DASHBOARD
# =========================================================

if st.session_state.page == "Dashboard":

    st.markdown(
        """
        <div class="section-title">
            Good morning, Operator.
        </div>

        <div class="section-subtitle">
            Here's the current water intelligence overview.
        </div>
        """,
        unsafe_allow_html=True
    )


    # METRICS

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">
                    Dams Monitored
                </div>

                <div class="metric-value">
                    12
                </div>

                <div class="metric-info">
                    ↑ 2 connected today
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">
                    Normal
                </div>

                <div class="metric-value">
                    6
                </div>

                <div class="metric-info">
                    ● Stable
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">
                    Warning
                </div>

                <div class="metric-value">
                    4
                </div>

                <div class="metric-info">
                    ● Monitoring
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">
                    Critical
                </div>

                <div class="metric-value">
                    2
                </div>

                <div class="metric-info">
                    ⚠ Immediate attention
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    st.markdown("<br>", unsafe_allow_html=True)


    # MAIN DASHBOARD AREA

    left, right = st.columns([1.65, 1])


    with left:

        st.markdown(
            """
            <div class="glass-card">

                <div class="section-title">
                    🌍 Regional Water Intelligence
                </div>

                <div class="section-subtitle">
                    Live overview of monitored dams and their current risk state.
                </div>

                <div style="
                    height:390px;
                    border-radius:16px;

                    background:
                        radial-gradient(
                            circle at 50% 50%,
                            rgba(56,189,248,0.13),
                            transparent 45%
                        ),
                        linear-gradient(
                            135deg,
                            rgba(5,35,57,0.8),
                            rgba(2,17,30,0.9)
                        );

                    border:
                        1px solid rgba(125,211,252,0.10);

                    display:flex;
                    align-items:center;
                    justify-content:center;

                    color:#5e879d;

                    font-size:15px;

                    letter-spacing:1px;
                ">

                    🗺️ INTERACTIVE DAM MAP<br>
                    <span style="font-size:11px;">
                        Map module coming next
                    </span>

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with right:

        st.markdown(
            """
            <div class="glass-card">

                <div class="section-title">
                    💧 Priority Dam
                </div>

                <div style="
                    color:#38bdf8;
                    font-size:23px;
                    font-weight:700;
                ">
                    Idukki Dam
                </div>

                <div style="
                    color:#7896a7;
                    font-size:12px;
                    margin-top:4px;
                ">
                    Kerala • Prototype Monitoring
                </div>

                <br>

                <div style="
                    color:#8ba9b9;
                    font-size:12px;
                ">
                    CURRENT WATER LEVEL
                </div>

                <div style="
                    font-size:38px;
                    font-weight:800;
                    margin-top:4px;
                ">
                    88%
                </div>

                <div style="
                    height:9px;
                    border-radius:20px;
                    background:#102c42;
                    overflow:hidden;
                    margin-top:8px;
                ">

                    <div style="
                        width:88%;
                        height:100%;
                        border-radius:20px;

                        background:
                            linear-gradient(
                                90deg,
                                #0ea5e9,
                                #38bdf8
                            );

                        box-shadow:
                            0 0 15px rgba(56,189,248,0.4);
                    ">
                    </div>

                </div>

                <br>

                <div style="
                    display:flex;
                    justify-content:space-between;
                    color:#7896a7;
                    font-size:12px;
                ">

                    <span>Rainfall</span>
                    <strong style="color:#dff7ff;">
                        72 mm/hr
                    </strong>

                </div>

                <div style="
                    display:flex;
                    justify-content:space-between;
                    color:#7896a7;
                    font-size:12px;
                    margin-top:10px;
                ">

                    <span>Inflow</span>
                    <strong style="color:#dff7ff;">
                        1,800 m³/s
                    </strong>

                </div>

                <div style="
                    display:flex;
                    justify-content:space-between;
                    color:#7896a7;
                    font-size:12px;
                    margin-top:10px;
                ">

                    <span>Shutters</span>
                    <strong style="color:#fbbf24;">
                        2 / 8
                    </strong>

                </div>

                <br>

                <div style="
                    padding:10px;
                    border-radius:10px;

                    background:
                        rgba(245,158,11,0.08);

                    border:
                        1px solid rgba(245,158,11,0.18);

                    color:#fbbf24;

                    font-size:12px;
                ">

                    🟠 WARNING — Increased monitoring required

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # QUICK ACTIONS

    st.markdown(
        "<div class='section-title'>Quick Actions</div>",
        unsafe_allow_html=True
    )

    q1, q2, q3, q4 = st.columns(4)

    with q1:
        if st.button(
            "📍 Find Nearby Dams",
            use_container_width=True
        ):
            st.session_state.page = "Dam Monitoring"
            st.rerun()

    with q2:
        if st.button(
            "📈 View Prediction",
            use_container_width=True
        ):
            st.session_state.page = "Prediction"
            st.rerun()

    with q3:
        if st.button(
            "🌊 Run Simulation",
            use_container_width=True
        ):
            st.session_state.page = "Flood Simulation"
            st.rerun()

    with q4:
        if st.button(
            "🚨 Emergency Center",
            use_container_width=True
        ):
            st.session_state.page = "Emergency"
            st.rerun()


    # WATER EFFECT

    st.markdown(
        """
        <div class="wave-container">

            <div class="wave"></div>
            <div class="wave two"></div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# DAM MONITORING
# =========================================================

elif st.session_state.page == "Dam Monitoring":

    st.markdown(
        "<div class='section-title'>💧 Dam Monitoring</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='section-subtitle'>"
        "Real-time dam status and environmental conditions."
        "</div>",
        unsafe_allow_html=True
    )

    st.info(
        "The interactive dam map and live monitoring module will be added next."
    )


# =========================================================
# PREDICTION
# =========================================================

elif st.session_state.page == "Prediction":

    st.markdown(
        "<div class='section-title'>📈 Water & Shutter Prediction</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='section-subtitle'>"
        "Predict future water levels and controlled-release probability."
        "</div>",
        unsafe_allow_html=True
    )

    st.info(
        "Prediction engine will be connected after the monitoring data layer."
    )


# =========================================================
# FLOOD SIMULATION
# =========================================================

elif st.session_state.page == "Flood Simulation":

    st.markdown(
        "<div class='section-title'>🌊 Flood Simulation</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='section-subtitle'>"
        "Explore downstream flood propagation after a hypothetical dam failure."
        "</div>",
        unsafe_allow_html=True
    )

    st.info(
        "GIS-based dam-break simulation will be added here."
    )


# =========================================================
# EMERGENCY CENTER
# =========================================================

elif st.session_state.page == "Emergency":

    st.markdown(
        "<div class='section-title'>🚨 Emergency Center</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='section-subtitle'>"
        "Monitor critical conditions and downstream emergency risk."
        "</div>",
        unsafe_allow_html=True
    )

    st.warning(
        "Emergency intelligence and evacuation mapping will be connected here."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">

        HYDROSCOPE • Intelligent Water & Flood Risk Platform
        <br>
        Prototype Environment • SIH

    </div>
    """,
    unsafe_allow_html=True
)
