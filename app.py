import math
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import requests
import plotly.graph_objects as go
import streamlit as st
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components

st.set_page_config(page_title='HYDROSCOPE', page_icon='🌊', layout='wide', initial_sidebar_state='collapsed')

st.markdown('''<style>
.stApp{background:radial-gradient(circle at 10% 10%,rgba(25,120,160,.20),transparent 28%),linear-gradient(135deg,#06131b,#081b26 48%,#051017);color:#eaf8ff}
header[data-testid="stHeader"]{background:transparent}.block-container{max-width:1450px;padding-top:1rem}
.brand{font-size:2.25rem;font-weight:800;letter-spacing:2px}.tagline{color:#8fc9df;margin-top:-7px;margin-bottom:15px}
.status{display:inline-block;padding:6px 12px;border-radius:999px;font-size:.78rem;font-weight:700;background:rgba(255,193,7,.12);border:1px solid rgba(255,193,7,.25);color:#ffd76a}
.live{display:inline-block;padding:6px 12px;border-radius:999px;font-size:.78rem;font-weight:700;background:rgba(0,210,140,.12);border:1px solid rgba(0,210,140,.25);color:#73efbe}
.title{font-size:1.45rem;font-weight:750;margin:8px 0 4px}.note{color:#91aeb9;font-size:.82rem}.footer{margin-top:30px;padding-top:16px;border-top:1px solid rgba(255,255,255,.08);color:#71919e;font-size:.78rem;text-align:center}
div.stButton>button{border-radius:12px;border:1px solid rgba(130,210,240,.16);background:rgba(255,255,255,.045);color:#eaf8ff;min-height:42px;font-weight:650}div.stButton>button:hover{border-color:rgba(100,220,255,.55);background:rgba(50,170,210,.13)}
div[data-testid="stMetric"]{background:rgba(255,255,255,.035);border:1px solid rgba(160,225,255,.10);border-radius:14px;padding:10px}
</style>''', unsafe_allow_html=True)

DAMS={
'Idukki Dam':(9.8494,76.9726,88,1800,600,72,8,2,20,60,.84),
'Idamalayar Dam':(10.2068,76.7032,72,920,310,48,4,1,15,48,.70),
'Malankara Dam':(9.7804,76.8787,67,210,95,41,6,1,10,18,.64),
'Bhoothathankettu':(10.1457,76.6788,61,160,80,36,5,1,10,15,.58),
'Pamba Dam':(9.3805,76.9275,64,450,170,39,6,1,12,35,.61),
'Kakki Dam':(9.35,77.0,70,520,190,44,4,1,15,40,.68),
'Neyyar Dam':(8.535,77.145,58,190,75,31,4,0,0,20,.55),
'Banasura Sagar Dam':(11.7,75.95,63,330,120,52,4,1,10,32,.60),}
LOCS={'Kochi':(9.9312,76.2673),'Idukki':(9.85,76.97),'Munnar':(10.0889,77.0595),'Kothamangalam':(10.058,76.629),'Thodupuzha':(9.895,76.718),'Kottayam':(9.5916,76.5222),'Pathanamthitta':(9.2648,76.787),'Alappuzha':(9.4981,76.3388),'Thiruvananthapuram':(8.5241,76.9366),'Wayanad':(11.6854,76.132)}

def hav(a,b,c,d):
 r=6371; p1=math.radians(a);p2=math.radians(c);dp=math.radians(c-a);dl=math.radians(d-b)
 x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
 return 2*r*math.asin(math.sqrt(x))

def nearby(loc):
 a,b=LOCS[loc]; return sorted([(n,hav(a,b,d[0],d[1])) for n,d in DAMS.items() if hav(a,b,d[0],d[1])<=120],key=lambda x:x[1])

def key():
 try:return st.secrets['OPENWEATHER_API_KEY']
 except:return ''

@st.cache_data(ttl=600)
def weather(lat,lon,k):
 if not k:return {'ok':False,'error':'OPENWEATHER_API_KEY is not configured.'}
 try:
  r=requests.get('https://api.openweathermap.org/data/2.5/weather',params={'lat':lat,'lon':lon,'appid':k,'units':'metric'},timeout=10);x=r.json()
  if r.status_code!=200:return {'ok':False,'error':x.get('message','Weather request failed')}
  return {'ok':True,'temp':x['main']['temp'],'humidity':x['main']['humidity'],'wind':x['wind'].get('speed',0),'rain':x.get('rain',{}).get('1h',0),'description':x['weather'][0]['description'].title(),'city':x.get('name','Selected location')}
 except Exception as e:return {'ok':False,'error':str(e)}

@st.cache_data(ttl=600)
def forecast(lat,lon,k):
 if not k:return {'ok':False,'points':[],'error':'API key unavailable'}
 try:
  r=requests.get('https://api.openweathermap.org/data/2.5/forecast',params={'lat':lat,'lon':lon,'appid':k,'units':'metric'},timeout=10);x=r.json()
  if r.status_code!=200:return {'ok':False,'points':[],'error':x.get('message','Forecast failed')}
  pts=[]
  for q in x['list']:
   pts.append({'dt':datetime.fromtimestamp(q['dt'],timezone.utc),'rain':q.get('rain',{}).get('3h',0)})
  return {'ok':True,'points':pts}
 except Exception as e:return {'ok':False,'points':[],'error':str(e)}

def model(d,w,f):
 lat,lon,h,qin,qout,base_rain,sh,op,opening,area,cap=d
 rain=w.get('rain',base_rain) if w.get('ok') else base_rain
 next24=sum(x['rain'] for x in f.get('points',[])[:8])
 mult=1+min(1.2,(max(0,rain)+.35*next24)/120)
 inflow=qin*mult
 outflow=qout*(1+.25*max(0,(cap*100-70)/30))
 dt=3600; dv=(inflow-outflow)*dt; dh=dv/(area*1e6)
 h1=h+dh; h6=h+6*dh; pct=min(110,max(0,cap*100+(h6-h)*2))
 risk='High' if pct>=92 or rain>=100 or inflow/qin>=1.65 else 'Moderate' if pct>=78 or rain>=50 or inflow/qin>=1.25 else 'Normal'
 breach=min(.85,max(.15,.20+.45*max(0,pct-70)/30)); peak=max(500,inflow*(1.5+3*breach)); arrival=max(8,95-55*breach); pop=int(15000+95000*breach+180*max(0,pct-70))
 return {'lat':lat,'lon':lon,'h':h,'inflow':inflow,'outflow':outflow,'rain':rain,'next24':next24,'sh':sh,'op':op,'opening':opening,'h1':h1,'h6':h6,'pct':pct,'risk':risk,'breach':breach,'peak':peak,'arrival':arrival,'pop':pop,'area':area}

def dam_map(loc,selected):
 la,lo=LOCS[loc];m=folium.Map([la,lo],zoom_start=8,tiles='OpenStreetMap');folium.Circle([la,lo],120000,color='#36c8ef',fill=True,fill_opacity=.03).add_to(m);folium.Marker([la,lo],tooltip=f'User location: {loc}',icon=folium.Icon(color='blue',icon='user',prefix='fa')).add_to(m)
 colors={'Normal':'green','Moderate':'orange','High':'red'}
 for n,d in DAMS.items():
  dist=hav(la,lo,d[0],d[1])
  if dist>120:continue
  folium.Marker([d[0],d[1]],tooltip=('★ ' if n==selected else '')+n,popup=f'<b>{n}</b><br>Distance: {dist:.1f} km<br>Water level: {d[2]:.1f} m<br><b>SIMULATION MODE</b>',icon=folium.Icon(color=('orange' if d[10]>=.78 else 'green'),icon='tint',prefix='fa')).add_to(m)
 return m

def level_chart(s):
 x=np.arange(7);y=np.linspace(s['h'],s['h6'],7);f=go.Figure(go.Scatter(x=x,y=y,mode='lines+markers',name='Modelled level'));f.update_layout(height=340,margin=dict(l=10,r=10,t=30,b=10),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis_title='Hours',yaxis_title='Level (m)',font=dict(color='#d9f3ff'));return f

def safety(r):
 return {'High':'High-risk simulation condition. Follow official emergency instructions, move to safer/elevated locations when instructed, and avoid flooded roads and waterways.','Moderate':'Moderate simulation condition. Monitor official alerts, avoid unnecessary travel near waterways, and keep an emergency plan ready.','Normal':'Normal simulation condition. Continue monitoring weather and official emergency information.'}[r]

if 'page' not in st.session_state:st.session_state.page='Home'
pages=['Home','Dam Monitor','Prediction','Flood Simulation','Public Safety','Flood Ready']
st.markdown('<div class="brand">🌊 HYDROSCOPE</div><div class="tagline">Public Dam Monitoring • Water Prediction • Flood-Risk Awareness</div>',unsafe_allow_html=True)
cols=st.columns(len(pages))
for i,p in enumerate(pages):
 with cols[i]:
  if st.button(p,key='nav_'+p,use_container_width=True):st.session_state.page=p
st.divider()

loc=st.selectbox('📍 Select your location',list(LOCS),index=list(LOCS).index('Idukki'))
near=nearby(loc)
if not near:st.error('No prototype dams within 120 km.');st.stop()
dam=st.selectbox('💧 Select a nearby dam',[x[0] for x in near])
k=key();la,lo=LOCS[loc];w=weather(la,lo,k);f=forecast(la,lo,k);s=model(DAMS[dam],w,f)

c=st.columns(4);c[0].markdown('<span class="status">DAM TELEMETRY: SIMULATION</span>',unsafe_allow_html=True);c[1].markdown('<span class="live">WEATHER: LIVE API</span>' if w.get('ok') else '<span class="status">WEATHER: API UNAVAILABLE</span>',unsafe_allow_html=True);c[2].write(f'**Dam:** {dam}');c[3].write(f'**Risk:** {s["risk"]}')

page=st.session_state.page
if page=='Home':
 st.markdown('<div class="title">Public Flood Awareness Dashboard</div>',unsafe_allow_html=True);st.write('One integrated workflow: weather → simulated telemetry → water-balance model → prediction → risk → flood scenario → public safety.')
 a,b,c,d=st.columns(4);a.metric('Water Level',f'{s["h"]:.1f} m');b.metric('Inflow',f'{s["inflow"]:.0f} m³/s');c.metric('Outflow',f'{s["outflow"]:.0f} m³/s');d.metric('Rainfall',f'{s["rain"]:.1f} mm/h')
 l,r=st.columns([1.35,1]);
 with l:st.markdown('### 🗺️ Nearby dams');st_folium(dam_map(loc,dam),height=500,returned_objects=[])
 with r:
  st.markdown('### 🌧️ Weather')
  if w.get('ok'):x,y=st.columns(2);x.metric('Temperature',f'{w["temp"]:.1f} °C');x.metric('Humidity',f'{w["humidity"]:.0f}%');y.metric('Rainfall',f'{w["rain"]:.1f} mm/h');y.metric('Wind',f'{w["wind"]:.1f} m/s');st.caption('Weather data provided by OpenWeather.')
  else:st.warning(w['error'])
  st.markdown('### 🚦 Integrated assessment');st.write(safety(s['risk']));st.info('Reservoir telemetry is simulated in this prototype. It is not official live dam status.')
elif page=='Dam Monitor':
 st.markdown('<div class="title">💧 Dam Monitor</div>',unsafe_allow_html=True);st.caption('Simulation Mode: telemetry responds to live weather inputs when available.')
 a,b,c,d,e=st.columns(5);a.metric('Water Level',f'{s["h"]:.2f} m');b.metric('Inflow',f'{s["inflow"]:.0f} m³/s');c.metric('Outflow',f'{s["outflow"]:.0f} m³/s');d.metric('Shutters Open',f'{s["op"]} / {s["sh"]}');e.metric('Rainfall',f'{s["rain"]:.1f} mm/h')
 l,r=st.columns([1.2,1]);
 with l:st.plotly_chart(level_chart(s),use_container_width=True)
 with r:st.dataframe(pd.DataFrame({'Parameter':['Water level','Inflow','Outflow','Rainfall','Shutters open','Shutter opening'],'Value':[f'{s["h"]:.2f} m',f'{s["inflow"]:.0f} m³/s',f'{s["outflow"]:.0f} m³/s',f'{s["rain"]:.1f} mm/h',f'{s["op"]}/{s["sh"]}',f'{s["opening"]:.1f}%']}),hide_index=True,use_container_width=True);st.info('The simulated telemetry layer can later be replaced by an authorized official API/data feed.')
elif page=='Prediction':
 st.markdown('<div class="title">📈 Water-Level Prediction</div>',unsafe_allow_html=True);a,b,c=st.columns(3);a.metric('Current',f'{s["h"]:.2f} m');b.metric('1-hour estimate',f'{s["h1"]:.2f} m');c.metric('6-hour estimate',f'{s["h6"]:.2f} m');st.plotly_chart(level_chart(s),use_container_width=True)
 l,r=st.columns(2)
 with l:st.markdown('### 🌧️ Rainfall input');st.write(f'Current rainfall: **{s["rain"]:.1f} mm/h**');st.write(f'Next 24 h forecast used: **{s["next24"]:.1f} mm**')
 with r:st.markdown('### 🧮 Current model');st.latex(r'\Delta V=(Q_{in}-Q_{out})\Delta t');st.latex(r'\Delta h\approx\frac{\Delta V}{A}');st.latex(r'h_{t+1}=h_t+\frac{(Q_{in}-Q_{out})\Delta t}{A}');st.warning('Simplified prototype model; not an official rule curve or operational dam-control model.')
elif page=='Flood Simulation':
 st.markdown('<div class="title">🌊 Flood Simulation</div>',unsafe_allow_html=True);st.write('Hypothetical dam-break scenario driven by the same integrated reservoir state. Simulation only.')
 a,b,c=st.columns(3);a.metric('Estimated Peak Flow',f'{s["peak"]:.0f} m³/s');b.metric('Estimated Arrival',f'{s["arrival"]:.0f} min');c.metric('Potential Exposure',f'{s["pop"]:,}')
 x=np.arange(13);y=s['peak']*np.exp(-((x-3)**2)/5.5);fig=go.Figure(go.Scatter(x=x,y=y,mode='lines+markers'));fig.update_layout(height=330,margin=dict(l=10,r=10,t=30,b=10),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis_title='Hours',yaxis_title='Hypothetical discharge',font=dict(color='#d9f3ff'));st.plotly_chart(fig,use_container_width=True)
 fmap=folium.Map([s['lat'],s['lon']],zoom_start=9,tiles='OpenStreetMap');folium.Marker([s['lat'],s['lon']],tooltip=f'{dam} scenario origin',icon=folium.Icon(color='red',icon='tint',prefix='fa')).add_to(fmap)
 for i,(name,km) in enumerate([('Zone A',8),('Zone B',18),('Zone C',30)]):
  folium.Circle([s['lat']-km/111,s['lon']+.015*(i+1)],radius=(i+1)*3500,color='red' if i==0 else 'orange',fill=True,fill_opacity=.12,popup=f'{name}: illustrative exposure zone').add_to(fmap)
 st_folium(fmap,height=500,returned_objects=[]);st.warning('SIMULATION ONLY — not a real flood forecast and not for evacuation decisions.')
elif page=='Public Safety':
 st.markdown('<div class="title">🚨 Public Safety</div>',unsafe_allow_html=True);st.markdown(f'### Current prototype status: **{s["risk"]}**');st.write(safety(s['risk']))
 for q in ['Follow official disaster-management and local-authority instructions.','Move to safer/elevated locations when an official evacuation instruction is issued.','Avoid flooded roads, bridges, riverbanks and fast-moving water.','Do not cross floodwater on foot or by vehicle.','Keep emergency documents, medicines, water and contacts ready.','Official alerts always take priority over HYDROSCOPE.']:st.write('• '+q)
 st.info('HYDROSCOPE is a public-awareness prototype. It does not operate dam gates or issue legally authoritative evacuation orders.')
elif page=='Flood Ready':
 st.markdown('<div class="title">🎮 Flood Ready — Safety Navigation Game</div>',unsafe_allow_html=True);st.write('Navigate the boat to the safe zone while avoiding flood debris. Keyboard, touch buttons and phone tilt are supported.')
 components.html('''<!doctype html><html><body style="margin:0;background:#071923;color:#eaf8ff;font-family:Arial;text-align:center"><div>🎮 Score: <span id=s>0</span> &nbsp; ❤️ <span id=l>3</span> &nbsp; <span id=m>Reach the green safe zone</span></div><canvas id=c width=900 height=500 style="width:100%;border-radius:18px;background:#073347;touch-action:none"></canvas><div><button onclick="K('ArrowLeft')">◀</button><button onclick="K('ArrowUp')">▲</button><button onclick="K('ArrowDown')">▼</button><button onclick="K('ArrowRight')">▶</button></div><small>WASD / arrows • touch • supported phones: tilt</small><script>
const c=document.getElementById('c'),x=c.getContext('2d');let b={x:90,y:240,w:48,h:24},safe={x:820,y:90,r:42},ks={},score=0,lives=3,run=1,ds=[];for(let i=0;i<12;i++)ds.push({x:200+Math.random()*650,y:30+Math.random()*440,r:9+Math.random()*12,v:.5+Math.random()*1.5});function K(k){ks[k]=1;setTimeout(()=>ks[k]=0,180)}function hit(d){let nx=Math.max(b.x,Math.min(d.x,b.x+b.w)),ny=Math.max(b.y,Math.min(d.y,b.y+b.h));return (d.x-nx)**2+(d.y-ny)**2<d.r*d.r}function loop(){if(run){if(ks.ArrowLeft||ks.a)b.x-=4;if(ks.ArrowRight||ks.d)b.x+=4;if(ks.ArrowUp||ks.w)b.y-=4;if(ks.ArrowDown||ks.s)b.y+=4;b.x=Math.max(0,Math.min(850,b.x));b.y=Math.max(0,Math.min(476,b.y));ds.forEach(d=>{d.x-=d.v;if(d.x<0){d.x=900;d.y=20+Math.random()*460}if(hit(d)){lives--;b.x=90;b.y=240;document.getElementById('l').textContent=lives;if(lives<=0){run=0;document.getElementById('m').textContent='Stay away from hazardous water. Press R to restart.'}}});if(Math.hypot(b.x+24-safe.x,b.y+12-safe.y)<safe.r){score+=100;run=0;document.getElementById('s').textContent=score;document.getElementById('m').textContent='Safe! Follow official instructions in a real emergency.'}}x.clearRect(0,0,900,500);x.fillStyle='#073347';x.fillRect(0,0,900,500);for(let i=0;i<18;i++){x.strokeStyle='rgba(150,240,255,.1)';x.beginPath();x.moveTo(0,25+i*30);x.lineTo(900,25+i*30);x.stroke()}x.beginPath();x.arc(safe.x,safe.y,safe.r,0,7);x.strokeStyle='#63efb4';x.lineWidth=4;x.stroke();x.fillStyle='#63efb4';x.font='bold 15px Arial';x.fillText('SAFE',safe.x-18,safe.y+5);ds.forEach(d=>{x.fillStyle='#8b5a3c';x.beginPath();x.arc(d.x,d.y,d.r,0,7);x.fill()});x.fillStyle='#f4c95d';x.beginPath();x.moveTo(b.x,b.y);x.lineTo(b.x+b.w-8,b.y);x.lineTo(b.x+b.w,b.y+12);x.lineTo(b.x+b.w-8,b.y+b.h);x.lineTo(b.x,b.y+b.h);x.fill();requestAnimationFrame(loop)}loop();window.onkeydown=e=>{ks[e.key]=1;if(e.key.toLowerCase()=='r'){b={x:90,y:240,w:48,h:24};lives=3;score=0;run=1;document.getElementById('l').textContent=3;document.getElementById('s').textContent=0;document.getElementById('m').textContent='Reach the green safe zone'}};window.onkeyup=e=>ks[e.key]=0;window.ondeviceorientation=e=>{if(e.gamma<-10){ks.ArrowLeft=1;ks.ArrowRight=0}else if(e.gamma>10){ks.ArrowRight=1;ks.ArrowLeft=0}else{ks.ArrowLeft=0;ks.ArrowRight=0}};
</script></body></html>''',height=610,scrolling=False)

st.markdown('<div class="footer">HYDROSCOPE is a public-awareness prototype. Weather data is provided by OpenWeather. Dam telemetry shown here is simulation data, not official live dam status. Always follow official disaster-management instructions.</div>',unsafe_allow_html=True)
