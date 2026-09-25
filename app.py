import math

import folium
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import streamlit.components.v1 as components
from streamlit_folium import st_folium

st.set_page_config(page_title="HYDROSCOPE", layout="wide", initial_sidebar_state="collapsed")

# ============================================================
# FIGMA-STYLE 3D WATER INTERFACE
# ============================================================
st.markdown(r"""
<style>
:root{
    --bg:#031521;
    --panel:#08283a;
    --panel2:#0b3449;
    --line:rgba(111,218,255,.20);
    --line2:rgba(111,218,255,.38);
    --text:#edfaff;
    --muted:#8fb8ca;
    --cyan:#39cfff;
    --cyan2:#79e5ff;
}

.stApp{
    background:
      radial-gradient(circle at 15% 8%, rgba(25,181,255,.16), transparent 25%),
      radial-gradient(circle at 85% 18%, rgba(0,102,190,.18), transparent 30%),
      linear-gradient(145deg,#02111b 0%,#05283c 48%,#02131f 100%);
    color:var(--text);
}

.stApp:after{
    content:"";
    position:fixed;
    left:-10%; right:-10%; bottom:-18vh;
    height:38vh;
    background:radial-gradient(ellipse,rgba(35,204,255,.13),transparent 68%);
    pointer-events:none;
    animation:waterGlow 8s ease-in-out infinite alternate;
}
@keyframes waterGlow{from{transform:translateX(-2%) scaleX(1)}to{transform:translateX(2%) scaleX(1.07)}}

.block-container{max-width:1420px;padding:1.2rem 1.5rem 4rem;position:relative;z-index:1}

/* Main brand panel */
.hs-brand{
    position:relative;
    min-height:145px;
    padding:28px 34px;
    border-radius:30px;
    border:1px solid var(--line);
    background:linear-gradient(145deg,rgba(11,57,79,.92),rgba(3,25,40,.78));
    box-shadow:0 28px 70px rgba(0,0,0,.30), inset 0 1px 0 rgba(255,255,255,.05);
    overflow:hidden;
    transform:perspective(1200px) rotateX(.6deg);
}
.hs-brand:before{
    content:"";
    position:absolute;
    width:420px;height:420px;
    right:-170px;top:-260px;
    border-radius:50%;
    border:1px solid rgba(91,220,255,.16);
    box-shadow:0 0 0 34px rgba(91,220,255,.035),0 0 0 68px rgba(91,220,255,.025);
}
.hs-brand:after{
    content:"";
    position:absolute;
    left:-10%;right:-10%;bottom:-44px;height:90px;
    background:radial-gradient(ellipse,rgba(50,210,255,.18),transparent 66%);
    animation:brandWave 5s ease-in-out infinite alternate;
}
@keyframes brandWave{from{transform:translateX(-4%)}to{transform:translateX(4%)}}
.hs-brand-title{font-size:48px;line-height:1;font-weight:900;letter-spacing:6px;position:relative;z-index:2}
.hs-brand-title span{color:var(--cyan2)}
.hs-brand-sub{margin-top:12px;color:#8fc7db;letter-spacing:2px;font-size:12px;font-weight:700;position:relative;z-index:2}
.hs-status{position:absolute;right:32px;bottom:28px;z-index:3;color:#8bdff4;font-size:11px;letter-spacing:1.5px}
.hs-dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:#55e0ff;box-shadow:0 0 14px #55e0ff;margin-right:7px}

/* Navigation */
div.stButton>button{
    width:100%;
    min-height:48px;
    border-radius:16px;
    border:1px solid rgba(105,211,247,.18);
    background:linear-gradient(145deg,rgba(10,54,74,.82),rgba(5,30,46,.82));
    color:#dff8ff;
    font-weight:800;
    letter-spacing:.2px;
    box-shadow:0 9px 20px rgba(0,0,0,.18), inset 0 1px 0 rgba(255,255,255,.04);
    transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
div.stButton>button:hover{
    transform:translateY(-3px) perspective(500px) rotateX(3deg);
    border-color:var(--line2);
    box-shadow:0 15px 28px rgba(0,0,0,.25),0 0 22px rgba(42,202,255,.12);
}
div.stButton>button:active{transform:translateY(1px) scale(.985)}

/* 3D content cards */
.hs-card{
    position:relative;
    min-height:150px;
    padding:23px;
    border-radius:24px;
    border:1px solid var(--line);
    background:linear-gradient(145deg,rgba(10,54,75,.88),rgba(4,28,44,.88));
    box-shadow:14px 18px 38px rgba(0,0,0,.24), inset 0 1px 0 rgba(255,255,255,.045);
    overflow:hidden;
    transform:perspective(900px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg)) translateZ(0);
    transition:transform .18s ease, border-color .2s ease, box-shadow .2s ease;
    will-change:transform;
}
.hs-card:hover{border-color:rgba(100,220,255,.42);box-shadow:18px 24px 48px rgba(0,0,0,.30),0 0 30px rgba(26,191,255,.09)}
.hs-card:before{
    content:"";
    position:absolute;
    width:180px;height:180px;
    right:-80px;bottom:-110px;
    border-radius:50%;
    background:radial-gradient(circle,rgba(38,204,255,.20),transparent 66%);
}
.hs-card:after{
    content:"";
    position:absolute;
    left:-25%;right:-25%;bottom:-44px;height:78px;
    background:radial-gradient(ellipse,rgba(49,204,255,.16),transparent 68%);
    animation:cardWave 4.5s ease-in-out infinite alternate;
}
@keyframes cardWave{from{transform:translateX(-4%)}to{transform:translateX(4%)}}
.hs-card-title{font-size:18px;font-weight:850;letter-spacing:.3px;position:relative;z-index:2}
.hs-card-label{font-size:11px;text-transform:uppercase;letter-spacing:1.7px;color:#78b7ca;font-weight:800;position:relative;z-index:2}
.hs-card-value{font-size:34px;font-weight:900;margin-top:8px;position:relative;z-index:2}
.hs-card-copy{color:#9cc5d5;font-size:13px;line-height:1.55;position:relative;z-index:2}

.hs-section{margin:30px 0 14px;font-size:23px;font-weight:900;letter-spacing:.2px}
.hs-section-line{height:1px;background:linear-gradient(90deg,rgba(80,205,255,.42),transparent);margin:8px 0 20px}
.hs-pill{display:inline-block;padding:6px 11px;border-radius:999px;border:1px solid rgba(91,216,255,.22);background:rgba(31,178,224,.08);font-size:11px;color:#aeeaff;font-weight:800;letter-spacing:.6px}
.hs-note{padding:15px 17px;border-radius:16px;background:rgba(10,47,62,.72);border:1px solid rgba(91,214,255,.15);color:#a8cbd7;font-size:13px;line-height:1.55}

/* Interactive dashboard controls */
.hs-gauge{position:relative;height:15px;border-radius:999px;background:rgba(255,255,255,.07);border:1px solid rgba(100,215,255,.16);overflow:hidden;margin-top:15px}
.hs-gauge-fill{height:100%;background:linear-gradient(90deg,#1aa8db,#6ee8ff);box-shadow:0 0 22px rgba(67,214,255,.35);border-radius:999px;transition:width .6s ease}
.hs-gauge-marker{position:absolute;top:-3px;width:21px;height:21px;border-radius:50%;background:#effcff;border:4px solid #39cfff;transform:translateX(-50%);box-shadow:0 0 18px rgba(57,207,255,.55)}
.hs-gauge-labels{display:flex;justify-content:space-between;color:#7099aa;font-size:10px;margin-top:6px}
.hs-gauge-labels strong{color:#dff9ff;font-size:12px}
.shutter-row{display:flex;gap:8px;margin-top:15px}
.shutter{height:34px;flex:1;border-radius:8px;border:1px solid rgba(125,220,255,.2);background:linear-gradient(180deg,#0c4056,#062637);box-shadow:inset 0 1px rgba(255,255,255,.04);transition:.25s}
.shutter.open{background:linear-gradient(180deg,#39d8ff,#087ca4);box-shadow:0 0 18px rgba(50,205,255,.22)}
.hs-interactive{padding:18px;border-radius:22px;border:1px solid rgba(100,215,255,.17);background:linear-gradient(145deg,rgba(8,49,67,.82),rgba(3,24,38,.86));box-shadow:10px 16px 34px rgba(0,0,0,.2);}
.hs-mini{font-size:11px;color:#80adbf;text-transform:uppercase;letter-spacing:1.4px;font-weight:800}
.hs-big{font-size:30px;font-weight:900;margin-top:5px}
.hs-click{font-size:12px;color:#9ec9d8;margin-top:5px}
/* Streamlit metrics */
div[data-testid="stMetric"]{
    min-height:112px;
    padding:17px;
    border-radius:21px;
    border:1px solid var(--line);
    background:linear-gradient(145deg,rgba(9,52,71,.88),rgba(4,28,43,.88));
    box-shadow:12px 16px 30px rgba(0,0,0,.20),inset 0 1px 0 rgba(255,255,255,.04);
}
div[data-testid="stMetricLabel"]{color:#86b8ca}
div[data-testid="stMetricValue"]{color:#effcff;font-weight:900}

/* Inputs */
div[data-baseweb="select"]>div,
div[data-baseweb="input"]>div{
    background:rgba(7,37,52,.88)!important;
    border:1px solid rgba(102,211,245,.18)!important;
    border-radius:14px!important;
}
.stSlider>div>div>div>div{background:#35caff!important}

/* Dataframes / alerts */
.stAlert{border-radius:17px!important;border:1px solid rgba(111,218,255,.16)!important}

.hs-footer{text-align:center;color:#648fa4;font-size:11px;letter-spacing:.8px;padding-top:30px}

/* Interactive reservoir / game visuals */
.hs-dam-scene{position:relative;height:390px;border-radius:30px;border:1px solid rgba(105,220,255,.22);overflow:hidden;background:linear-gradient(180deg,#071d2b 0%,#063b55 46%,#052537 100%);box-shadow:0 25px 70px rgba(0,0,0,.30),inset 0 1px rgba(255,255,255,.06);}
.hs-dam-sky{position:absolute;inset:0;background:radial-gradient(circle at 76% 18%,rgba(117,230,255,.18),transparent 20%),linear-gradient(180deg,rgba(5,22,34,.25),transparent 60%);}
.hs-moon{position:absolute;right:9%;top:9%;width:58px;height:58px;border-radius:50%;background:rgba(220,249,255,.75);box-shadow:0 0 35px rgba(113,224,255,.35);}
.hs-mountain{position:absolute;bottom:31%;width:0;height:0;border-left:180px solid transparent;border-right:180px solid transparent;border-bottom:155px solid rgba(11,61,78,.9);}
.hs-mountain.m1{left:-50px}.hs-mountain.m2{right:-70px;transform:scale(.78);border-bottom-color:rgba(9,53,70,.92)}
.hs-reservoir{position:absolute;left:0;right:0;bottom:28%;height:48%;overflow:hidden;background:linear-gradient(180deg,rgba(24,164,211,.78),rgba(5,87,125,.92));border-top:2px solid rgba(128,236,255,.45);}
.hs-waterline{position:absolute;inset:0;background:repeating-linear-gradient(-4deg,rgba(150,243,255,.18) 0 2px,transparent 2px 17px);animation:waterShift 5s linear infinite;}
@keyframes waterShift{from{transform:translateX(-50px)}to{transform:translateX(50px)}}
.hs-reservoir-fill{position:absolute;left:0;right:0;bottom:0;background:linear-gradient(180deg,rgba(104,229,255,.32),rgba(0,92,145,.2));transition:height .8s ease;}
.hs-dam-wall{position:absolute;left:50%;bottom:28%;transform:translateX(-50%);width:270px;height:155px;background:linear-gradient(90deg,#5b7280,#9db0b9 42%,#526b78);clip-path:polygon(10% 0,90% 0,100% 100%,0 100%);box-shadow:0 15px 28px rgba(0,0,0,.28);}
.hs-gates{position:absolute;left:50%;bottom:28%;transform:translateX(-50%);width:220px;height:115px;display:flex;gap:7px;align-items:flex-end;justify-content:center;padding:10px 16px;}
.hs-gate{height:92px;flex:1;border-radius:4px 4px 0 0;border:1px solid rgba(225,250,255,.28);background:linear-gradient(90deg,#29434e,#9db1b9,#2b4651);position:relative;overflow:hidden;}
.hs-gate.open:after{content:"";position:absolute;left:25%;right:25%;bottom:-55px;height:100px;background:linear-gradient(180deg,rgba(136,243,255,.85),rgba(29,171,222,.05));border-radius:50%;filter:blur(2px);animation:flowPulse 1.8s ease-in-out infinite;}
@keyframes flowPulse{0%,100%{transform:scaleX(.8);opacity:.55}50%{transform:scaleX(1.2);opacity:.95}}
.hs-river{position:absolute;left:0;right:0;bottom:0;height:30%;background:linear-gradient(180deg,#087fa8,#032e49);clip-path:polygon(0 32%,18% 20%,37% 40%,54% 16%,72% 37%,100% 12%,100% 100%,0 100%);}
.hs-river:after{content:"";position:absolute;inset:0;background:repeating-linear-gradient(-7deg,rgba(157,244,255,.18) 0 2px,transparent 2px 23px);animation:riverFlow 4s linear infinite;}
@keyframes riverFlow{from{transform:translateX(-70px)}to{transform:translateX(70px)}}
.hs-scene-label{position:absolute;z-index:5;left:24px;top:22px}.hs-scene-label .big{font-size:28px;font-weight:900}.hs-scene-label .small{font-size:10px;letter-spacing:1.5px;color:#8cc6d8;text-transform:uppercase;font-weight:800;margin-bottom:4px}
.hs-scene-level{position:absolute;right:24px;top:22px;z-index:5;text-align:right}.hs-scene-level strong{font-size:30px;font-weight:900}.hs-scene-level span{display:block;color:#9acbd9;font-size:11px}
.hg-world{position:relative;height:390px;border-radius:28px;overflow:hidden;border:1px solid rgba(110,225,255,.25);background:linear-gradient(180deg,#061c2a 0%,#0a4860 58%,#06354a 100%);box-shadow:inset 0 1px rgba(255,255,255,.06),0 24px 60px rgba(0,0,0,.28);}
.hg-cloud{position:absolute;width:150px;height:42px;border-radius:50px;background:rgba(185,229,239,.10);filter:blur(2px);z-index:2}.hg-c1{left:10%;top:13%}.hg-c2{right:12%;top:21%;transform:scale(.72)}
.hg-rain{position:absolute;inset:0;z-index:3;background:repeating-linear-gradient(105deg,transparent 0 18px,rgba(126,225,255,.55) 19px 21px,transparent 22px 42px);animation:hgRain .65s linear infinite;pointer-events:none}
@keyframes hgRain{from{transform:translateY(-30px)}to{transform:translateY(30px)}}
.hg-mountain{position:absolute;bottom:31%;width:0;height:0;border-left:190px solid transparent;border-right:190px solid transparent;border-bottom:175px solid rgba(9,66,82,.92);z-index:1}.hg-m1{left:-45px}.hg-m2{right:-85px;transform:scale(.8);border-bottom-color:rgba(7,57,75,.95)}
.hg-reservoir{position:absolute;left:0;right:0;bottom:29%;height:44%;overflow:hidden;background:rgba(7,119,160,.55);border-top:2px solid rgba(131,239,255,.38);z-index:4}.hg-water{position:absolute;left:0;right:0;bottom:0;background:linear-gradient(180deg,rgba(93,229,255,.88),rgba(3,92,139,.94));transition:height .8s ease}.hg-wave{position:absolute;inset:0;background:repeating-linear-gradient(-5deg,rgba(202,250,255,.16) 0 2px,transparent 2px 18px);animation:hgWave 4s linear infinite}@keyframes hgWave{from{transform:translateX(-50px)}to{transform:translateX(50px)}}
.hg-dam{position:absolute;left:50%;bottom:29%;transform:translateX(-50%);width:250px;height:145px;background:linear-gradient(90deg,#526a77,#9fb2ba 45%,#526a77);clip-path:polygon(9% 0,91% 0,100% 100%,0 100%);z-index:6;box-shadow:0 16px 30px rgba(0,0,0,.3)}.hg-dam-top{position:absolute;left:7%;right:7%;top:10px;height:8px;border-radius:8px;background:rgba(231,252,255,.28)}
.hg-gates{position:absolute;left:18%;right:18%;bottom:0;height:105px;display:flex;gap:7px;align-items:flex-end}.hg-gate{flex:1;height:84px;border-radius:3px 3px 0 0;border:1px solid rgba(236,253,255,.25);background:linear-gradient(90deg,#203b47,#a1b4bc,#203b47);position:relative;overflow:hidden}.hg-open{background:linear-gradient(90deg,#284651,#b5c6cc,#284651)}.hg-open:after{content:"";position:absolute;left:30%;right:30%;bottom:-46px;height:100px;border-radius:50%;background:linear-gradient(180deg,rgba(144,242,255,.9),rgba(28,163,215,.05));animation:hgFlow 1.3s ease-in-out infinite}@keyframes hgFlow{50%{transform:scaleX(1.35);opacity:.7}}
.hg-river{position:absolute;left:0;right:0;bottom:0;height:30%;z-index:5;background:linear-gradient(180deg,#087fa8,#032d48);clip-path:polygon(0 25%,18% 14%,36% 36%,52% 16%,70% 32%,100% 10%,100% 100%,0 100%)}.hg-river-flow{position:absolute;inset:0;background:repeating-linear-gradient(-8deg,rgba(168,246,255,.18) 0 2px,transparent 2px 22px);animation:hgRiver 2.8s linear infinite}@keyframes hgRiver{from{transform:translateX(-80px)}to{transform:translateX(80px)}}
.hg-valley{position:absolute;right:6%;bottom:13%;display:flex;gap:10px;z-index:8;align-items:flex-end}.hg-house{width:22px;height:18px;background:#d8c59c;position:relative;box-shadow:0 4px 9px rgba(0,0,0,.25)}.hg-house:before{content:"";position:absolute;left:-4px;top:-11px;border-left:15px solid transparent;border-right:15px solid transparent;border-bottom:14px solid #8a5660}.hg-overlay{position:absolute;left:18px;right:18px;top:17px;display:flex;gap:8px;z-index:12}.hg-overlay>div{padding:8px 11px;border-radius:13px;background:rgba(3,25,39,.68);border:1px solid rgba(131,231,255,.18);backdrop-filter:blur(8px)}.hg-overlay span{display:block;font-size:8px;letter-spacing:1.2px;color:#83b9c8;font-weight:800}.hg-overlay strong{display:block;font-size:17px;margin-top:2px;color:#effcff}
.hs-game{position:relative;padding:28px;border-radius:28px;border:1px solid rgba(102,221,255,.25);background:linear-gradient(145deg,rgba(7,52,72,.94),rgba(3,25,39,.96));box-shadow:20px 25px 55px rgba(0,0,0,.28);overflow:hidden;}
.hs-game:before{content:"";position:absolute;left:-10%;right:-10%;bottom:-30%;height:55%;background:radial-gradient(ellipse,rgba(40,208,255,.17),transparent 65%);animation:gameGlow 6s ease-in-out infinite alternate;}
@keyframes gameGlow{from{transform:translateX(-3%)}to{transform:translateX(3%)}}
.hs-game-title{font-size:38px;font-weight:950;letter-spacing:2px}.hs-game-sub{color:#91c6d6;font-size:13px;line-height:1.6}.hs-game-stat{padding:16px;border-radius:18px;border:1px solid rgba(100,215,255,.17);background:rgba(4,31,46,.72);text-align:center}.hs-game-stat strong{display:block;font-size:25px;margin-top:5px}.hs-game-bar{height:14px;border-radius:99px;background:rgba(255,255,255,.07);overflow:hidden;border:1px solid rgba(100,215,255,.15);margin-top:9px}.hs-game-bar>span{display:block;height:100%;background:linear-gradient(90deg,#1daedb,#79e7ff);transition:width .4s ease}.hs-game-over{padding:22px;border-radius:22px;border:1px solid rgba(100,220,255,.3);background:rgba(8,58,77,.72);text-align:center}.hs-score{font-size:54px;font-weight:950;color:#7de9ff}

/* Remove default Streamlit decoration */
#MainMenu,footer{visibility:hidden}
</style>
""", unsafe_allow_html=True)

# Mouse-position water ripple + 3D card tilt.
# The ripple is created only where the pointer is pressed, not continuously across the page.
components.html(r"""
<script>
(function(){
  const doc = window.parent.document;
  if(doc.__hydroscopeInteractionInstalled) return;
  doc.__hydroscopeInteractionInstalled = true;

  const layer = doc.createElement('div');
  layer.id = 'hydroscope-ripples';
  layer.style.cssText='position:fixed;inset:0;z-index:999999;pointer-events:none;overflow:hidden;';
  doc.body.appendChild(layer);

  function ripple(x,y){
    const el=doc.createElement('span');
    el.style.cssText=`position:absolute;left:${x-16}px;top:${y-16}px;width:32px;height:32px;border:1.5px solid rgba(88,221,255,.70);border-radius:50%;box-shadow:0 0 18px rgba(44,204,255,.16);transform:scale(.25);opacity:.85;transition:transform .85s cubic-bezier(.2,.7,.2,1),opacity .95s ease-out;`;
    layer.appendChild(el);
    requestAnimationFrame(()=>{el.style.transform='scale(3.5)';el.style.opacity='0';});
    setTimeout(()=>el.remove(),1000);
  }
  doc.addEventListener('pointerdown',e=>ripple(e.clientX,e.clientY),{passive:true});

  function reset(card){card.style.setProperty('--rx','0deg');card.style.setProperty('--ry','0deg');}
  doc.addEventListener('pointermove',e=>{
    const card=e.target.closest && e.target.closest('.hs-card');
    if(!card){doc.querySelectorAll('.hs-card').forEach(reset);return;}
    const r=card.getBoundingClientRect();
    const px=(e.clientX-r.left)/r.width-.5;
    const py=(e.clientY-r.top)/r.height-.5;
    card.style.setProperty('--rx',`${(-py*7).toFixed(2)}deg`);
    card.style.setProperty('--ry',`${(px*9).toFixed(2)}deg`);
  },{passive:true});
  doc.addEventListener('pointerleave',()=>doc.querySelectorAll('.hs-card').forEach(reset),{passive:true});
})();
</script>
""", height=0)

# ============================================================
# DEMO DATA
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
# Major Kerala locations: district headquarters plus major cities/towns used as public search points.
# Coordinates are representative map points; they are not intended as precise user geolocation.
LOCATIONS={
"Thiruvananthapuram":(8.5241,76.9366),"Neyyattinkara":(8.3988,77.0820),"Attingal":(8.6961,76.8151),"Varkala":(8.7379,76.7163),
"Kollam":(8.8932,76.6141),"Karunagappally":(9.0580,76.5350),"Punalur":(9.0005,76.9254),"Kottarakkara":(9.0060,76.7729),
"Pathanamthitta":(9.2648,76.7870),"Adoor":(9.1551,76.7319),"Thiruvalla":(9.3835,76.5740),"Ranni":(9.3850,76.8120),"Konni":(9.2343,76.8497),
"Alappuzha":(9.4981,76.3388),"Cherthala":(9.6850,76.3356),"Kayamkulam":(9.1810,76.5009),"Chengannur":(9.3151,76.6151),"Mavelikara":(9.2594,76.5560),
"Kottayam":(9.5916,76.5222),"Changanassery":(9.4420,76.5363),"Pala":(9.7047,76.6856),"Ettumanoor":(9.6690,76.5600),"Vaikom":(9.7480,76.3950),
"Painavu":(9.8500,76.9726),"Thodupuzha":(9.8950,76.7180),"Munnar":(10.0889,77.0595),"Adimali":(10.0110,76.9560),"Kattappana":(9.7550,77.1140),"Nedumkandam":(9.7930,77.1260),
"Kochi":(9.9312,76.2673),"Aluva":(10.1076,76.3516),"Angamaly":(10.1960,76.3860),"Perumbavoor":(10.1076,76.4730),"Muvattupuzha":(9.9847,76.5790),"Kothamangalam":(10.0580,76.6290),"North Paravur":(10.1480,76.2260),
"Thrissur":(10.5276,76.2144),"Chalakudy":(10.3070,76.3310),"Kodungallur":(10.2220,76.1990),"Irinjalakuda":(10.3420,76.2110),"Guruvayur":(10.5940,76.0410),"Kunnamkulam":(10.6500,76.0820),
"Palakkad":(10.7867,76.6548),"Ottapalam":(10.7720,76.3770),"Shoranur":(10.7590,76.2700),"Chittur":(10.6990,76.7470),"Mannarkkad":(10.9920,76.4610),
"Malappuram":(11.0510,76.0711),"Manjeri":(11.1200,76.1190),"Perinthalmanna":(10.9780,76.2260),"Tirur":(10.9130,75.9220),"Ponnani":(10.7670,75.9250),"Kondotty":(11.1450,75.9600),
"Kozhikode":(11.2588,75.7804),"Vadakara":(11.5940,75.5890),"Koyilandy":(11.4390,75.6950),"Ramanattukara":(11.1830,75.8650),
"Kalpetta":(11.6080,76.0830),"Sulthan Bathery":(11.6630,76.2640),"Mananthavady":(11.8000,76.0010),
"Kannur":(11.8745,75.3704),"Thalassery":(11.7480,75.4890),"Payyannur":(12.1030,75.2020),"Iritty":(11.9810,75.6750),"Mattannur":(11.9300,75.5720),
"Kasaragod":(12.4996,74.9869),"Kanhangad":(12.3080,75.1060),"Nileshwar":(12.2590,75.1350),"Uppala":(12.6710,74.9500)
}
LOCATION_DISTRICTS={
"Thiruvananthapuram":"Thiruvananthapuram","Neyyattinkara":"Thiruvananthapuram","Attingal":"Thiruvananthapuram","Varkala":"Thiruvananthapuram",
"Kollam":"Kollam","Karunagappally":"Kollam","Punalur":"Kollam","Kottarakkara":"Kollam",
"Pathanamthitta":"Pathanamthitta","Adoor":"Pathanamthitta","Thiruvalla":"Pathanamthitta","Ranni":"Pathanamthitta","Konni":"Pathanamthitta",
"Alappuzha":"Alappuzha","Cherthala":"Alappuzha","Kayamkulam":"Alappuzha","Chengannur":"Alappuzha","Mavelikara":"Alappuzha",
"Kottayam":"Kottayam","Changanassery":"Kottayam","Pala":"Kottayam","Ettumanoor":"Kottayam","Vaikom":"Kottayam",
"Painavu":"Idukki","Thodupuzha":"Idukki","Munnar":"Idukki","Adimali":"Idukki","Kattappana":"Idukki","Nedumkandam":"Idukki",
"Kochi":"Ernakulam","Aluva":"Ernakulam","Angamaly":"Ernakulam","Perumbavoor":"Ernakulam","Muvattupuzha":"Ernakulam","Kothamangalam":"Ernakulam","North Paravur":"Ernakulam",
"Thrissur":"Thrissur","Chalakudy":"Thrissur","Kodungallur":"Thrissur","Irinjalakuda":"Thrissur","Guruvayur":"Thrissur","Kunnamkulam":"Thrissur",
"Palakkad":"Palakkad","Ottapalam":"Palakkad","Shoranur":"Palakkad","Chittur":"Palakkad","Mannarkkad":"Palakkad",
"Malappuram":"Malappuram","Manjeri":"Malappuram","Perinthalmanna":"Malappuram","Tirur":"Malappuram","Ponnani":"Malappuram","Kondotty":"Malappuram",
"Kozhikode":"Kozhikode","Vadakara":"Kozhikode","Koyilandy":"Kozhikode","Ramanattukara":"Kozhikode",
"Kalpetta":"Wayanad","Sulthan Bathery":"Wayanad","Mananthavady":"Wayanad",
"Kannur":"Kannur","Thalassery":"Kannur","Payyannur":"Kannur","Iritty":"Kannur","Mattannur":"Kannur",
"Kasaragod":"Kasaragod","Kanhangad":"Kasaragod","Nileshwar":"Kasaragod","Uppala":"Kasaragod"
}

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

def location_options(district="All districts", search=""):
    names=[n for n in LOCATIONS if district=="All districts" or LOCATION_DISTRICTS.get(n)==district]
    search=search.strip().lower()
    if search:
        names=[n for n in names if search in n.lower()]
    return names

def risk_score(d):
    level=min(100,d["water_level"]); flow=min(100,d["inflow"]/20); opening=min(100,d["opening_percent"]*2)
    return int(min(100,round(level*.45+flow*.35+opening*.20)))

def water_level_gauge(level):
    pct=max(0,min(100,level))
    return f'''<div class="hs-gauge"><div class="hs-gauge-fill" style="width:{pct}%;"></div><div class="hs-gauge-marker" style="left:{pct}%"></div></div><div class="hs-gauge-labels"><span>0</span><strong>{level:.1f}</strong><span>100</span></div>'''

def shutter_visual(opened,total):
    blocks=[]
    for i in range(total):
        state="open" if i<opened else "closed"
        blocks.append(f'<span class="shutter {state}"></span>')
    return '<div class="shutter-row">'+''.join(blocks)+'</div>'

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

def release_outlook(d):
    """Public 24–48 h controlled-release outlook.

    This is a prototype indicator using forecast rainfall and current
    reservoir conditions. It does NOT predict an operator's decision.
    Production deployment must use the dam's approved rule curve,
    official gate status, catchment inflow forecasts and authorised data.
    """
    f=forecast(d["lat"],d["lon"])
    if not f["success"]:
        return {"success":False,"error":f["error"]}
    df=f["data"].copy()
    if df.empty:
        return {"success":False,"error":"No forecast data available."}

    start=df["datetime"].min()
    r24=float(df[df["datetime"]<=start+pd.Timedelta(hours=24)]["rainfall"].sum())
    r48=float(df[df["datetime"]<=start+pd.Timedelta(hours=48)]["rainfall"].sum())

    # Use the existing prototype water-level calculation for a transparent
    # public indicator; do not present this as an operational forecast.
    level24=predict_level(d,r24)
    level48=d["water_level"]+(max(0,d["inflow"]-d["outflow"])/1000)*1.5+(r48/100)*4.0

    current_release=d["open_shutters"]>0 or d["outflow"]>0
    heavy24=r24>=50
    heavy48=r48>=80
    elevated=d["risk"] in {"Moderate","High"}

    if d["open_shutters"]>0:
        outlook="Release currently active"
        detail="The prototype data already shows an open shutter state. Continued or adjusted release depends on official reservoir operations."
        flag="ACTIVE"
    elif (heavy24 and elevated) or (heavy48 and elevated):
        outlook="Potential controlled release"
        detail="Forecast rainfall plus the current reservoir condition indicate that controlled release may need to be considered within the next 24–48 hours."
        flag="WATCH"
    elif heavy24 or heavy48:
        outlook="Rainfall-driven watch"
        detail="Forecast rainfall is elevated, but the prototype does not have enough verified dam-operation data to indicate a release."
        flag="WATCH"
    else:
        outlook="No release indication"
        detail="The prototype does not indicate a likely controlled release from the available 24–48 hour rainfall and current reservoir inputs."
        flag="LOW"

    return {
        "success":True,"rain24":round(r24,1),"rain48":round(r48,1),
        "level24":round(level24,2),"level48":round(level48,2),
        "outlook":outlook,"detail":detail,"flag":flag,
        "current_release":current_release
    }


# ============================================================
# HYDRAULIC MODEL — educational prototype
# ============================================================
def saint_venant_2d(dam, breach_fraction=0.55, nx=70, ny=42, steps=90):
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
        h_new=(h_new+np.roll(h_new,1,0)+np.roll(h_new,-1,0)+np.roll(h_new,1,1)+np.roll(h_new,-1,1))/5
        h_new[0,:]=0; h_new[-1,:]=0; h_new[:,-1]=0
        wet=(h_new>0.08)&np.isnan(arrival)
        arrival[wet]=k*dt/60.0
        h,u,v=h_new,u_new,v_new
        peak=max(peak,float(np.max(h*np.sqrt(g*np.maximum(h,0)))))
        depth_peak=np.maximum(depth_peak,h)
    return {"X":X,"Y":Y,"depth":depth_peak,"arrival":arrival,"peak_velocity":float(np.nanmax(np.sqrt(u*u+v*v))),"peak_discharge":peak*1000}

# Prototype downstream corridors. These are illustrative monitoring zones only;
# production HYDROSCOPE must load verified downstream locations from the dam's
# approved Emergency Action Plan (EAP), rule-curve data and GIS layers.
DOWNSTREAM_ZONES={
    "Idukki Dam":["Cheruthoni","Karimban","Vazhathoppe","Lower Periyar corridor"],
    "Idamalayar Dam":["Pooyamkutty corridor","Kothamangalam downstream belt","Periyar low-lying areas"],
    "Malankara Dam":["Thodupuzha downstream corridor","Muvattupuzha river-side areas"],
    "Bhoothathankettu":["Kothamangalam downstream corridor","Periyar river-side areas","Low-lying Periyar settlements"],
    "Pamba Dam":["Ranni downstream corridor","Pampa river-side areas","Chengannur low-lying areas"],
    "Kakki Dam":["Kakki–Pampa downstream corridor","Ranni river-side areas","Pampa basin low-lying areas"],
    "Neyyar Dam":["Neyyattinkara downstream corridor","Neyyar river-side areas","Low-lying Neyyar basin areas"],
    "Banasura Sagar Dam":["Padinjarathara downstream corridor","Panamaram river-side areas","Low-lying Kabini basin areas"]
}

def projected_release(d, scenario_shutters):
    # This is a transparent prototype scaling, not a gate-discharge equation.
    # It estimates relative release pressure from the current demo outflow and
    # the change in number of open shutters.
    current=d["open_shutters"]
    current_open=max(1,current)
    if scenario_shutters==0:
        return 0.0
    if current==0:
        return d["outflow"]*(scenario_shutters/max(1,d["total_shutters"]))
    return d["outflow"]*(scenario_shutters/current)

def public_release_assessment(d, scenario_shutters):
    total=max(1,d["total_shutters"])
    fraction=scenario_shutters/total
    current_fraction=d["open_shutters"]/total
    # Public-facing classification is intentionally conservative and descriptive.
    if scenario_shutters==0:
        level="No gate opening scenario"
    elif fraction <= .25:
        level="Lower release scenario"
    elif fraction <= .50:
        level="Moderate release scenario"
    elif fraction <= .75:
        level="High release scenario"
    else:
        level="Very high release scenario"

    zones=DOWNSTREAM_ZONES.get(d["name"],["Downstream river corridor","Nearby low-lying areas"])
    affected_count=max(1,min(len(zones),1+int(round(fraction*len(zones)))))
    if scenario_shutters <= d["open_shutters"]:
        status="Within or below the current prototype gate-opening state"
    else:
        status="Higher than the current prototype gate-opening state"
    return {
        "level":level,
        "status":status,
        "release":projected_release(d,scenario_shutters),
        "zones":zones[:affected_count],
        "current_fraction":current_fraction
    }

def interactive_dam_visual(dam):
    pct=max(8,min(94,float(dam["water_level"])))
    gates=[]
    total=int(dam.get("total_shutters",4))
    opened=int(dam.get("open_shutters",0))
    for i in range(total):
        gates.append('<span class="hs-gate open"></span>' if i < opened else '<span class="hs-gate"></span>')
    name=dam.get("name","Idukki Dam")
    return f'''<div class="hs-dam-scene">
      <div class="hs-dam-sky"></div><div class="hs-moon"></div>
      <div class="hs-mountain m1"></div><div class="hs-mountain m2"></div>
      <div class="hs-scene-label"><div class="small">Interactive reservoir view</div><div class="big">{name}</div></div>
      <div class="hs-scene-level"><strong>{float(dam["water_level"]):.1f} m</strong><span>current prototype level</span></div>
      <div class="hs-reservoir"><div class="hs-waterline"></div><div class="hs-reservoir-fill" style="height:{pct}%"></div></div>
      <div class="hs-dam-wall"></div><div class="hs-gates">{''.join(gates)}</div>
      <div class="hs-river"></div>
    </div>'''


def hydro_game_scene(step, water, rainfall, safety):
    water_pct=max(10,min(92,int(water)))
    rain_pct=max(12,min(96,int(rainfall/1.7)))
    safety_pct=max(8,min(96,int(safety)))
    gates_open=1 if step>=1 else 0
    if step>=2: gates_open=2
    gates=[]
    for i in range(4):
        gates.append('<span class="hg-gate hg-open"></span>' if i < gates_open else '<span class="hg-gate"></span>')
    houses=''.join('<span class="hg-house"></span>' for _ in range(5))
    return f'''<div class="hg-world">
      <div class="hg-cloud hg-c1"></div><div class="hg-cloud hg-c2"></div><div class="hg-rain" style="opacity:{0.25+rain_pct/140:.2f}"></div>
      <div class="hg-mountain hg-m1"></div><div class="hg-mountain hg-m2"></div>
      <div class="hg-reservoir"><div class="hg-water" style="height:{water_pct}%"></div><div class="hg-wave"></div></div>
      <div class="hg-dam"><div class="hg-dam-top"></div><div class="hg-gates">{''.join(gates)}</div></div>
      <div class="hg-river"><div class="hg-river-flow"></div></div>
      <div class="hg-valley">{houses}</div>
      <div class="hg-overlay">
        <div><span>EVENT</span><strong>{step+1}/3</strong></div>
        <div><span>RAINFALL</span><strong>{rainfall} mm</strong></div>
        <div><span>RESERVOIR</span><strong>{water}%</strong></div>
        <div><span>SAFETY</span><strong>{safety}%</strong></div>
      </div>
    </div>'''


def hydro_guardian_reset():
    st.session_state.game_started=True
    st.session_state.game_over=False
    st.session_state.game_step=0
    st.session_state.game_score=0
    st.session_state.game_safety=55
    st.session_state.game_water=58
    st.session_state.game_message="A monsoon cell is approaching the fictional valley. Start monitoring early."


def hydro_guardian_choice(choice):
    step=st.session_state.game_step
    outcomes=[
        {"monitor":(8,5,"Good monitoring gives the response team more lead time."),"warning":(12,9,"Early public information improves preparedness."),"evacuate":(4,2,"Evacuation information is useful, but the first step is confirming the evolving situation.")},
        {"monitor":(10,4,"The reservoir trend is now being watched closely."),"warning":(11,8,"A targeted warning helps downstream communities prepare."),"evacuate":(7,6,"Preparedness action helps, but broad evacuation should follow verified agency guidance.")},
        {"monitor":(6,3,"Monitoring alone is less effective once downstream risk is rising."),"warning":(13,10,"A clear warning creates valuable response time."),"evacuate":(14,12,"Prompt preparedness can reduce exposure when risk is escalating.")},
    ]
    score,safety,msg=outcomes[min(step,2)][choice]
    st.session_state.game_score=min(100,st.session_state.game_score+score)
    st.session_state.game_safety=min(100,st.session_state.game_safety+safety)
    st.session_state.game_water=min(100,st.session_state.game_water+[12,18,22][min(step,2)])
    st.session_state.game_message=msg
    st.session_state.game_step+=1
    if st.session_state.game_step>=3: st.session_state.game_over=True


def hydro_game_page():
    st.markdown('<div class="hs-section">Hydro Guardian</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    st.markdown('<div class="hs-game"><div class="hs-game-title">PROTECT THE VALLEY</div><div class="hs-game-sub">A short educational mini-game inside HYDROSCOPE. Manage information and preparedness as rainfall increases. This fictional simulation does not control or predict any real dam.</div></div>',unsafe_allow_html=True)
    if "game_started" not in st.session_state: st.session_state.game_started=False
    if not st.session_state.game_started:
        st.markdown(hydro_game_scene(0,58,82,55),unsafe_allow_html=True)
        st.write("")
        st.markdown('<div class="hs-note">Three events. One fictional valley. Rainfall intensifies, the reservoir rises and downstream conditions change. Choose the safest public-response action at each stage.</div>',unsafe_allow_html=True)
        if st.button("Start Hydro Guardian",type="primary",key="start_game",use_container_width=True): hydro_guardian_reset(); st.rerun()
        return
    if st.session_state.get("game_over"):
        a,b,c=st.columns(3)
        a.markdown(f'<div class="hs-game-stat">Safety<strong>{st.session_state.game_safety}%</strong></div>',unsafe_allow_html=True)
        b.markdown(f'<div class="hs-game-stat">Score<strong>{st.session_state.game_score}</strong></div>',unsafe_allow_html=True)
        c.markdown('<div class="hs-game-stat">Result<strong>Mission complete</strong></div>',unsafe_allow_html=True)
        st.write("")
        st.markdown(f'<div class="hs-game-over"><div class="hs-score">{st.session_state.game_score}</div><div>HYDRO GUARDIAN SCORE</div><p>{st.session_state.game_message}</p><p>Key lesson: early information and preparedness can create more time for communities to respond.</p></div>',unsafe_allow_html=True)
        if st.button("Play Again",type="primary",key="restart_game"): hydro_guardian_reset(); st.rerun()
        return
    step=st.session_state.game_step
    rainfall=[82,118,151][min(step,2)]
    level=st.session_state.game_water
    st.markdown(hydro_game_scene(step,level,rainfall,st.session_state.game_safety),unsafe_allow_html=True)
    st.write("")
    a,b,c=st.columns(3)
    a.markdown(f'<div class="hs-game-stat">Rainfall<strong>{rainfall} mm</strong><div class="hs-game-bar"><span style="width:{min(100,rainfall/1.6)}%"></span></div></div>',unsafe_allow_html=True)
    b.markdown(f'<div class="hs-game-stat">Reservoir<strong>{level}%</strong><div class="hs-game-bar"><span style="width:{level}%"></span></div></div>',unsafe_allow_html=True)
    c.markdown(f'<div class="hs-game-stat">Community safety<strong>{st.session_state.game_safety}%</strong><div class="hs-game-bar"><span style="width:{st.session_state.game_safety}%"></span></div></div>',unsafe_allow_html=True)
    st.write("")
    st.markdown(f'<div class="hs-card"><div class="hs-card-label">Event {step+1} of 3</div><div class="hs-card-title">Rainfall is intensifying</div><p class="hs-card-copy">{st.session_state.game_message}</p></div>',unsafe_allow_html=True)
    st.markdown('<div class="hs-section">Choose your response</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    x,y,z=st.columns(3)
    if x.button("Monitor conditions",key=f"gm_{step}_monitor",use_container_width=True): hydro_guardian_choice("monitor"); st.rerun()
    if y.button("Issue public warning",key=f"gm_{step}_warning",use_container_width=True): hydro_guardian_choice("warning"); st.rerun()
    if z.button("Prepare evacuation information",key=f"gm_{step}_evacuate",use_container_width=True): hydro_guardian_choice("evacuate"); st.rerun()
    st.caption("Game scenarios are fictional and educational. Real warnings and evacuation instructions come from authorized agencies.")


def dam_map(location):
    lat,lon=LOCATIONS[location]
    m=folium.Map(location=[lat,lon],zoom_start=8,tiles="OpenStreetMap",control_scale=True)
    folium.Circle([lat,lon],radius=120000,color="#25b9ff",fill=True,fill_opacity=.05).add_to(m)
    folium.Marker([lat,lon],tooltip=location,icon=folium.Icon(color="blue",icon="info-sign")).add_to(m)
    for name,d in DAM_DATABASE.items():
        dist=distance_km(lat,lon,d["lat"],d["lon"])
        if dist>120: continue
        c="red" if d["risk"]=="High" else "orange" if d["risk"]=="Moderate" else "green"
        txt=f"<b>{name}</b><br>Water level: {d['water_level']:.1f}<br>Shutters: {d['open_shutters']}/{d['total_shutters']}<br>Risk: {d['risk']}<br>Distance: {dist:.1f} km"
        folium.Marker([d["lat"],d["lon"]],tooltip=name,popup=folium.Popup(txt,max_width=260),icon=folium.Icon(color=c,icon="tint")).add_to(m)
    return m

# ============================================================
# AUTHORITY ACCESS
# ============================================================
def authority_login():
    st.markdown('<div class="hs-card"><div class="hs-card-label">Restricted area</div><div class="hs-card-title">Authority access</div><p class="hs-card-copy">Enter the registered authority identity and prototype access key to unlock the technical console.</p></div>',unsafe_allow_html=True)
    st.write("")
    identifier=st.text_input("Authority ID / Registered Gmail",placeholder="AUTH-001 or authority@gmail.com")
    access_key=st.text_input("Access Key",type="password",placeholder="Enter access key")
    if st.button("Enter Authority Dashboard",key="authority_enter",type="primary"):
        configured_id=str(st.secrets.get("AUTHORITY_ID","AUTH-001")).strip().lower()
        configured_key=str(st.secrets.get("AUTHORITY_ACCESS_KEY","HYDRO2026"))
        configured_emails=str(st.secrets.get("AUTHORIZED_AUTHORITY_EMAILS","")).lower()
        email_list=[x.strip() for x in configured_emails.split(",") if x.strip()]
        ident=identifier.strip().lower()
        valid_identity=ident==configured_id or ("@" in ident and ident in email_list)
        if "@" in ident and not email_list: valid_identity=ident.endswith("@gmail.com")
        if not identifier.strip() or not access_key:
            st.error("Enter the authority identity and access key.")
        elif valid_identity and access_key==configured_key:
            st.session_state.authority=True
            st.session_state.authority_id=identifier.strip()
            st.session_state.authority_email=identifier.strip().lower() if "@" in ident else "Authority ID verified"
            st.session_state.page="Authority Console"
            st.rerun()
        else:
            st.error("Access denied. Check the registered identity and access key.")
    with st.expander("Prototype access details"):
        st.write("Authority ID: `AUTH-001`")
        st.write("Access key: `HYDRO2026`")
        st.caption("Prototype only. Production deployment should use institutional SSO/OAuth or agency-managed identity verification.")

# ============================================================
# SESSION / HEADER
# ============================================================
if "page" not in st.session_state: st.session_state.page="Home"
if "authority" not in st.session_state: st.session_state.authority=False

st.markdown('<div class="hs-brand"><div class="hs-brand-title"><span>HYDRO</span>SCOPE</div><div class="hs-brand-sub">PUBLIC FLOOD AWARENESS  /  DAM MONITORING  /  PREDICTIVE WATER INTELLIGENCE</div><div class="hs-status"><span class="hs-dot"></span>SYSTEM ONLINE</div></div>',unsafe_allow_html=True)
st.write("")

nav=["Home","Public Dashboard","Hydro Guardian","Authority Access"]
if st.session_state.authority: nav += ["Prediction","Authority Console","Hydraulic Simulation"]
cols=st.columns(len(nav))
for c,name in zip(cols,nav):
    with c:
        if st.button(name,key="nav_"+name): st.session_state.page=name; st.rerun()

st.divider()

# ============================================================
# HOME
# ============================================================
if st.session_state.page=="Home":
    st.markdown('<div class="hs-section">A living view of changing water conditions</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    st.markdown('<div class="hs-note">Explore a water-themed public interface where the reservoir, gates and downstream flow visually respond to the current prototype dam state. Weather is live when the OpenWeather connection is available; dam parameters shown here are prototype data.</div>',unsafe_allow_html=True)
    st.write("")
    home_dam=DAM_DATABASE["Idukki Dam"]
    st.markdown(interactive_dam_visual(home_dam),unsafe_allow_html=True)
    st.write("")
    a,b,c,d=st.columns(4)
    a.metric("Water level",f'{home_dam["water_level"]:.1f} m')
    b.metric("Rainfall input",f'{home_dam["rainfall"]:.0f} mm')
    c.metric("Open shutters",f'{home_dam["open_shutters"]}/{home_dam["total_shutters"]}')
    d.metric("Risk state",home_dam["risk"])
    st.write("")
    a,b,c=st.columns(3)
    with a:
        st.markdown('<div class="hs-card"><div class="hs-card-label">01 / Explore</div><div class="hs-card-title">Inspect nearby dams</div><p class="hs-card-copy">Find monitored prototype dams around a Kerala location and open their 24–48 hour public release outlook.</p></div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="hs-card"><div class="hs-card-label">02 / Understand</div><div class="hs-card-title">Watch the water story</div><p class="hs-card-copy">The reservoir, gates and downstream river are presented as one connected visual story.</p></div>',unsafe_allow_html=True)
    with c:
        st.markdown('<div class="hs-card"><div class="hs-card-label">03 / Learn</div><div class="hs-card-title">Play Hydro Guardian</div><p class="hs-card-copy">Test how early monitoring, public warnings and preparedness affect a fictional flood scenario.</p></div>',unsafe_allow_html=True)
    st.write("")
    x,y=st.columns(2)
    if x.button("Explore Public Dashboard",key="home_public",type="primary"): st.session_state.page="Public Dashboard"; st.rerun()
    if y.button("Play Hydro Guardian",key="home_game"): st.session_state.page="Hydro Guardian"; st.rerun()

# ============================================================
# PUBLIC DASHBOARD
# ============================================================
elif st.session_state.page=="Public Dashboard":
    st.markdown('<div class="hs-section">Public Safety Dashboard</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    st.markdown('<div class="hs-note">Select a location, then inspect a dam to see its current water condition and a prototype 24–48 hour controlled-release outlook based on forecast rainfall and current reservoir inputs.</div>',unsafe_allow_html=True)
    st.write("")

    districts=["All districts"]+list(dict.fromkeys(LOCATION_DISTRICTS.values()))
    c1,c2,c3=st.columns([1.1,1.5,1.0])
    with c1:
        district=st.selectbox("District",districts,key="public_district")
    with c2:
        search=st.text_input("Search location",placeholder="Type a city or town",key="public_search")
    options=location_options(district,search)
    if not options:
        st.warning("No matching location. Clear the search or choose another district.")
        st.stop()
    with c3:
        default_loc=st.session_state.get("public_loc",options[0])
        if default_loc not in options: default_loc=options[0]
        loc=st.selectbox("Monitoring location",options,index=options.index(default_loc),key="public_loc")

    lat,lon=LOCATIONS[loc]
    st.markdown(f'<div class="hs-interactive"><div class="hs-mini">Selected location</div><div class="hs-big">{loc}</div><div class="hs-click">{LOCATION_DISTRICTS[loc]} district  |  {lat:.4f}, {lon:.4f}</div></div>',unsafe_allow_html=True)
    st.write("")
    preview_dams=nearby_dams(loc,120)
    if preview_dams:
        featured=preview_dams[0]
        st.markdown('<div class="hs-section">Living Reservoir View</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
        st.markdown(interactive_dam_visual(featured),unsafe_allow_html=True)
        st.caption(f'Visual focus: {featured["name"]}. The animation is a UI representation of prototype monitoring data, not a physical hydraulic model.')

    w=weather(lat,lon)
    if w["success"]:
        a,b,c,d=st.columns(4)
        a.metric("Temperature",f"{w['temperature']:.1f} °C")
        b.metric("Rainfall now",f"{w['rainfall']:.1f} mm")
        c.metric("Humidity",f"{w['humidity']}%")
        d.metric("Wind",f"{w['wind']:.1f} m/s")
        st.caption("Weather data provided by OpenWeather.")

    radius=st.slider("Monitoring radius",50,200,120,10,key="public_radius")
    dams=nearby_dams(loc,radius)
    st.markdown(f'<div class="hs-section">Nearby Dams <span class="hs-pill">{len(dams)} within {radius} km</span></div><div class="hs-section-line"></div>',unsafe_allow_html=True)

    if dams:
        # The Inspect button is the only public interaction that opens the
        # dam-specific forecast panel. There is no breach slider or release
        # simulation in the public interface.
        if "public_dam_focus_pending" in st.session_state:
            pending=st.session_state.pop("public_dam_focus_pending")
            if any(d["name"]==pending for d in dams):
                st.session_state.public_dam_focus=pending

        dam_names=[d["name"] for d in dams]
        if st.session_state.get("public_dam_focus") not in dam_names:
            st.session_state.public_dam_focus=None

        cards=st.columns(3)
        for i,d in enumerate(dams):
            with cards[i%3]:
                active=st.session_state.get("public_dam_focus")==d["name"]
                border='border:1px solid rgba(58,210,255,.85);box-shadow:0 0 24px rgba(35,185,255,.18);' if active else ''
                st.markdown(f'<div class="hs-card" style="{border}"><span class="hs-pill">{d["risk"]}  /  {d["distance"]:.1f} km</span><div class="hs-card-title" style="margin-top:12px">{d["name"]}</div><div class="hs-card-copy">Water level <b>{d["water_level"]:.1f}</b>  |  Shutters <b>{d["open_shutters"]}/{d["total_shutters"]}</b></div><div class="hs-card-copy">Rainfall input <b>{d["rainfall"]:.0f} mm</b></div></div>',unsafe_allow_html=True)
                if st.button("Inspect",key=f"inspect_{d['name']}",use_container_width=True):
                    st.session_state.public_dam_focus_pending=d["name"]
                    st.rerun()

        selected=st.session_state.get("public_dam_focus")
        if selected in dam_names:
            focus=next(d for d in dams if d["name"]==selected)
            st.markdown('<div class="hs-section">Dam Release Outlook</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
            st.markdown(f'<div class="hs-interactive"><div class="hs-mini">Public inspection</div><div class="hs-big">{focus["name"]}</div><div class="hs-click">Current level {focus["water_level"]:.1f}  |  Current shutters {focus["open_shutters"]}/{focus["total_shutters"]}  |  Distance {focus["distance"]:.1f} km</div></div>',unsafe_allow_html=True)

            outlook=release_outlook(focus)
            if outlook["success"]:
                x,y,z,q=st.columns(4)
                x.metric("24 h forecast rain",f"{outlook['rain24']:.1f} mm")
                y.metric("48 h forecast rain",f"{outlook['rain48']:.1f} mm")
                z.metric("24 h projected level",f"{outlook['level24']:.1f}")
                q.metric("48 h projected level",f"{outlook['level48']:.1f}")

                if outlook["flag"]=="ACTIVE":
                    st.warning(f"{outlook['outlook']}: the prototype data currently shows {focus['open_shutters']} of {focus['total_shutters']} shutters open.")
                elif outlook["flag"]=="WATCH":
                    st.warning(outlook["outlook"]+": review the official dam status and warnings before making safety decisions.")
                else:
                    st.success(outlook["outlook"]+" for the next 24–48 hours based on the prototype inputs.")

                st.markdown(f'<div class="hs-card"><div class="hs-card-label">What this means for the public</div><div class="hs-card-title">{outlook["outlook"]}</div><p class="hs-card-copy">{outlook["detail"]}</p></div>',unsafe_allow_html=True)

                zones=DOWNSTREAM_ZONES.get(focus["name"],["Downstream river corridor","Nearby low-lying areas"])
                st.markdown(f'<div class="hs-card"><div class="hs-card-label">If controlled release occurs</div><div class="hs-card-title">Downstream areas to monitor</div><p class="hs-card-copy">{" • ".join(zones)}</p></div>',unsafe_allow_html=True)
                st.caption("This is a prototype public-awareness indicator. It does not predict an operator's decision or issue an official evacuation warning. Production use should use the dam's approved rule curve, official gate status, catchment forecast and Emergency Action Plan.")
            else:
                st.info(f"Release outlook unavailable: {outlook['error']}")
        else:
            st.markdown('<div class="hs-note">Select Inspect on a dam to open its 24–48 hour public release outlook. Detailed flood-depth, velocity, breach and arrival-time simulation is restricted to authorized users.</div>',unsafe_allow_html=True)
    else:
        st.info("No monitored demo dams are within this radius. The public interface is ready for additional verified reservoir feeds.")

    st.markdown('<div class="hs-section">Kerala Monitoring Map</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    st_folium(dam_map(loc),height=560,width=None,returned_objects=[])
    st.markdown('<div class="hs-note">HYDROSCOPE provides public awareness and safety information. Official warnings and evacuation instructions remain the responsibility of authorized agencies. Demo dam parameters are prototype data.</div>',unsafe_allow_html=True)

# ============================================================
# HYDRO GUARDIAN
# ============================================================
elif st.session_state.page=="Hydro Guardian":
    hydro_game_page()

# ============================================================
# PREDICTION
# ============================================================
elif st.session_state.page=="Prediction":
    if not st.session_state.authority:
        st.session_state.page="Public Dashboard"
        st.rerun()
    st.markdown('<div class="hs-section">Water-Level Prediction</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    name=st.selectbox("Select Dam",list(DAM_DATABASE),key="pred_dam"); dam=DAM_DATABASE[name]
    f=forecast(dam["lat"],dam["lon"])
    if not f["success"]: st.error(f["error"]); st.stop()
    s=rainfall_summary(f["data"])
    a,b,c,d4=st.columns(4)
    a.metric("6h rainfall",f"{s['rain_6h']} mm")
    b.metric("12h rainfall",f"{s['rain_12h']} mm")
    c.metric("24h rainfall",f"{s['rain_24h']} mm")
    d4.metric("Peak 3h",f"{s['peak_3h']} mm")
    fig=go.Figure(go.Bar(x=f["data"]["datetime"],y=f["data"]["rainfall"]))
    fig.update_layout(template="plotly_dark",height=350,title="Forecast Rainfall",xaxis_title="Time",yaxis_title="mm / 3h")
    st.plotly_chart(fig,use_container_width=True)
    pred=predict_level(dam,s["rain_24h"]); prob=release_probability(dam,pred)
    a,b,c=st.columns(3)
    a.metric("Current level",dam["water_level"])
    b.metric("Predicted level",pred)
    c.metric("Release-risk indicator",f"{prob}%")
    st.markdown('<div class="hs-note">Prototype mathematical calculation; not an operational release decision.</div>',unsafe_allow_html=True)

# ============================================================
# AUTHORITY LOGIN
# ============================================================
elif st.session_state.page=="Authority Access":
    if st.session_state.authority:
        st.markdown(f'<div class="hs-note">Verified authority session: <b>{st.session_state.authority_id}</b>  /  {st.session_state.authority_email}</div>',unsafe_allow_html=True)
        if st.button("Sign out",key="signout"):
            st.session_state.authority=False; st.session_state.page="Home"; st.rerun()
    else:
        authority_login()

# ============================================================
# AUTHORITY CONSOLE
# ============================================================
elif st.session_state.page=="Authority Console":
    if not st.session_state.authority:
        st.session_state.page="Authority Access"; st.rerun()
    st.markdown('<div class="hs-section">Authority Console</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    st.markdown(f'<div class="hs-note">Verified session: <b>{st.session_state.authority_id}</b>  /  {st.session_state.authority_email}</div>',unsafe_allow_html=True)
    name=st.selectbox("Dam",list(DAM_DATABASE),key="auth_dam"); dam=DAM_DATABASE[name]
    a,b,c,e=st.columns(4)
    a.metric("Water level",dam["water_level"])
    b.metric("Inflow",f"{dam['inflow']:.0f} m³/s")
    c.metric("Outflow",f"{dam['outflow']:.0f} m³/s")
    e.metric("Open shutters",f"{dam['open_shutters']}/{dam['total_shutters']}")
    st.markdown('<div class="hs-section">Technical risk factors</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    factors=pd.DataFrame({"Factor":["Reservoir level","Inflow","Rainfall","Shutter opening","Net flow"],"Value":[dam["water_level"],dam["inflow"],dam["rainfall"],dam["opening_percent"],max(0,dam["inflow"]-dam["outflow"])],"Unit":["m","m³/s","mm","%","m³/s"]})
    st.dataframe(factors,use_container_width=True,hide_index=True)
    st.markdown('<div class="hs-note">Open the Hydraulic Simulation page for the detailed 2-D scenario model.</div>',unsafe_allow_html=True)

# ============================================================
# AUTHORITY HYDRAULIC SIMULATION
# ============================================================
elif st.session_state.page=="Hydraulic Simulation":
    if not st.session_state.authority:
        st.session_state.page="Authority Access"; st.rerun()
    st.markdown('<div class="hs-section">Authority Hydraulic Simulation</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    st.markdown('<div class="hs-note">Restricted technical scenario analysis. The current solver is an educational prototype and is not an operational flood forecast.</div>',unsafe_allow_html=True)
    name=st.selectbox("Dam",list(DAM_DATABASE),key="hyd_dam"); dam=DAM_DATABASE[name]
    st.markdown('<div class="hs-card"><div class="hs-card-label">Scenario control</div><div class="hs-card-title">Hypothetical breach fraction</div><p class="hs-card-copy">Choose the fraction used by this prototype scenario model.</p></div>',unsafe_allow_html=True)
    breach=st.slider("Breach fraction",0.10,0.90,0.55,0.05,label_visibility="collapsed")
    st.caption(f"Selected scenario: {breach:.0%}")
    if st.button("Run Hydraulic Scenario",type="primary",key="run_hydraulic"):
        with st.spinner("Running hydraulic scenario..."):
            st.session_state.hyd_result=saint_venant_2d(dam,breach_fraction=breach)
    if "hyd_result" in st.session_state:
        r=st.session_state.hyd_result
        a,b,c=st.columns(3)
        a.metric("Peak estimated velocity",f"{r['peak_velocity']:.2f} m/s")
        b.metric("Peak discharge index",f"{r['peak_discharge']:.1f}")
        c.metric("Wet cells",f"{np.sum(r['depth']>.08):,}")
        st.markdown('<div class="hs-section">Maximum Flood Depth</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
        fig=go.Figure(go.Heatmap(x=r["X"][0],y=r["Y"][:,0],z=r["depth"],colorbar_title="Depth (m)"))
        fig.update_layout(template="plotly_dark",height=500,xaxis_title="Downstream distance (m)",yaxis_title="Cross-stream distance (m)")
        st.plotly_chart(fig,use_container_width=True)
        st.markdown('<div class="hs-section">Flood Arrival Time</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
        arr=np.where(np.isnan(r["arrival"]),np.nan,r["arrival"])
        fig2=go.Figure(go.Heatmap(x=r["X"][0],y=r["Y"][:,0],z=arr,colorbar_title="Arrival (min)"))
        fig2.update_layout(template="plotly_dark",height=500,xaxis_title="Downstream distance (m)",yaxis_title="Cross-stream distance (m)")
        st.plotly_chart(fig2,use_container_width=True)
        st.markdown('<div class="hs-note">The governing equations are implemented inside the hydraulic model; they are intentionally not displayed in the dashboard interface. Production deployment requires calibrated terrain, dam geometry, breach hydraulics, roughness, boundary conditions and validation.</div>',unsafe_allow_html=True)

st.divider()
st.markdown('<div class="hs-footer">HYDROSCOPE  ·  Public Flood Awareness  ·  Authorized Technical Analysis<br>Smart India Hackathon Prototype  ·  Kerala</div>',unsafe_allow_html=True)
