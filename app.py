import math
from datetime import datetime
import numpy as np
import pandas as pd
import requests
import plotly.graph_objects as go
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title='HYDROSCOPE', page_icon='🌊', layout='wide')

st.markdown('''<style>
.stApp{background:radial-gradient(circle at 10% 10%,rgba(0,180,255,.13),transparent 30%),linear-gradient(135deg,#07111f,#081827 50%,#06101b);color:#eef7ff}
.block-container{padding-top:1.1rem;max-width:1450px}.hero{padding:1.25rem 1.5rem;border:1px solid rgba(255,255,255,.13);border-radius:22px;background:rgba(255,255,255,.055);margin-bottom:1rem}.hero-title{font-size:2.35rem;font-weight:800;letter-spacing:.08em}.hero-subtitle{color:#a9c7dd}.glass{padding:1rem;border:1px solid rgba(255,255,255,.1);border-radius:18px;background:rgba(255,255,255,.045);margin-bottom:.8rem}.small-muted{color:#93adc0;font-size:.82rem}.section-title{font-size:1.4rem;font-weight:750;margin:.6rem 0 .8rem}div.stButton>button{border-radius:12px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.055);color:#eaf7ff;min-height:42px}[data-testid=stMetric]{background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.09);border-radius:16px;padding:.7rem}.footer{text-align:center;color:#7894a8;font-size:.78rem;padding:1.5rem 0}
</style>''', unsafe_allow_html=True)

DAMS={
'Idukki Dam':dict(lat=9.8494,lon=76.9726,water_level=88.,inflow=1800.,outflow=600.,rainfall=72.,shutters=8,open_shutters=2,opening_pct=20.,warning_level=89.,critical_level=91.,capacity_level=92.,surface_area_km2=60.),
'Idamalayar Dam':dict(lat=10.2068,lon=76.7032,water_level=72.,inflow=920.,outflow=310.,rainfall=48.,shutters=4,open_shutters=1,opening_pct=15.,warning_level=75.,critical_level=77.,capacity_level=78.,surface_area_km2=28.),
'Malankara Dam':dict(lat=9.7804,lon=76.8787,water_level=67.,inflow=210.,outflow=95.,rainfall=41.,shutters=6,open_shutters=1,opening_pct=10.,warning_level=69.,critical_level=71.,capacity_level=72.,surface_area_km2=12.),
'Bhoothathankettu':dict(lat=10.1457,lon=76.6788,water_level=61.,inflow=160.,outflow=80.,rainfall=36.,shutters=5,open_shutters=1,opening_pct=10.,warning_level=63.,critical_level=65.,capacity_level=66.,surface_area_km2=8.),
'Pamba Dam':dict(lat=9.3805,lon=76.9275,water_level=64.,inflow=450.,outflow=170.,rainfall=39.,shutters=6,open_shutters=1,opening_pct=12.,warning_level=66.,critical_level=68.,capacity_level=69.,surface_area_km2=17.),
'Kakki Dam':dict(lat=9.35,lon=77.0,water_level=70.,inflow=520.,outflow=190.,rainfall=44.,shutters=4,open_shutters=1,opening_pct=15.,warning_level=72.,critical_level=74.,capacity_level=75.,surface_area_km2=20.),
'Neyyar Dam':dict(lat=8.535,lon=77.145,water_level=58.,inflow=190.,outflow=75.,rainfall=31.,shutters=4,open_shutters=0,opening_pct=0.,warning_level=61.,critical_level=63.,capacity_level=64.,surface_area_km2=10.),
'Banasura Sagar Dam':dict(lat=11.7,lon=75.95,water_level=63.,inflow=330.,outflow=120.,rainfall=52.,shutters=4,open_shutters=1,opening_pct=10.,warning_level=65.,critical_level=67.,capacity_level=68.,surface_area_km2=18.)}
LOCATIONS={'Kochi':(9.9312,76.2673),'Idukki':(9.85,76.97),'Munnar':(10.0889,77.0595),'Kothamangalam':(10.058,76.629),'Thodupuzha':(9.895,76.718),'Kottayam':(9.5916,76.5222),'Pathanamthitta':(9.2648,76.787),'Alappuzha':(9.4981,76.3388),'Thiruvananthapuram':(8.5241,76.9366),'Wayanad':(11.6854,76.132)}

if 'page' not in st.session_state: st.session_state.page='Dashboard'
if 'tick' not in st.session_state: st.session_state.tick=0
if 'game' not in st.session_state: st.session_state.game=None
if 'game_msg' not in st.session_state: st.session_state.game_msg=''

def haversine(a,b,c,d):
    R=6371.; p1,p2=math.radians(a),math.radians(c); dp=math.radians(c-a); dl=math.radians(d-b)
    x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(x))

def nearby(location,radius=120):
    la,lo=LOCATIONS[location]; out=[]
    for name,d in DAMS.items():
        x=dict(d); x['name']=name; x['distance_km']=haversine(la,lo,d['lat'],d['lon']);
        if x['distance_km']<=radius: out.append(x)
    return sorted(out,key=lambda x:x['distance_km'])

def risk(level,d): return 'High' if level>=d['critical_level'] else ('Moderate' if level>=d['warning_level'] else 'Normal')
def icon(r): return {'Normal':'🟢','Moderate':'🟠','High':'🔴'}[r]

def simulate(d,rain,steps=1,dt_hours=1):
    s=dict(d); area=max(s['surface_area_km2'],.1)*1e6; level=s['water_level']; inflow=s['inflow']; outflow=s['outflow']
    rain_factor=1+min(max(rain,0)/250,1.2)
    for _ in range(steps):
        inflow=.72*inflow+.28*inflow*rain_factor
        r=risk(level,s); mult={'Normal':1.,'Moderate':1.12,'High':1.28}[r]; out=outflow*mult
        dh=np.clip(((inflow-out)*dt_hours*3600)/area,-.35,.35); level+=float(dh)
    s.update(water_level=round(level,3),inflow=round(inflow,1),outflow=round(out,1),risk=risk(level,s))
    return s

def prediction(d,rains):
    s=dict(d); rows=[]
    for i,r in enumerate(rains,1):
        s=simulate(s,r,1,3); rows.append([i,r,s['water_level'],s['inflow'],s['outflow'],s['risk']])
    return pd.DataFrame(rows,columns=['step','rainfall','water_level','inflow','outflow','risk'])

def flood_scenario(d):
    f=np.clip((d['water_level']-d['warning_level'])/max(d['capacity_level']-d['warning_level'],.1),0,1.5); frac=d['water_level']/d['capacity_level']
    peak=max(100,d['inflow']*(1.8+2.2*frac)*(1+.35*f)); arrival=max(10,90-35*frac-15*f)
    population=int(np.clip(5000+peak*9+d['surface_area_km2']*1200,5000,2500000))
    t=np.linspace(0,max(arrival*2.5,120),100); wave=peak*np.exp(-((t-arrival)**2)/(2*max(arrival*.3,8)**2))
    return peak,arrival,population,t,wave

@st.cache_data(ttl=600)
def weather(lat,lon,key):
    a=requests.get('https://api.openweathermap.org/data/2.5/weather',params={'lat':lat,'lon':lon,'appid':key,'units':'metric'},timeout=10); a.raise_for_status()
    b=requests.get('https://api.openweathermap.org/data/2.5/forecast',params={'lat':lat,'lon':lon,'appid':key,'units':'metric'},timeout=10); b.raise_for_status(); return a.json(),b.json()

def map_view(location,selected):
    la,lo=LOCATIONS[location]; m=folium.Map([la,lo],zoom_start=8,tiles='OpenStreetMap')
    folium.Circle([la,lo],radius=120000,color='#38bdf8',fill=True,fill_opacity=.04).add_to(m)
    folium.Marker([la,lo],tooltip=f'User location: {location}',icon=folium.Icon(color='blue',icon='user')).add_to(m)
    for x in nearby(location):
        d=DAMS[x['name']]; r=risk(d['water_level'],d); color={'Normal':'green','Moderate':'orange','High':'red'}[r]
        folium.Marker([d['lat'],d['lon']],tooltip=f'{icon(r)} {x["name"]}',popup=f'<b>{x["name"]}</b><br>Risk: {r}<br>Water level: {d["water_level"]} m<br>Inflow: {d["inflow"]:.0f} m³/s<br>Outflow: {d["outflow"]:.0f} m³/s<br>Shutters: {d["open_shutters"]}/{d["shutters"]}<br><i>Prototype reservoir data</i>',icon=folium.Icon(color=color,icon='tint',prefix='fa')).add_to(m)
        if x['name']==selected: folium.Circle([d['lat'],d['lon']],radius=7000,color='#fbbf24',fill=False,weight=3).add_to(m)
    return m

st.markdown('<div class="hero"><div class="hero-title">🌊 HYDROSCOPE</div><div class="hero-subtitle">Public Dam Monitoring • Water Prediction • Flood-Risk Awareness</div></div>',unsafe_allow_html=True)
nav=['Dashboard','Dam Monitoring','Prediction','Flood Simulation','Public Safety','Hydro Challenge']
cols=st.columns(len(nav))
for c,n in zip(cols,nav):
    with c:
        if st.button(n,key='nav_'+n,use_container_width=True): st.session_state.page=n; st.rerun()

location=st.selectbox('📍 Select your location',list(LOCATIONS),index=list(LOCATIONS).index('Idukki'))
near=nearby(location)
if not near: st.error('No prototype dams found within the monitoring radius.'); st.stop()
selected=st.selectbox('💧 Select a nearby dam',[x['name'] for x in near])
d=dict(DAMS[selected])
if st.session_state.tick: d=simulate(d,max(d['rainfall'],5+st.session_state.tick*2),st.session_state.tick,1)

key=st.secrets.get('OPENWEATHER_API_KEY',None)
current=forecast=None; weather_error=None
if key:
    try: current,forecast=weather(*LOCATIONS[location],key)
    except Exception as e: weather_error=str(e)

rain_live=float(current.get('rain',{}).get('1h',0)) if current else d['rainfall']

if st.session_state.page=='Dashboard':
    st.markdown('<div class="section-title">📊 Public Monitoring Dashboard</div>',unsafe_allow_html=True)
    a,b,c,e=st.columns(4); a.metric('Selected Location',location); b.metric('Nearby Dams',len(near)); c.metric('Selected Dam',selected); r=risk(d['water_level'],d); e.metric('Current Risk',f'{icon(r)} {r}')
    if current:
        w=current['main']; c1,c2,c3,c4=st.columns(4); c1.metric('Temperature',f"{w['temp']:.1f} °C"); c2.metric('Rainfall (1h)',f'{rain_live:.1f} mm'); c3.metric('Humidity',f"{w['humidity']} %"); c4.metric('Condition',current['weather'][0]['description'].title()); st.caption('Weather data provided by OpenWeather.')
    else: st.info('OpenWeather data unavailable. Configure OPENWEATHER_API_KEY in Streamlit Secrets.' if not weather_error else f'Weather service unavailable: {weather_error}')
    st_folium(map_view(location,selected),height=500)
    a,b,c,e=st.columns(4); a.metric('Water Level',f"{d['water_level']:.2f} m"); b.metric('Inflow',f"{d['inflow']:.0f} m³/s"); c.metric('Outflow',f"{d['outflow']:.0f} m³/s"); e.metric('Shutters Open',f"{d['open_shutters']} / {d['shutters']}")
    st.info('Weather is live through OpenWeather. Reservoir parameters are internally simulated for the prototype and are designed to be replaceable by authorized official feeds.')

elif st.session_state.page=='Dam Monitoring':
    st.markdown('<div class="section-title">💧 Dam Monitoring</div>',unsafe_allow_html=True)
    a,b,c,e=st.columns(4); a.metric('Water Level',f"{d['water_level']:.2f} m"); b.metric('Inflow',f"{d['inflow']:.0f} m³/s"); c.metric('Outflow',f"{d['outflow']:.0f} m³/s"); e.metric('Risk',f"{icon(risk(d['water_level'],d))} {risk(d['water_level'],d)}")
    st.markdown('### 🚪 Shutter Status'); cs=st.columns(min(d['shutters'],8))
    for i in range(d['shutters']):
        with cs[i]: st.markdown(f"<div class='glass' style='text-align:center;font-size:1.4rem'>{'🟦' if i<d['open_shutters'] else '⬜'}<br><span class='small-muted'>Gate {i+1}</span></div>",unsafe_allow_html=True)
    times=pd.date_range(end=datetime.now(),periods=12,freq='h'); vals=np.linspace(d['water_level']-.7,d['water_level'],12)+.04*np.sin(np.arange(12)); fig=go.Figure(go.Scatter(x=times,y=vals,mode='lines+markers',name='Water level')); fig.add_hline(y=d['warning_level'],line_dash='dash',annotation_text='Warning'); fig.add_hline(y=d['critical_level'],line_dash='dash',annotation_text='Critical'); fig.update_layout(template='plotly_dark',height=380); st.plotly_chart(fig,use_container_width=True); st_folium(map_view(location,selected),height=450)

elif st.session_state.page=='Prediction':
    st.markdown('<div class="section-title">📈 Water-Level Prediction</div>',unsafe_allow_html=True)
    rains=[]
    if forecast:
        rains=[float(x.get('rain',{}).get('3h',0)) for x in forecast.get('list',[])[:8]]
    rains=(rains+[rain_live]*8)[:8]
    p=prediction(d,rains); final=p.iloc[-1]; a,b,c=st.columns(3); a.metric('Current Level',f"{d['water_level']:.2f} m"); b.metric('Predicted Level',f"{final.water_level:.2f} m"); c.metric('Predicted Risk',f"{icon(final.risk)} {final.risk}")
    fig=go.Figure(go.Scatter(x=list(range(0,len(p)+1)),y=[d['water_level']]+p.water_level.tolist(),mode='lines+markers',name='Predicted')); fig.add_hline(y=d['warning_level'],line_dash='dash',annotation_text='Warning'); fig.add_hline(y=d['critical_level'],line_dash='dash',annotation_text='Critical'); fig.update_layout(template='plotly_dark',height=400,xaxis_title='Forecast step (3h)',yaxis_title='Water level (m)'); st.plotly_chart(fig,use_container_width=True)
    st.dataframe(p,use_container_width=True,hide_index=True); st.info('Current prototype prediction is rule-based and mathematical. No dataset or machine-learning training model is used.')

elif st.session_state.page=='Flood Simulation':
    st.markdown('<div class="section-title">🌊 Hypothetical Flood Simulation</div>',unsafe_allow_html=True)
    peak,arrival,pop,t,wave=flood_scenario(d); a,b,c=st.columns(3); a.metric('Estimated Peak Flow',f'{peak:.0f} m³/s'); b.metric('Estimated Arrival',f'{arrival:.0f} min'); c.metric('Potential Population',f'{pop:,}')
    st.warning('Simplified hypothetical scenario for public awareness. It is not an operational emergency prediction or a validated engineering hydraulic model.')
    fig=go.Figure(go.Scatter(x=t,y=wave,mode='lines',name='Simplified flood wave')); fig.update_layout(template='plotly_dark',height=380,xaxis_title='Time after hypothetical breach (min)',yaxis_title='Relative discharge estimate (m³/s)'); st.plotly_chart(fig,use_container_width=True)
    st.markdown('### 🗺️ Potential Impact Zones');
    for z in ['Immediate downstream low-lying areas','River-adjacent settlements','Downstream roads and bridges','Flood-prone residential areas']: st.write('• '+z)
    st_folium(map_view(location,selected),height=430)

elif st.session_state.page=='Public Safety':
    st.markdown('<div class="section-title">🆘 Public Safety & Flood Awareness</div>',unsafe_allow_html=True)
    r=risk(d['water_level'],d); (st.error if r=='High' else st.warning if r=='Moderate' else st.success)(f'{icon(r)} {r.upper()} CONDITION — Follow official information and instructions.')
    st.markdown("""<div class='glass'><b>Public Safety Checklist</b><br><br>• Keep emergency contacts accessible.<br>• Follow official evacuation instructions when issued.<br>• Avoid flooded roads, bridges and fast-flowing water.<br>• Keep essential documents, medicines and emergency supplies ready.<br>• Do not rely on HYDROSCOPE as a replacement for official warnings.</div>""",unsafe_allow_html=True)
    st.markdown('### 🏛️ Official Information Sources'); st.write('• Kerala State Disaster Management Authority (KSDMA)'); st.write('• Central Water Commission (CWC)'); st.write('• Kerala Water Resources / Irrigation authorities'); st.write('• KSEB and other authorized dam/reservoir data providers'); st.info('HYDROSCOPE is a public information and flood-awareness platform. It does not operate dam gates, control reservoirs, or issue official evacuation orders.')

else:
    st.markdown('<div class="section-title">🎮 HYDRO CHALLENGE</div>',unsafe_allow_html=True)
    st.write('Educational simulation showing how rainfall, inflow, reservoir level and preparedness interact.')
    if st.session_state.game is None:
        if st.button('▶️ Start Challenge'): st.session_state.game={'level':86.5,'rain':55.,'inflow':1400.,'outflow':500.,'score':0,'round':1}; st.session_state.game_msg=''; st.rerun()
    else:
        g=st.session_state.game; a,b,c,e=st.columns(4); a.metric('Round',g['round']); b.metric('Water Level',f"{g['level']:.1f} m"); c.metric('Inflow',f"{g['inflow']:.0f} m³/s"); e.metric('Rainfall',f"{g['rain']:.0f} mm")
        st.markdown('### Choose an educational public-safety response'); x,y,z=st.columns(3)
        action=None
        with x:
            if st.button('🟢 Continue Monitoring',use_container_width=True): action='monitor'
        with y:
            if st.button('🟠 Prepare Public Alert',use_container_width=True): action='alert'
        with z:
            if st.button('🔴 Escalate Emergency Readiness',use_container_width=True): action='emergency'
        if action:
            delta={'monitor':10,'alert':15,'emergency':20}[action]; release={'monitor':1.,'alert':1.1,'emergency':1.2}[action]; g['score']+=delta; g['outflow']*=release; g['rain']*=1.05 if g['round']%2==0 else .95; g['inflow']*=1+max(g['rain']-45,0)/500; g['level']=max(75,g['level']+np.clip(((g['inflow']-g['outflow'])*3600)/35e6,-.3,.3)); g['round']+=1; st.session_state.game_msg='Educational response applied; the simulated reservoir state has advanced.'; st.rerun()
        if st.session_state.game_msg: st.info(st.session_state.game_msg)
        if g['round']>6:
            st.success(f"Challenge complete! Educational score: {g['score']}");
            if st.button('🔄 Restart Challenge'): st.session_state.game=None; st.session_state.game_msg=''; st.rerun()
        st.caption('Educational simulation only. It does not recommend real dam-gate operations and must not be used for emergency decisions.')

st.markdown('<div class="footer">HYDROSCOPE • Public Dam Monitoring & Flood-Risk Awareness Prototype<br>Prototype reservoir values are simulated unless explicitly marked as live API data.</div>',unsafe_allow_html=True)
