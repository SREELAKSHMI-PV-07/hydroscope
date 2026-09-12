import streamlit as st

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------

st.set_page_config(
    page_title="HYDROSCOPE",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -----------------------------
# CUSTOM CSS
# -----------------------------

st.markdown("""
<style>

    .stApp {
        background-color: #07111f;
        color: #e8f1f8;
    }

    [data-testid="stSidebar"] {
        background-color: #0b1728;
        border-right: 1px solid #1d344d;
    }

    .hydro-title {
        font-size: 42px;
        font-weight: 700;
        letter-spacing: 2px;
        color: #38bdf8;
        margin-bottom: 0;
    }

    .hydro-subtitle {
        font-size: 16px;
        color: #94a3b8;
        margin-top: 0;
    }

    .status-card {
        background: #0d1b2e;
        border: 1px solid #1d344d;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }

    .status-number {
        font-size: 30px;
        font-weight: 700;
        color: #38bdf8;
    }

    .status-label {
        color: #94a3b8;
        font-size: 14px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 600;
        color: #e8f1f8;
        margin-top: 20px;
    }

    .footer {
        text-align: center;
        color: #64748b;
        font-size: 12px;
        margin-top: 40px;
    }

</style>
""", unsafe_allow_html=True)


# -----------------------------
# SIDEBAR
# -----------------------------

with st.sidebar:

    st.markdown(
        "<div class='hydro-title'>🌊 HYDROSCOPE</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='hydro-subtitle'>Water Intelligence System</div>",
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### Navigation")

    page = st.radio(
        "Go to",
        [
            "🏠 Dashboard",
            "💧 Dam Monitoring",
            "📈 Prediction",
            "🌊 Flood Simulation",
            "🚨 Emergency Center"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.caption("HYDROSCOPE v0.1")
    st.caption("Prototype Environment")


# -----------------------------
# DASHBOARD
# -----------------------------

if page == "🏠 Dashboard":

    st.markdown(
        "<div class='hydro-title'>HYDROSCOPE</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='hydro-subtitle'>"
        "Intelligent Dam Monitoring & Flood Risk Prediction System"
        "</div>",
        unsafe_allow_html=True
    )

    st.divider()

    # STATUS CARDS

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
            <div class="status-card">
                <div class="status-number">12</div>
                <div class="status-label">Dams Monitored</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="status-card">
                <div class="status-number">2</div>
                <div class="status-label">Critical Dams</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="status-card">
                <div class="status-number">4</div>
                <div class="status-label">Warning Dams</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            """
            <div class="status-card">
                <div class="status-number">3</div>
                <div class="status-label">Active Alerts</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        "<div class='section-title'>System Overview</div>",
        unsafe_allow_html=True
    )

    st.info(
        "HYDROSCOPE monitoring system is online. "
        "The current environment uses prototype data."
    )

    st.markdown(
        "<div class='section-title'>What HYDROSCOPE does</div>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📍 Monitor")
        st.write(
            "Track dam locations, water levels, rainfall, "
            "inflow, outflow and spillway status."
        )

    with col2:
        st.markdown("### 📈 Predict")
        st.write(
            "Predict future water levels and estimate "
            "the probability of controlled water release."
        )

    with col3:
        st.markdown("### 🌊 Simulate")
        st.write(
            "Simulate dam-break scenarios and visualize "
            "potential downstream flood impacts."
        )


# -----------------------------
# OTHER PAGES — TEMPORARY
# -----------------------------

elif page == "💧 Dam Monitoring":

    st.title("💧 Dam Monitoring")

    st.info(
        "Dam monitoring module will be built next."
    )


elif page == "📈 Prediction":

    st.title("📈 Prediction")

    st.info(
        "Water-level and shutter prediction module "
        "will be built next."
    )


elif page == "🌊 Flood Simulation":

    st.title("🌊 Flood Simulation")

    st.info(
        "Dam-break and flood propagation simulation "
        "will be built here."
    )


elif page == "🚨 Emergency Center":

    st.title("🚨 Emergency Center")

    st.info(
        "Emergency alerts and evacuation intelligence "
        "will be built here."
    )


# -----------------------------
# FOOTER
# -----------------------------

st.markdown(
    "<div class='footer'>"
    "HYDROSCOPE • Intelligent Water & Flood Risk Platform"
    "</div>",
    unsafe_allow_html=True
)
