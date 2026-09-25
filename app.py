import math
import secrets
import time
from datetime import datetime

import folium
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(page_title="HYDROSCOPE", page_icon="💧", layout="wide", initial_sidebar_state="collapsed")

# ============================================================
# STYLE — water-flowing glass interface
# ============================================================
st.markdown(r"""
<style>
.stApp{background:radial-gradient(circle at 20% 10%,rgba(0,180,255,.16),transparent 28%),radial-gradient(circle at 85% 20%,rgba(0,110,255,.12),transparent 30%),linear-gradient(135deg,#02111c,#06243a 48%,#011019);color:#eefaff;overflow-x:hidden}
.stApp:before{content:"";position:fixed;inset:auto -10% -18% -10%;height:42vh;background:radial-gradient(ellipse at 50% 100%,rgba(0,170,255,.18),transparent 60%);animation:water 9s ease-in-out infinite alternate;pointer-events:none;z-index:0}
@keyframes water{from{transform:translateX(-2%) scaleX(1)}to{transform:translateX(2%) scaleX(1.08)}}
.block-container{max-width:1450px;padding-top:1.4rem;padding-bottom:3rem;position:relative;z-index:1}
.hero{padding:20px 24px;border:1px solid rgba(130,220,255,.18);border-radius:24px;background:linear-gradient(135deg,rgba(7,43,65,.78),rgba(4,25,42,.62));box-shadow:0 18px 60px rgba(0,0,0,.24);overflow:hidden;position:relative}
.hero:after{content:"";position:absolute;left:-10%;right:-10%;bottom:-28px;height:70px;background:radial-gradient(ellipse,rgba(35,195,255,.22),transparent 68%);animation:wave 5s ease-in-out infinite alternate}
@keyframes wave{from{transform:translateX(-4%)}to{transform:translateX(4%)}}
.hero-title{font-size:44px;font-weight:850;letter-spacing:3px}.hero-sub{color:#9bcce2;font-size:14px;letter-spacing:1.4px}
div.stButton>button{width:100%;min-height:44px;border-radius:15px;border:1px solid rgba(100,210,255,.25);background:rgba(7,42,61,.72);color:#e5f9ff;font-weight:750;transition:.2s}
div.stButton>button:hover{transform:translateY(-2px);border-color:rgba(100,225,255,.85);box-shadow:0 0 24px rgba(0,190,255,.22)}
div[data-testid="stMetric"]{background:rgba(7,39,57,.72);border:1px solid rgba(120,210,245,.18);border-radius:18px;padding:14px}
.glass{background:rgba(7,38,57,.66);border:1px solid rgba(120,215,245,.18);border-radius:20px;padding:20px;box-shadow:0 12px 38px rgba(0,0,0,.20)}
.water-card{background:linear-gradient(180deg,rgba(8,43,63,.72),rgba(3,28,44,.78));border:1px solid rgba(80,205,255,.22);border-radius:20px;padding:18px;position:relative;overflow:hidden}
.water-card:before{content:"";position:absolute;left:-20%;right:-20%;bottom:-38px;height:95px;background:radial-gradient(ellipse,rgba(0,190,255,.24),transparent 65%);animation:wave 4s ease-in-out infinite alternate}
.badge{display:inline-block;padding:5px 10px;border-radius:999px;background:rgba(30,190,255,.12);border:1px solid rgba(80,210,255,.22);font-size:12px;color:#bdeeff}
.ripple{border:1px solid rgba(75,215,255,.28);border-radius:50%;height:80px;width:80px;animation:ripple 2.2s infinite;margin:auto;box-shadow:0 0 0 12px rgba(40,190,255,.04),0 0 0 25px rgba(40,190,255,.025)}
@keyframes ripple{0%{transform:scale(.75);opacity:.25}50%{transform:scale(1);opacity:.9}100%{transform:scale(1.25);opacity:.1}}
.footer{text-align:center;color:#7096aa;font-size:12px;padding-top:24px}
</style>
""", unsafe_allow_html=True)

# ============================================================
# DEMO DAM DATA — replace with authorized feeds in deployment
# ============================================================
DAM_DATABASE={
"Idukki Dam":{"district":"Idukki","lat":9.8494,"lon":76.9726,"water_level":88.0,"inflow":1800.0,"outflow":600.0,"rainfall":72.0,"total_shutters":8,"open_shutters":2,"opening_percent":20,"risk":"Moderate","status":"PROTOTYPE"},
"Idamalayar Dam":{"district":"Ernakulam","lat":10.2068,"lon":76.7032,"water_level":72.0,"inflow":920.0,"outflow":310.0,"rainfall":48.0,"total_shutters":4,"open_shutters":1,"opening_percent":15,"risk":"Normal","status":"PROTOTYPE"},
"Malankara Dam":{"district":"Idukki","lat":9.7804,"lon":76.8787,"water_level":67.0,"inflow":210.0,"outflow":95.0,"rainfall":41.0,"total_shutters":6,"open_shutters":1,"opening_percent":10,"risk":"Normal","status":"PROTOTYPE"},
"Bhoothathankettu":{"district":"Ernakulam","lat":10.1457,"lon":76.6788,"water_level":61.0,"inflow":160.0,"outflow":80.0,"rainfall":36.0,"total_shutters":5,"open_shutters":1,"opening_percent":10,"risk":"Normal","status":"PROTOTYPE"},
"Pamba Dam":{"district":"Pathanamthitta","lat":9.3805,"lon":76.9275,"water_level":64.0,"inflow":450.0,"outflow":170.0,"rainfall":39.0,"total_shutters":6,"open_shutters":1,"opening_percent":12,"risk":"Normal","status":"PROTOTYPE"},
"Kakki Dam":{"district":"Pathanamthitta","lat":9.35,"lon":77.0,"water_level":70.0,"inflow":520.0,"outflow":190.0,"rainfall":44.0,"total_shutters":4,"open_shutters":1,"opening_percent":15,"risk":"Normal","status":"PROTOTYPE"},
"Neyyar Dam":{"district":"Thiruvananthapuram","lat":8.535,"lon":77.145,"water_level":58.0,"inflow":190.0,"outflow":75.0,"rainfall":31.0,"total_shutters":4,"open_shutters":0,"opening_percent":0,"risk":"Normal","status":"PROTOTYPE"},
"Banasura Sagar Dam":{"district":"Wayanad","lat":11.7,"lon":75.95,"water_level":63.0,"inflow":330.0,"outflow":120.0,"rainfall":52.0,"total_shutters":4,"open_shutters":1,"opening_percent":10,"risk":"Normal","status":"PROTOTYPE"}}
LOCATIONS={"Kochi":(9.9312,76.2673),"Idukki":(9.85,76.97),"Munnar":(10.0889,77.0595),"Kothamangalam":(10.058,76.629),"Thodupuzha":(9.895,76.718),"Kottayam":(9.5916,76.5222),"Pathanamthitta":(9.2648,76.787),"Alappuzha":(9.4981,76.3388),"Thiruvananthapuram":(8.5241,76.9366),"Wayanad":(11.6854,76.132)}

# ============================================================
# HELPERS
# ============================================================
def distance_km(lat1,lon1,lat2,lon2):
    R=6371.0; p1=math.radians(lat1); p2=math.radians(lat2); dp=math.radians(lat2-lat1); dl=math.radians(lon2-lon1)
    a=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.atan2(math.sqrt(a),math.sqrt(1-a))

def nearby_dams(location,radius=120):
    lat,lon=LOCATIONS[location]; out=[]
    for name,d in DAM_DATABASE.items():
        dist=distance_km(lat,lon,d["lat"],d["lon"])
        if dist<=radius:
            x=d.copy(); x["name"]=name; x["distance"]=dist; out.append(x)
    return sorted(out,key=lambda x:x["distance"])

@st.cache_data(ttl=600)
def weather(lat,lon):
    try:key=st.secrets["OPENWEATHER_API_KEY"]
    except Exception:return {"success":False,"error":"OPENWEATHER_API_KEY is not configured."}
    try:
        r=requests.get("https://api.openweathermap.org/data/2.5/weather",params={"lat":lat,"lon":lon,"appid":key,"units":"metric"},timeout=10)
        if r.status_code==401:return {"success":False,"error":"OpenWeather API key is not active yet."}
        r.raise_for_status(); d=r.json(); rain=d.get("rain",{}).get("1h",0.0)
        return {"success":True,"temperature":d["main"]["temp"],"humidity":d["main"]["humidity"],"pressure":d["main"]["pressure"],"wind":d.get("wind",{}).get("speed",0),"rainfall":rain,"description":d["weather"][0]["description"],"city":d.get("name","Unknown")}
    except Exception as e:return {"success":False,"error":str(e)}

@st.cache_data(ttl=600)
def forecast(lat,lon):
    try:key=st.secrets["OPENWEATHER_API_KEY"]
    except Exception:return {"success":False,"error":"OPENWEATHER_API_KEY is not configured."}
    try:
        r=requests.get("https://api.openweathermap.org/data/2.5/forecast",params={"lat":lat,"lon":lon,"appid":key,"units":"metric"},timeout=10)
        if r.status_code==401:return {"success":False,"error":"OpenWeather API key is not active yet."}
        r.raise_for_status(); rows=[]
        for x in r.json().get("list",[]):
            rows.append({"datetime":pd.to_datetime(x["dt"],unit="s"),"rainfall":x.get("rain",{}).get("3h",0.0),"temperature":x["main"]["temp"]})
        return {"success":True,"data":pd.DataFrame(rows)}
    except Exception as e:return {"success":False,"error":str(e)}

def rainfall_summary(df):
    if df.empty:return {"rain_6h":0,"rain_12h":0,"rain_24h":0,"peak_3h":0,"trend":"Unknown"}
    t=df["datetime"].min(); vals=lambda h:df[df.datetime<=t+pd.Timedelta(hours=h)]["rainfall"].sum()
    a=df.head(max(1,len(df)//3))["rainfall"].mean(); b=df.tail(max(1,len(df)//3))["rainfall"].mean()
    trend="Increasing" if b>a*1.25 else "Decreasing" if b<a*.75 else "Stable"
    return {"rain_6h":round(vals(6),1),"rain_12h":round(vals(12),1),"rain_24h":round(vals(24),1),"peak_3h":round(df.rainfall.max(),1),"trend":trend}

def predict_level(d,rain24):
    net=max(0,d["inflow"]-d["outflow"])
    return round(d["water_level"]+(net/1000)*.75+(rain24/100)*2.5,2)

def release_probability(d,pred):
    score=d["water_level"]*.35+min(100,pred)*.35+min(100,d["inflow"]/20)*.30
    return min(99,round(score))

# ============================================================
# HYDRAULIC MODEL — prototype 2-D shallow-water solver
# ============================================================
def saint_venant_2d(dam, breach_fraction=0.55, nx=70, ny=42, steps=90):
    """Educational prototype of the 2-D shallow-water equations.
    Solves a simplified explicit finite-difference mass/momentum system.
    Not suitable for operational decisions without calibrated DEM, roughness,
    boundary conditions, dam geometry and numerical validation.
    """
    dx=120.0; dy=120.0; dt=0.15; g=9.81; n=0.035
    x=np.arange(nx)*dx; y=np.arange(ny)*dy
    X,Y=np.meshgrid(x,y)
    bed=0.002*X+0.0008*(Y-(ny*dy)/2)**2/(ny*dy)+0.6*np.sin(X/900)*np.sin(Y/700)
    bed-=bed.min()
    h=np.zeros((ny,nx),float)
    reservoir=max(2.0,dam["water_level"]*.055)
    h[:, :max(3,int(nx*.12))]=reservoir
    breach_col=max(2,int(nx*.10)); h[:,breach_col:breach_col+2]*=(1-breach_fraction)
    u=np.zeros_like(h); v=np.zeros_like(h)
    peak=0.; depth_peak=np.zeros_like(h); arrival=np.full_like(h,np.nan)
    for k in range(steps):
        eta=h+bed
        dhdx=np.gradient(eta,dx,axis=1); dhdy=np.gradient(eta,dy,axis=0)
        dudx=np.gradient(u,dx,axis=1); dudy=np.gradient(u,dy,axis=0)
        dvdx=np.gradient(v,dx,axis=1); dvdy=np.gradient(v,dy,axis=0)
        speed=np.sqrt(u*u+v*v)+1e-6
        sf_x=g*n*n*u*speed/np.maximum(h,0.05)**(4/3)
        sf_y=g*n*n*v*speed/np.maximum(h,0.05)**(4/3)
        u_new=u+dt*(-g*dhdx-u*dudx-v*dudy-sf_x)
        v_new=v+dt*(-g*dhdy-u*dvdx-v*dvdy-sf_y)
        div=np.gradient(h*u,dx,axis=1)+np.gradient(h*v,dy,axis=0)
        h_new=np.maximum(0,h-dt*div)
        # controlled numerical diffusion for prototype stability
        h_new=(h_new+np.roll(h_new,1,0)+np.roll(h_new,-1,0)+np.roll(h_new,1,1)+np.roll(h_new,-1,1))/5
        h_new[0,:]=0; h_new[-1,:]=0; h_new[:,-1]=0
        wet=(h_new>0.08)&np.isnan(arrival)
        arrival[wet]=k*dt/60.0
        h,u,v=h_new,u_new,v_new
        peak=max(peak,float(np.max(h*np.sqrt(g*np.maximum(h,0)))))
        depth_peak=np.maximum(depth_peak,h)
    return {"X":X,"Y":Y,"depth":depth_peak,"arrival":arrival,"peak_velocity":float(np.nanmax(np.sqrt(u*u+v*v))),"peak_discharge":peak*1000}

def public_release_impact(d):
    # Public view intentionally uses a release-impact corridor, not failure simulation.
    score=min(1,(d["open_shutters"]/max(1,d["total_shutters"]))*0.6+d["opening_percent"]/100*.4)
    zones=[("Immediate downstream", "Monitor" if score<.45 else "Attention"),("Near downstream","Monitor" if score<.65 else "Attention"),("Low-lying areas","Watch" if score<.8 else "Attention")]
    return zones

def dam_map(location, public=True):
    lat,lon=LOCATIONS[location]
    m=folium.Map(location=[lat,lon],zoom_start=8,tiles="OpenStreetMap",control_scale=True)
    folium.Circle([lat,lon],radius=120000,color="#25b9ff",fill=True,fill_opacity=.05).add_to(m)
    folium.Marker([lat,lon],tooltip=f"📍 {location}",icon=folium.Icon(color="blue",icon="info-sign")).add_to(m)
    for name,d in DAM_DATABASE.items():
        dist=distance_km(lat,lon,d["lat"],d["lon"])
        if dist>120:continue
        c="red" if d["risk"]=="High" else "orange" if d["risk"]=="Moderate" else "green"
        txt=f"<b>💧 {name}</b><br>Water level: {d['water_level']:.1f}<br>Shutters: {d['open_shutters']}/{d['total_shutters']}<br>Risk: {d['risk']}<br>Distance: {dist:.1f} km"
        folium.Marker([d["lat"],d["lon"]],tooltip=name,popup=folium.Popup(txt,max_width=260),icon=folium.Icon(color=c,icon="tint")).add_to(m)
    return m

# ============================================================
# AUTHORITY ACCESS — prototype verification
# ============================================================
def authority_login():
    st.subheader("🔐 Authority Verification")
    st.caption("Prototype access control: Authority ID + verified Gmail + OTP. For deployment, replace this with institutional SSO/OAuth and agency-managed accounts.")
    if "otp" not in st.session_state:
        st.session_state.otp=None
    aid=st.text_input("Authority ID",placeholder="AUTH-001")
    email=st.text_input("Authority Gmail",placeholder="authority@gmail.com")
    if st.button("Send Verification Code",key="send_otp"):
        allowed=st.secrets.get("AUTHORIZED_AUTHORITY_EMAILS","")
        allowed_list=[x.strip().lower() for x in str(allowed).split(",") if x.strip()]
        if not aid.strip() or not email.lower().endswith("@gmail.com"):
            st.error("Enter a valid Authority ID and Gmail address.")
        elif allowed_list and email.lower() not in allowed_list:
            st.error("This email is not on the authorized prototype list.")
        else:
            st.session_state.otp=st.secrets.get("AUTHORITY_DEMO_OTP","246810")
            st.session_state.otp_email=email.lower()
            st.info("Prototype verification code generated. In deployment this code must be delivered through the approved email/identity service.")
            st.code(st.session_state.otp)
    code=st.text_input("Verification code",type="password")
    if st.button("Verify & Enter Authority Console",key="verify_authority"):
        if st.session_state.get("otp") and code==str(st.session_state.otp):
            st.session_state.authority=True; st.session_state.authority_id=aid; st.session_state.authority_email=email.lower(); st.rerun()
        else:st.error("Invalid or missing verification code.")

# ============================================================
# SESSION / HEADER
# ============================================================
if "page" not in st.session_state: st.session_state.page="Home"
if "authority" not in st.session_state: st.session_state.authority=False

st.markdown('<div class="hero"><div class="hero-title">💧 HYDROSCOPE</div><div class="hero-sub">PUBLIC FLOOD AWARENESS • DAM MONITORING • PREDICTIVE WATER INTELLIGENCE</div></div>',unsafe_allow_html=True)

nav=[("🏠","Home"),("💧","Public Dashboard"),("🌧️","Prediction"),("🔐","Authority Access")]
if st.session_state.authority: nav += [("🛰️","Authority Console"),("🌊","Hydraulic Simulation")]
cols=st.columns(len(nav))
for c,(icon,name) in zip(cols,nav):
    with c:
        if st.button(f"{icon} {name}",key="nav_"+name):st.session_state.page=name;st.rerun()

st.divider()

# ============================================================
# HOME
# ============================================================
if st.session_state.page=="Home":
    st.markdown('<div class="glass">',unsafe_allow_html=True)
    st.title("🌊 Understand the water before it becomes a disaster.")
    st.write("HYDROSCOPE connects weather, reservoir conditions and downstream impact into one public safety platform.")
    a,b,c=st.columns(3)
    with a:
        st.markdown('<div class="ripple"></div>',unsafe_allow_html=True); st.markdown("### 👥 Public Interface"); st.write("See dam status, rainfall, shutter information and potential downstream release-impact areas.")
    with b:
        st.markdown('<div class="ripple"></div>',unsafe_allow_html=True); st.markdown("### 🔐 Authority Interface"); st.write("Verified users can access technical hydraulic scenarios, flood depth, velocity and arrival-time analysis.")
    with c:
        st.markdown('<div class="ripple"></div>',unsafe_allow_html=True); st.markdown("### 📡 Data Pipeline"); st.write("OpenWeather is live in the prototype. Dam values are currently simulated and marked as prototype data.")
    st.markdown('</div>',unsafe_allow_html=True)

# ============================================================
# PUBLIC DASHBOARD
# ============================================================
elif st.session_state.page=="Public Dashboard":
    st.header("👥 Public Safety Dashboard")
    st.info("Public view: detailed dam-break failure simulations are restricted to verified authority users. This view focuses on understandable safety information.")
    loc=st.selectbox("📍 Your location",list(LOCATIONS),key="public_loc")
    lat,lon=LOCATIONS[loc]
    w=weather(lat,lon)
    if w["success"]:
        a,b,c,d=st.columns(4); a.metric("🌡️ Temperature",f"{w['temperature']:.1f} °C"); b.metric("🌧️ Rainfall",f"{w['rainfall']:.1f} mm"); c.metric("💧 Humidity",f"{w['humidity']}%"); d.metric("💨 Wind",f"{w['wind']:.1f} m/s")
        st.caption("Weather data provided by OpenWeather.")
    dams=nearby_dams(loc)
    st.subheader("🏗️ Nearby Dams")
    cards=st.columns(3)
    for i,d in enumerate(dams):
        with cards[i%3]:
            st.markdown(f'<div class="water-card"><span class="badge">{d["risk"]} • {d["distance"]:.1f} km</span><h3>💧 {d["name"]}</h3><p>Water level: <b>{d["water_level"]:.1f}</b></p><p>Shutters: <b>{d["open_shutters"]}/{d["total_shutters"]}</b> • Opening: <b>{d["opening_percent"]}%</b></p></div>',unsafe_allow_html=True)
            zones=public_release_impact(d)
            st.caption("Potential controlled-release impact: "+" • ".join(f"{z}: {r}" for z,r in zones))
    st.subheader("🗺️ Public Monitoring Map")
    st_folium(dam_map(loc),height=520,width=None,returned_objects=[])
    st.subheader("🛡️ Safety principle")
    st.success("HYDROSCOPE provides public awareness and safety information. Official warnings and evacuation instructions remain the responsibility of authorized agencies.")

# ============================================================
# PREDICTION
# ============================================================
elif st.session_state.page=="Prediction":
    st.header("🌧️ Water-Level Prediction")
    name=st.selectbox("🏗️ Select Dam",list(DAM_DATABASE),key="pred_dam"); d=DAM_DATABASE[name]
    f=forecast(d["lat"],d["lon"])
    if not f["success"]: st.error(f["error"]); st.stop()
    s=rainfall_summary(f["data"])
    a,b,c,d4=st.columns(4); a.metric("6h rain",f"{s['rain_6h']} mm"); b.metric("12h rain",f"{s['rain_12h']} mm"); c.metric("24h rain",f"{s['rain_24h']} mm"); d4.metric("Peak 3h",f"{s['peak_3h']} mm")
    st.plotly_chart(go.Figure(go.Bar(x=f["data"]["datetime"],y=f["data"]["rainfall"])).update_layout(template="plotly_dark",height=350,title="Forecast Rainfall",xaxis_title="Time",yaxis_title="mm / 3h"),use_container_width=True)
    pred=predict_level(d,s["rain_24h"]); prob=release_probability(d,pred)
    a,b,c=st.columns(3); a.metric("Current level",d["water_level"]); b.metric("Predicted level",pred); c.metric("Release-risk indicator",f"{prob}%")
    st.warning("Prototype mathematical calculation; not an operational release decision.")

# ============================================================
# AUTH LOGIN
# ============================================================
elif st.session_state.page=="Authority Access":
    if st.session_state.authority:
        st.success(f"Verified authority session: {st.session_state.authority_id} • {st.session_state.authority_email}")
        if st.button("Sign out"): st.session_state.authority=False; st.rerun()
    else: authority_login()

# ============================================================
# AUTHORITY CONSOLE
# ============================================================
elif st.session_state.page=="Authority Console":
    if not st.session_state.authority:
        st.warning("Authority verification required."); st.session_state.page="Authority Access"; st.rerun()
    st.header("🔐 Authority Console")
    st.caption(f"Verified session: {st.session_state.authority_id} • {st.session_state.authority_email}")
    name=st.selectbox("🏗️ Dam",list(DAM_DATABASE),key="auth_dam"); d=DAM_DATABASE[name]
    a,b,c,e=st.columns(4); a.metric("Water level",d["water_level"]); b.metric("Inflow",f"{d['inflow']:.0f} m³/s"); c.metric("Outflow",f"{d['outflow']:.0f} m³/s"); e.metric("Open shutters",f"{d['open_shutters']}/{d['total_shutters']}")
    st.subheader("⚠️ Technical risk factors")
    factors=pd.DataFrame({"Factor":["Reservoir level","Inflow","Rainfall","Shutter opening","Net flow"],"Value":[d["water_level"],d["inflow"],d["rainfall"],d["opening_percent"],max(0,d["inflow"]-d["outflow"])],"Unit":["m","m³/s","mm","%","m³/s"]})
    st.dataframe(factors,use_container_width=True,hide_index=True)
    st.info("Use the Hydraulic Simulation tab for the detailed 2-D scenario model.")

# ============================================================
# AUTHORITY HYDRAULIC SIMULATION
# ============================================================
elif st.session_state.page=="Hydraulic Simulation":
    if not st.session_state.authority:
        st.warning("Authority verification required."); st.session_state.page="Authority Access"; st.rerun()
    st.header("🌊 Authority-Only 2-D Hydraulic Simulation")
    st.warning("Restricted technical scenario analysis. This prototype uses a simplified numerical implementation of the 2-D shallow-water/Saint-Venant equations and is not an operational flood forecast.")
    name=st.selectbox("🏗️ Dam",list(DAM_DATABASE),key="hyd_dam"); d=DAM_DATABASE[name]
    breach=st.slider("Hypothetical breach fraction",0.10,0.90,0.55,0.05)
    if st.button("▶ Run Hydraulic Scenario",type="primary"):
        with st.spinner("Solving 2-D shallow-water equations..."):
            result=saint_venant_2d(d,breach_fraction=breach)
        st.session_state.hyd_result=result
    if "hyd_result" in st.session_state:
        r=st.session_state.hyd_result
        a,b,c=st.columns(3); a.metric("Peak estimated velocity",f"{r['peak_velocity']:.2f} m/s"); b.metric("Peak discharge index",f"{r['peak_discharge']:.1f}"); c.metric("Wet cells",f"{np.sum(r['depth']>.08):,}")
        st.subheader("🌊 Maximum Flood Depth")
        fig=go.Figure(go.Heatmap(x=r["X"][0],y=r["Y"][:,0],z=r["depth"],colorbar_title="Depth (m)")); fig.update_layout(template="plotly_dark",height=500,xaxis_title="Downstream distance (m)",yaxis_title="Cross-stream distance (m)"); st.plotly_chart(fig,use_container_width=True)
        st.subheader("⏱️ Flood Arrival")
        arr=r["arrival"]; arr2=np.where(np.isnan(arr),np.nan,arr)
        fig2=go.Figure(go.Heatmap(x=r["X"][0],y=r["Y"][:,0],z=arr2,colorbar_title="Arrival (min)")); fig2.update_layout(template="plotly_dark",height=500); st.plotly_chart(fig2,use_container_width=True)
        st.subheader("📐 Governing equations")
        st.latex(r"\frac{\partial h}{\partial t}+\frac{\partial(hu)}{\partial x}+\frac{\partial(hv)}{\partial y}=0")
        st.latex(r"\frac{\partial(hu)}{\partial t}+\frac{\partial}{\partial x}(hu^2+\frac12gh^2)+\frac{\partial(huv)}{\partial y}=-gh\frac{\partial z}{\partial x}-ghS_{fx}")
        st.latex(r"\frac{\partial(hv)}{\partial t}+\frac{\partial(huv)}{\partial x}+\frac{\partial}{\partial y}(hv^2+\frac12gh^2)=-gh\frac{\partial z}{\partial y}-ghS_{fy}")
        st.caption("Production deployment requires calibrated DEM/topography, dam geometry, breach hydraulics, roughness, boundary conditions and validation against an established hydraulic solver.")

st.divider(); st.markdown('<div class="footer">💧 HYDROSCOPE • Public Flood Awareness + Authorized Technical Decision Support<br>Smart India Hackathon Prototype • Kerala</div>',unsafe_allow_html=True)
