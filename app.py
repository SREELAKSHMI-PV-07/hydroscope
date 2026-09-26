import math
import re
from pathlib import Path
from io import StringIO
from urllib.parse import quote

import folium
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import streamlit.components.v1 as components
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
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



/* ------------------------------------------------------------
   HYDROSCOPE UI POLISH LAYER
   ------------------------------------------------------------ */
.hs-brand{min-height:112px;padding:22px 30px;border-radius:26px;background:linear-gradient(120deg,rgba(7,44,61,.96),rgba(3,22,36,.88) 55%,rgba(4,48,65,.90));}
.hs-brand-title{font-size:42px;letter-spacing:7px}
.hs-brand-sub{font-size:10px;letter-spacing:1.8px;margin-top:9px}
.hs-status{right:28px;bottom:24px}
.hs-topbar{display:flex;align-items:center;justify-content:space-between;gap:20px;margin:18px 0 4px;padding:12px 16px;border:1px solid rgba(107,220,255,.13);border-radius:18px;background:rgba(3,25,39,.55);backdrop-filter:blur(14px);}
.hs-topbar-copy{font-size:10px;color:#709daf;text-transform:uppercase;letter-spacing:1.6px;font-weight:800}
.hs-topbar-live{display:flex;align-items:center;gap:8px;font-size:10px;color:#9beaff;text-transform:uppercase;letter-spacing:1.2px;font-weight:900}
.hs-live-line{width:6px;height:6px;border-radius:50%;background:#59e4ff;box-shadow:0 0 15px #59e4ff;animation:livePulse 1.7s ease-in-out infinite}
@keyframes livePulse{0%,100%{opacity:.45;transform:scale(.8)}50%{opacity:1;transform:scale(1.15)}}
div.stButton>button[kind="primary"]{background:linear-gradient(135deg,#0d779a,#19b8df)!important;border-color:rgba(143,241,255,.7)!important;color:#021c28!important;box-shadow:0 10px 30px rgba(30,196,238,.25),inset 0 1px rgba(255,255,255,.28)!important;}
div.stButton>button[kind="primary"]:hover{box-shadow:0 15px 35px rgba(30,196,238,.35)!important;}
.hs-hero{position:relative;min-height:310px;padding:34px 38px;margin-top:18px;border-radius:30px;border:1px solid rgba(101,220,255,.22);overflow:hidden;background:radial-gradient(circle at 82% 35%,rgba(41,211,255,.14),transparent 26%),linear-gradient(120deg,rgba(7,45,61,.97),rgba(3,25,40,.93) 58%,rgba(5,42,57,.88));box-shadow:0 28px 70px rgba(0,0,0,.28),inset 0 1px rgba(255,255,255,.05);}
.hs-hero:before{content:"";position:absolute;left:-10%;right:-10%;bottom:-64px;height:145px;background:repeating-linear-gradient(-5deg,rgba(75,220,255,.10) 0 2px,transparent 2px 24px);transform:skewY(-2deg);animation:heroWater 7s linear infinite;}
@keyframes heroWater{from{background-position:0 0}to{background-position:180px 0}}
.hs-hero-copywrap{position:relative;z-index:3;max-width:600px}
.hs-kicker{display:inline-flex;align-items:center;gap:8px;color:#76dfff;font-size:10px;text-transform:uppercase;letter-spacing:2px;font-weight:900;padding:7px 11px;border:1px solid rgba(95,221,255,.22);border-radius:999px;background:rgba(20,157,199,.08)}
.hs-kicker:before{content:"";width:6px;height:6px;border-radius:50%;background:#64e5ff;box-shadow:0 0 12px #64e5ff}
.hs-hero-title{font-size:clamp(32px,4.2vw,57px);line-height:1.02;font-weight:950;letter-spacing:-1.8px;margin-top:20px;max-width:650px}
.hs-hero-title span{color:#62ddff}
.hs-hero-copy{color:#9ac7d6;font-size:14px;line-height:1.7;max-width:590px;margin-top:16px}
.hs-hero-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:23px}
.hs-action{display:inline-block;padding:10px 15px;border-radius:13px;border:1px solid rgba(104,220,255,.20);background:rgba(6,48,65,.72);color:#dff9ff;font-size:11px;font-weight:850;letter-spacing:.6px}
.hs-hero-orbit{position:absolute;right:-70px;top:-80px;width:430px;height:430px;border-radius:50%;border:1px solid rgba(88,222,255,.13);box-shadow:0 0 0 28px rgba(88,222,255,.025),0 0 0 58px rgba(88,222,255,.018)}
.hs-hero-orbit:after{content:"";position:absolute;left:50%;top:50%;width:115px;height:115px;transform:translate(-50%,-50%);border-radius:50%;background:radial-gradient(circle,rgba(87,226,255,.23),rgba(6,62,82,.03) 68%,transparent 70%);box-shadow:0 0 50px rgba(52,213,255,.16)}
.hs-command{display:grid;grid-template-columns:1.15fr .85fr;gap:14px;margin-top:18px}
.hs-command-panel{padding:21px 23px;border-radius:22px;border:1px solid rgba(102,220,255,.16);background:linear-gradient(145deg,rgba(8,50,67,.84),rgba(3,25,39,.88));box-shadow:10px 18px 35px rgba(0,0,0,.18)}
.hs-command-label{font-size:9px;text-transform:uppercase;letter-spacing:1.8px;color:#6faabd;font-weight:900}
.hs-command-value{font-size:23px;font-weight:950;margin-top:6px}
.hs-command-copy{font-size:12px;color:#8fbaca;line-height:1.55;margin-top:5px}
.hs-signal{height:7px;border-radius:99px;background:rgba(255,255,255,.06);overflow:hidden;margin-top:13px}
.hs-signal span{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#168bb2,#67e4ff);box-shadow:0 0 16px rgba(70,220,255,.35)}
.hs-section{margin-top:36px}
.hs-section-line{margin-bottom:17px}
.hs-note{background:linear-gradient(120deg,rgba(7,48,64,.72),rgba(3,29,43,.62));backdrop-filter:blur(12px)}
.hs-card{min-height:165px}
.hs-dashboard-head{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-top:10px}
.hs-dashboard-title{font-size:34px;font-weight:950;letter-spacing:-.7px}
.hs-dashboard-sub{color:#83b4c5;font-size:13px;margin-top:5px}
.hs-location-badge{padding:9px 13px;border-radius:13px;border:1px solid rgba(96,220,255,.19);background:rgba(9,54,71,.62);color:#b9edfa;font-size:11px;font-weight:850;white-space:nowrap}
@media(max-width:900px){.hs-brand-title{font-size:34px}.hs-brand-sub{max-width:72%;line-height:1.5}.hs-status{display:none}.hs-hero{padding:25px 23px;min-height:350px}.hs-hero-orbit{right:-180px;top:90px;opacity:.65}.hs-command{grid-template-columns:1fr}.hs-dashboard-head{align-items:flex-start;flex-direction:column}.hs-location-badge{white-space:normal}}
@media(max-width:600px){.block-container{padding:.8rem .8rem 3rem}.hs-brand{padding:20px 19px;border-radius:22px}.hs-brand-title{font-size:29px;letter-spacing:4px}.hs-brand-sub{font-size:8px;letter-spacing:1.1px;max-width:100%}.hs-topbar{padding:10px 12px}.hs-topbar-copy{font-size:8px}.hs-topbar-live{font-size:8px}.hs-hero{border-radius:23px;padding:23px 19px}.hs-hero-title{font-size:35px}.hs-hero-copy{font-size:12px}.hs-hero-orbit{width:290px;height:290px;right:-145px;top:150px}.hs-dam-scene{height:300px;border-radius:22px}.hs-game{padding:15px;border-radius:22px}.hs-game-title{font-size:28px}.hs-dashboard-title{font-size:28px}div[data-testid="stMetric"]{min-height:94px;padding:13px}}

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
# ============================================================
# HYDROSCOPE DAM DATA
# ============================================================
# The entries below are the prototype hydraulic/forecast records currently connected.
# Their operating figures are demo values and are NOT live KSEB measurements.
DAM_DATABASE={
"Idukki Dam":{"district":"Idukki","lat":9.8494,"lon":76.9726,"water_level":88.0,"inflow":1800.0,"outflow":600.0,"rainfall":72.0,"total_shutters":8,"open_shutters":2,"opening_percent":20,"risk":"Moderate","status":"PROTOTYPE"},
"Idamalayar Dam":{"district":"Ernakulam","lat":10.2068,"lon":76.7032,"water_level":72.0,"inflow":920.0,"outflow":310.0,"rainfall":48.0,"total_shutters":4,"open_shutters":1,"opening_percent":15,"risk":"Normal","status":"PROTOTYPE"},
"Malankara Dam":{"district":"Idukki","lat":9.7804,"lon":76.8787,"water_level":67.0,"inflow":210.0,"outflow":95.0,"rainfall":41.0,"total_shutters":6,"open_shutters":1,"opening_percent":10,"risk":"Normal","status":"PROTOTYPE"},
"Bhoothathankettu":{"district":"Ernakulam","lat":10.1457,"lon":76.6788,"water_level":61.0,"inflow":160.0,"outflow":80.0,"rainfall":36.0,"total_shutters":5,"open_shutters":1,"opening_percent":10,"risk":"Normal","status":"PROTOTYPE"},
"Pamba Dam":{"district":"Pathanamthitta","lat":9.3805,"lon":76.9275,"water_level":64.0,"inflow":450.0,"outflow":170.0,"rainfall":39.0,"total_shutters":6,"open_shutters":1,"opening_percent":12,"risk":"Normal","status":"PROTOTYPE"},
"Kakki Dam":{"district":"Pathanamthitta","lat":9.35,"lon":77.0,"water_level":70.0,"inflow":520.0,"outflow":190.0,"rainfall":44.0,"total_shutters":4,"open_shutters":1,"opening_percent":15,"risk":"Normal","status":"PROTOTYPE"},
"Neyyar Dam":{"district":"Thiruvananthapuram","lat":8.535,"lon":77.145,"water_level":58.0,"inflow":190.0,"outflow":75.0,"rainfall":31.0,"total_shutters":4,"open_shutters":0,"opening_percent":0,"risk":"Normal","status":"PROTOTYPE"},
"Banasura Sagar Dam":{"district":"Wayanad","lat":11.7,"lon":75.95,"water_level":63.0,"inflow":330.0,"outflow":120.0,"rainfall":52.0,"total_shutters":4,"open_shutters":1,"opening_percent":10,"risk":"Normal","status":"PROTOTYPE"}
}

# ============================================================
# KERALA DAM REGISTRY — AUTHORITY REFERENCE
# ============================================================
# Scope: the 61 operational large-dam entries corresponding to the Kerala
# section of the CWC/NRLD register used for this prototype, with the older
# Attapady under-construction entry excluded, plus two additional major
# state-listed reservoirs (Banasura Sagar and Bhoothathankettu).
# Registry metadata is for identification/reference. It is NOT a live feed.
KERALA_DAM_REGISTRY={
    "Kundala Dam":{"district":"Idukki","operator":"KSEB","year":1947,"river":"Mudirapuzha","lat":10.10,"lon":77.18},
    "Sengulam Dam":{"district":"Idukki","operator":"KSEB","year":1957,"river":"Mudirapuzha","lat":10.00,"lon":77.04},
    "Malampuzha Dam":{"district":"Palakkad","operator":"Kerala Irrigation Department","year":1955,"river":"Bharathapuzha","lat":10.83,"lon":76.69},
    "Walayar Dam":{"district":"Palakkad","operator":"Kerala Irrigation Department","year":1956,"river":"Bharathapuzha","lat":10.75,"lon":76.78},
    "Mattupetty Dam":{"district":"Idukki","operator":"KSEB","year":1956,"river":"Mudirapuzha","lat":10.11,"lon":77.13},
    "Poringalkuthu Dam":{"district":"Thrissur","operator":"KSEB","year":1957,"river":"Chalakudy","lat":10.37,"lon":76.62},
    "Vazhani Dam":{"district":"Thrissur","operator":"Kerala Irrigation Department","year":1957,"river":"Kechery","lat":10.65,"lon":76.33},
    "Peechi Dam":{"district":"Thrissur","operator":"Kerala Irrigation Department","year":1958,"river":"Karuvannur","lat":10.53,"lon":76.34},
    "Neyyar Dam":{"district":"Thiruvananthapuram","operator":"Kerala Irrigation Department","year":1959,"river":"Neyyar","lat":8.535,"lon":77.145},
    "Meenkara Dam":{"district":"Palakkad","operator":"Kerala Irrigation Department","year":1960,"river":"Gayathri","lat":10.63,"lon":76.79},
    "Kallarkutty Dam":{"district":"Idukki","operator":"KSEB","year":1961,"river":"Mudirapuzha","lat":10.00,"lon":77.02},
    "Ponmudi Dam":{"district":"Idukki","operator":"KSEB","year":1965,"river":"Panniar","lat":9.98,"lon":77.06},
    "Periyar Valley Barrage":{"district":"Ernakulam","operator":"Kerala Irrigation Department","year":1964,"river":"Periyar","lat":10.14,"lon":76.67},
    "Anayirankal Dam":{"district":"Idukki","operator":"KSEB","year":1965,"river":"Panniar","lat":10.03,"lon":77.15},
    "Sholayar Flanking Dam":{"district":"Thrissur","operator":"KSEB","year":1965,"river":"Chalakudy","lat":10.36,"lon":76.75},
    "Sholayar Main Dam":{"district":"Thrissur","operator":"KSEB","year":1965,"river":"Chalakudy","lat":10.36,"lon":76.75},
    "Sholayar Saddle Dam":{"district":"Thrissur","operator":"KSEB","year":1965,"river":"Chalakudy","lat":10.36,"lon":76.75},
    "Chulliyar Dam":{"district":"Palakkad","operator":"Kerala Irrigation Department","year":1966,"river":"Gayathri","lat":10.60,"lon":76.60},
    "Kakki Dam":{"district":"Pathanamthitta","operator":"KSEB","year":1966,"river":"Pamba","lat":9.35,"lon":77.26},
    "Mangalam Dam":{"district":"Palakkad","operator":"Kerala Irrigation Department","year":1966,"river":"Bharathapuzha","lat":10.53,"lon":76.45},
    "Anathode Dam":{"district":"Pathanamthitta","operator":"KSEB","year":1967,"river":"Pamba","lat":9.34,"lon":77.22},
    "Pamba Dam":{"district":"Pathanamthitta","operator":"KSEB","year":1967,"river":"Pamba","lat":9.39,"lon":76.95},
    "Pothundy Dam":{"district":"Palakkad","operator":"Kerala Irrigation Department","year":1967,"river":"Ayalur","lat":10.58,"lon":76.70},
    "Aruvikkara Dam":{"district":"Thiruvananthapuram","operator":"Kerala Water Authority","year":1972,"river":"Karamana","lat":8.57,"lon":77.02},
    "Kuttiyadi HE Project Dam":{"district":"Kozhikode","operator":"KSEB","year":1972,"river":"Kuttiyadi","lat":11.54,"lon":75.84},
    "Kuttiyadi Irrigation Project Dam":{"district":"Kozhikode","operator":"Kerala Irrigation Department","year":1973,"river":"Kuttiyadi","lat":11.61,"lon":75.82},
    "Idukki Dam":{"district":"Idukki","operator":"KSEB","year":1975,"river":"Periyar","lat":9.8494,"lon":76.9726},
    "Cheruthoni Dam":{"district":"Idukki","operator":"KSEB","year":1976,"river":"Periyar","lat":9.8453,"lon":76.9653},
    "Maniyar Dam":{"district":"Pathanamthitta","operator":"Kerala Irrigation Department","year":1976,"river":"Pamba","lat":9.36,"lon":76.84},
    "Kulamavu Dam":{"district":"Idukki","operator":"KSEB","year":1977,"river":"Periyar","lat":9.81,"lon":76.90},
    "Pazhassi Dam":{"district":"Kannur","operator":"Kerala Irrigation Department","year":1978,"river":"Valapattanam","lat":11.98,"lon":75.62},
    "Upper Moozhiyar Dam":{"district":"Pathanamthitta","operator":"KSEB","year":1979,"river":"Pamba","lat":9.30,"lon":77.07},
    "Kanjirappuzha Dam":{"district":"Palakkad","operator":"Kerala Irrigation Department","year":1983,"river":"Bharathapuzha","lat":10.98,"lon":76.55},
    "Peppara Dam":{"district":"Thiruvananthapuram","operator":"Kerala Water Authority","year":1983,"river":"Karamana","lat":8.70,"lon":77.15},
    "Siruvani Dam":{"district":"Palakkad","operator":"Kerala Irrigation Department","year":1984,"river":"Siruvani","lat":10.9767,"lon":76.6417},
    "Idamalayar Dam":{"district":"Ernakulam","operator":"KSEB","year":1987,"river":"Periyar","lat":10.2068,"lon":76.7032},
    "Kallada Dam (Parappar)":{"district":"Kollam","operator":"Kerala Irrigation Department","year":1986,"river":"Kallada","lat":8.96,"lon":77.06},
    "Erattayar Dam":{"district":"Idukki","operator":"KSEB","year":1991,"river":"Periyar","lat":9.72,"lon":77.08},
    "Gavi Dam (SA Diversion)":{"district":"Pathanamthitta","operator":"KSEB","year":1989,"river":"Gaviar","lat":9.43,"lon":77.03},
    "Kullar Dam":{"district":"Pathanamthitta","operator":"KSEB","year":1990,"river":"Pamba","lat":9.43,"lon":77.03},
    "Moozhiyar Dam":{"district":"Pathanamthitta","operator":"KSEB","year":1990,"river":"Pamba","lat":9.36,"lon":76.95},
    "Veluthode Dam":{"district":"Pathanamthitta","operator":"KSEB","year":1990,"river":"Pamba","lat":9.32,"lon":76.98},
    "Kosani Saddle Dam":{"district":"Wayanad","operator":"KSEB","year":1991,"river":"Kabani","lat":11.61,"lon":75.95},
    "Kuttiyadi Augmentation Main Dam":{"district":"Wayanad","operator":"KSEB","year":2004,"river":"Kabani","lat":11.67,"lon":75.96},
    "Meenar I Dam":{"district":"Pathanamthitta","operator":"KSEB","year":1991,"river":"Pamba","lat":9.42,"lon":77.08},
    "Meenar II Dam":{"district":"Pathanamthitta","operator":"KSEB","year":1991,"river":"Pamba","lat":9.42,"lon":77.08},
    "Kuttiyadi Saddle Dam":{"district":"Wayanad","operator":"KSEB","year":1992,"river":"Kabani","lat":11.61,"lon":75.95},
    "Malankara Dam":{"district":"Idukki","operator":"Kerala Irrigation Department","year":1994,"river":"Muvattupuzha","lat":9.91,"lon":76.71},
    "Chimmini Dam":{"district":"Thrissur","operator":"Kerala Irrigation Department","year":1996,"river":"Karuvannur","lat":10.43,"lon":76.46},
    "Pambla Dam (Lower Periyar)":{"district":"Idukki","operator":"KSEB","year":1997,"river":"Periyar","lat":10.06,"lon":76.68},
    "Karapuzha Dam":{"district":"Wayanad","operator":"Kerala Irrigation Department","year":2004,"river":"Karapuzha","lat":11.62,"lon":76.10},
    "Mullaperiyar Dam":{"district":"Idukki","operator":"WRD, Tamil Nadu","year":1895,"river":"Periyar","lat":9.5286,"lon":77.1442},
    "Thunakkadavu Dam":{"district":"Palakkad","operator":"WRD, Tamil Nadu","year":1965,"river":"Chalakudy","lat":10.4344,"lon":76.7820},
    "Parambikulam Dam":{"district":"Palakkad","operator":"WRD, Tamil Nadu","year":1967,"river":"Chalakudy","lat":10.3875,"lon":76.7692},
    "Peruvarippallam Dam":{"district":"Palakkad","operator":"WRD, Tamil Nadu","year":1971,"river":"Chalakudy","lat":10.4475,"lon":76.7667},
    "Kotagiri Saddle Dam":{"district":"Wayanad","operator":"KSEB","year":1992,"river":"Kabani","lat":11.6147,"lon":75.9161},
    "Near Kottagiri Saddle Dam":{"district":"Wayanad","operator":"KSEB","year":1992,"river":"Kabani","lat":11.6122,"lon":75.9167},
    "Kuttiyadi Augmentation Spillway Dam":{"district":"Wayanad","operator":"KSEB","year":2004,"river":"Kabani","lat":11.6728,"lon":75.9558},
    "Kallar Dam":{"district":"Idukki","operator":"KSEB","year":1989,"river":"Periyar","lat":10.1083,"lon":77.0670},
    "Ranni Perinad Dam":{"district":"Pathanamthitta","operator":"KSEB","year":2005,"river":"Kallar","lat":9.35,"lon":76.87},
    "Kulamavu Saddle Dam":{"district":"Idukki","operator":"KSEB","year":1977,"river":"Periyar","lat":9.80,"lon":76.90},
    # Major state-listed reservoirs that are also present in current Kerala
    # public dam/reservoir sources but were not represented in the older NRLD
    # subset used above.
    "Banasura Sagar Dam":{"district":"Wayanad","operator":"KSEB","year":1979,"river":"Karamanthodu/Kabini system","lat":11.70,"lon":75.95},
    "Bhoothathankettu Dam":{"district":"Ernakulam","operator":"Kerala Irrigation Department","year":1962,"river":"Periyar","lat":10.15,"lon":76.68},
}

# Full authority-facing dam options. This registry is broader than the 8
# demo reservoirs used by the public live-style dashboard.
AUTHORITY_DAM_OPTIONS=sorted(KERALA_DAM_REGISTRY.keys())

# ============================================================
# KSEB / KSDMA DATA INGESTION
# ============================================================
# The current prototype uses published reservoir observations rather than
# inventing operating values whenever a public source is available. Direct
# KSEB access is attempted first. A public mirror that documents the source
# bulletin is used as a fallback for the prototype.
KSEB_STATISTICS_URL="https://dams.kseb.in/?page_id=45"
KSEB_MIRROR_LIVE_URL="https://raw.githubusercontent.com/amith-vp/Kerala-Dam-Water-Levels/refs/heads/main/live.json"
KSEB_MIRROR_HISTORY_BASE="https://raw.githubusercontent.com/amith-vp/Kerala-Dam-Water-Levels/refs/heads/main/historic_data/"
IRRIGATION_MIRROR_LIVE_URL="https://raw.githubusercontent.com/amith-vp/Kerala-Dam-Water-Levels/refs/heads/main/irrigation_live.json"

KSEB_NAME_TO_REGISTRY={
    "Idukki":"Idukki Dam",
    "Idamalayar":"Idamalayar Dam",
    "Anathode":"Anathode Dam",
    "Banasura Sagar":"Banasura Sagar Dam",
    "Sholayar":"Sholayar Main Dam",
    "Mattupetty":"Mattupetty Dam",
    "Anayirankal":"Anayirankal Dam",
    "Ponmudi":"Ponmudi Dam",
    "Kakkayam":"Kuttiyadi HE Project Dam",
    "Pamba":"Pamba Dam",
    "Poringalkuthu":"Poringalkuthu Dam",
    "Kundala":"Kundala Dam",
    "Kallarkutty":"Kallarkutty Dam",
    "Erattayar":"Erattayar Dam",
    "Pambla":"Pambla Dam (Lower Periyar)",
    "Moozhiyar":"Moozhiyar Dam",
    "Kallar":"Kallar Dam",
    "Chenkulam":"Sengulam Dam",
}

KSEB_OFFICIAL_TO_REGISTRY={
    "IDUKKI":"Idukki Dam",
    "IDAMALAYAR":"Idamalayar Dam",
    "KAKKI – ANATHODE":"Anathode Dam",
    "BANASURASAGAR (K A S)":"Banasura Sagar Dam",
    "SHOLAYAR":"Sholayar Main Dam",
    "MADUPETTY":"Mattupetty Dam",
    "ANAYIRANKAL":"Anayirankal Dam",
    "PONMUDI":"Ponmudi Dam",
    "KUTTIYADI (KAKKAYAM)":"Kuttiyadi HE Project Dam",
    "PAMBA":"Pamba Dam",
    "PORINGALKUTHU":"Poringalkuthu Dam",
    "KUNDALA":"Kundala Dam",
    "KALLARKUTTY":"Kallarkutty Dam",
    "ERATTAYAR":"Erattayar Dam",
    "LOWER PERIYAR":"Pambla Dam (Lower Periyar)",
    "MOOZHIYAR":"Moozhiyar Dam",
    "KALLAR":"Kallar Dam",
    "SENGULAM":"Sengulam Dam",
}

IRRIGATION_NAME_TO_REGISTRY={
    "Bhoothathankettu (Barrage)":"Bhoothathankettu Dam",
    "Chimoni":"Chimmini Dam",
    "Chulliyar":"Chulliyar Dam",
    "Kallada":"Kallada Dam (Parappar)",
    "Kanjirappuzha":"Kanjirappuzha Dam",
    "Karapuzha":"Karapuzha Dam",
    "Kuttiyadi":"Kuttiyadi Irrigation Project Dam",
    "Malampuzha":"Malampuzha Dam",
    "Malankara":"Malankara Dam",
    "Mangalam":"Mangalam Dam",
    "Maniyar (Barrage)":"Maniyar Dam",
    "Meenkara":"Meenkara Dam",
    "Neyyar":"Neyyar Dam",
    "Pazhassi (Barrage)":"Pazhassi Dam",
    "Peechi":"Peechi Dam",
    "Pothundy":"Pothundy Dam",
    "Siruvani (Inter state waters)":"Siruvani Dam",
    "Vazhani":"Vazhani Dam",
    "Walayar":"Walayar Dam",
}

def _norm_name(value):
    return re.sub(r"[^a-z0-9]+","",str(value).lower())

def _number(value):
    if value is None:
        return float("nan")
    text=str(value).strip().replace("—","-").replace("–","-")
    if not text or text in {"-","--","nan","None"}:
        return float("nan")
    m=re.search(r"-?\d+(?:\.\d+)?",text.replace(",",""))
    return float(m.group()) if m else float("nan")

def _level_m(value, force_feet=False):
    if value is None:
        return float("nan")
    text=str(value).strip().lower()
    num=_number(text)
    if not np.isfinite(num):
        return float("nan")
    if "ft" in text or force_feet:
        return num*0.3048
    return num

def _mcm_day_to_cumecs(value):
    num=_number(value)
    if not np.isfinite(num):
        return float("nan")
    return num*1_000_000/86400.0

def _risk_from_alerts(water, blue, orange, red):
    vals=[_level_m(water),_level_m(blue),_level_m(orange),_level_m(red)]
    w,b,o,r=vals
    if np.isfinite(r) and np.isfinite(w) and w>=r:
        return "High"
    if np.isfinite(o) and np.isfinite(w) and w>=o:
        return "Moderate"
    if np.isfinite(b) and np.isfinite(w) and w>=b:
        return "Watch"
    return "Normal"

def _clean_current_record(raw, registry_name, source_type, source_url):
    official=str(raw.get("officialName",raw.get("name",registry_name)))
    is_ft=_norm_name(official) in {_norm_name("IDUKKI"),_norm_name("SHOLAYAR")}
    data=raw.get("data") or []
    row=data[0] if data else {}
    frl=_level_m(raw.get("FRL"),force_feet=is_ft)
    water=_level_m(row.get("waterLevel"),force_feet=is_ft)
    blue=_level_m(raw.get("blueLevel"),force_feet=is_ft)
    orange=_level_m(raw.get("orangeLevel"),force_feet=is_ft)
    red=_level_m(raw.get("redLevel"),force_feet=is_ft)
    avg_inflow=_number(row.get("averageInflow"))
    if not np.isfinite(avg_inflow):
        avg_inflow=_mcm_day_to_cumecs(row.get("inflow"))
    total_outflow=_mcm_day_to_cumecs(row.get("totalOutflow"))
    spill_release=_number(row.get("spillwayRelease"))
    if not np.isfinite(total_outflow) and np.isfinite(spill_release):
        total_outflow=spill_release
    rainfall=_number(row.get("rainfall"))
    storage_pct=_number(row.get("storagePercentage"))
    live_storage=_number(row.get("liveStorage"))
    return {
        "name":registry_name,
        "registry_name":registry_name,
        "official_name":official,
        "water_level":water,
        "frl":frl,
        "rule_level":_level_m(raw.get("ruleLevel"),force_feet=is_ft),
        "blue_level":blue,"orange_level":orange,"red_level":red,
        "live_storage":live_storage,"storage_pct":storage_pct,
        "inflow":avg_inflow,"outflow":total_outflow,
        "spillway_release":spill_release,"rainfall":rainfall,
        "total_shutters":0,"open_shutters":0,"opening_percent":0,
        "shutter_status":"Not published in source dataset",
        "risk":_risk_from_alerts(water,blue,orange,red),
        "status":source_type,
        "data_available":bool(np.isfinite(water)),
        "observed_at":row.get("date",raw.get("lastUpdate","")),
        "data_source":source_type,
        "source_url":source_url,
        "level_pct_of_frl":(water/frl*100 if np.isfinite(water) and np.isfinite(frl) and frl>0 else float("nan")),
        "mirror_name":raw.get("name","")
    }

@st.cache_data(ttl=1800,show_spinner=False)
def fetch_kseb_published_data():
    """Fetch the newest KSEB daily table, then fall back to the public mirror."""
    records={}
    # Direct KSEB daily page listing.
    try:
        r=requests.get(KSEB_STATISTICS_URL,timeout=8)
        r.raise_for_status()
        from bs4 import BeautifulSoup
        soup=BeautifulSoup(r.text,"html.parser")
        links=[]
        for a in soup.select(".elementor-post__title a, a"):
            txt=re.sub(r"\s+"," ",a.get_text(" ",strip=True))
            href=a.get("href")
            if href and re.search(r"\d{1,2}\.\d{1,2}\.\d{4}|\d{1,2}/\d{1,2}/\d{4}",txt):
                links.append((txt,href))
        if links:
            date_text, daily_url=links[0]
            daily=requests.get(daily_url,timeout=8)
            daily.raise_for_status()
            tables=pd.read_html(StringIO(daily.text))
            table=None
            for t in tables:
                if t.shape[1]>=18 and any("reservoir" in str(c).lower() or "dam" in str(c).lower() for c in t.columns):
                    table=t
                    break
            if table is None and tables:
                table=max(tables,key=lambda t:t.shape[1])
            if table is not None and table.shape[1]>=18:
                for _,row in table.iloc[:,:19].iterrows():
                    official=str(row.iloc[1]).strip()
                    display=KSEB_OFFICIAL_TO_REGISTRY.get(official.upper())
                    if display is None:
                        norm=_norm_name(official)
                        display=next((v for k,v in {**KSEB_NAME_TO_REGISTRY,**KSEB_OFFICIAL_TO_REGISTRY}.items() if _norm_name(k)==norm or _norm_name(v)==norm),None)
                    if display is None:
                        continue
                    raw={
                        "name":display,"officialName":official,
                        "FRL":row.iloc[3],"ruleLevel":row.iloc[4],
                        "blueLevel":row.iloc[6],"orangeLevel":row.iloc[7],"redLevel":row.iloc[8],
                        "data":[{
                            "date":date_text,"waterLevel":row.iloc[5],
                            "liveStorage":row.iloc[9],"storagePercentage":row.iloc[10],
                            "inflow":row.iloc[11],"averageInflow":row.iloc[12],
                            "powerHouseDischarge":row.iloc[13],"spillwayRelease":row.iloc[15],
                            "totalOutflow":row.iloc[16],"rainfall":row.iloc[17]
                        }]
                    }
                    records[display]=_clean_current_record(raw,display,"KSEB PUBLISHED","KSEB: "+daily_url)
    except Exception:
        records={}

    # Public mirror fallback / supplementary records.
    try:
        mr=requests.get(KSEB_MIRROR_LIVE_URL,timeout=8)
        mr.raise_for_status()
        payload=mr.json()
        for raw in payload.get("dams",[]):
            display=KSEB_NAME_TO_REGISTRY.get(raw.get("name"))
            if not display:
                official_norm=_norm_name(raw.get("officialName",raw.get("name","")))
                display=next((v for k,v in KSEB_NAME_TO_REGISTRY.items() if _norm_name(k)==official_norm),None)
            if display and display not in records:
                records[display]=_clean_current_record(raw,display,"KSEB PUBLISHED (MIRROR FALLBACK)",raw.get("sourceUrl",KSEB_MIRROR_LIVE_URL))
    except Exception:
        pass
    return records

@st.cache_data(ttl=1800,show_spinner=False)
def fetch_irrigation_published_data():
    records={}
    try:
        r=requests.get(IRRIGATION_MIRROR_LIVE_URL,timeout=8)
        r.raise_for_status()
        payload=r.json()
        for raw in payload.get("dams",[]):
            display=IRRIGATION_NAME_TO_REGISTRY.get(raw.get("name"))
            if display:
                records[display]=_clean_current_record(raw,display,"IRRIGATION PUBLISHED (MIRROR)",payload.get("sourceUrl",IRRIGATION_MIRROR_LIVE_URL))
    except Exception:
        pass
    return records

def _published_record(name):
    rec=fetch_kseb_published_data().get(name)
    if rec:
        return rec
    return fetch_irrigation_published_data().get(name)

def _demo_record(name,meta):
    base=DAM_DATABASE.get(name)
    if not base:
        return None
    rec=base.copy()
    rec.update({"district":meta["district"],"operator":meta["operator"],"construction_year":meta["year"],"river":meta["river"],"data_available":True,"data_source":"LEGACY PROTOTYPE DATA","observed_at":"Prototype","level_pct_of_frl":float("nan")})
    return rec

def authority_dam_record(name):
    """Return registry metadata plus published operational data when available."""
    meta=KERALA_DAM_REGISTRY[name]
    published=_published_record(name)
    demo=_demo_record(name,meta)
    if published:
        rec=published.copy()
        rec.update({"district":meta["district"],"operator":meta["operator"],"construction_year":meta["year"],"river":meta["river"],"lat":meta["lat"],"lon":meta["lon"]})
        return rec
    if demo:
        demo.update({"lat":meta["lat"],"lon":meta["lon"]})
        return demo
    return {
        "name":name,"district":meta["district"],"operator":meta["operator"],
        "construction_year":meta["year"],"river":meta["river"],
        "lat":meta["lat"],"lon":meta["lon"],
        "water_level":float("nan"),"frl":float("nan"),"rule_level":float("nan"),
        "blue_level":float("nan"),"orange_level":float("nan"),"red_level":float("nan"),
        "live_storage":float("nan"),"storage_pct":float("nan"),
        "inflow":float("nan"),"outflow":float("nan"),"spillway_release":float("nan"),
        "rainfall":float("nan"),"total_shutters":0,"open_shutters":0,"opening_percent":0,
        "shutter_status":"Not published", "risk":"Data unavailable",
        "status":"REGISTRY ONLY","data_available":False,"data_source":"REGISTRY ONLY",
        "observed_at":"","source_url":"","level_pct_of_frl":float("nan")
    }

# ============================================================
# ML MODEL — historical KSEB reservoir level prediction
# ============================================================
def _history_filename(mirror_name):
    safe=re.sub(r"[\\/]","-",str(mirror_name)).replace(" ","_")
    return quote(safe+".json",safe="._-()")

@st.cache_data(ttl=21600,show_spinner=False)
def fetch_kseb_history(mirror_name):
    """Prefer the committed KSEB-history CSV, then fall back to the public mirror."""
    # 1) Local committed dataset in the repository. This makes the GitHub CSV
    # part of the reproducible ML pipeline rather than merely a display file.
    local_path=Path(__file__).resolve().parent/"data"/"kseb_reservoir_history.csv"
    if local_path.exists():
        try:
            local=pd.read_csv(local_path)
            if "dam" in local.columns:
                aliases={
                    "Banasurasagar":"Banasura Sagar Dam",
                    "Kakki (Anathode)":"Anathode Dam",
                    "Kakki–Anathode":"Anathode Dam",
                    "Kakkayam":"Kuttiyadi HE Project Dam",
                    "Sholayar":"Sholayar Main Dam",
                    "Madupetty":"Mattupetty Dam",
                    "Chenkulam":"Sengulam Dam",
                    "Lower Periyar":"Pambla Dam (Lower Periyar)",
                    "Anathode":"Anathode Dam",
                }
                local["registry_dam"]=local["dam"].map(lambda x:aliases.get(str(x).strip(),str(x).strip()))
                target=next((k for k,v in KSEB_NAME_TO_REGISTRY.items() if mirror_name and _norm_name(k)==_norm_name(mirror_name)),None)
                target_registry=aliases.get(mirror_name,mirror_name)
                if mirror_name in KERALA_DAM_REGISTRY:
                    target_registry=mirror_name
                subset=local[local["registry_dam"].map(_norm_name)==_norm_name(target_registry)].copy()
                if len(subset)>=3:
                    for col in ["date","water_level_m","storage_percentage","inflow_cumecs","total_outflow_cumecs","rainfall_mm"]:
                        if col not in subset.columns:
                            subset[col]=np.nan
                    df=pd.DataFrame({
                        "date":pd.to_datetime(subset["date"],dayfirst=True,errors="coerce"),
                        "water_level":pd.to_numeric(subset["water_level_m"],errors="coerce"),
                        "storage_pct":pd.to_numeric(subset["storage_percentage"],errors="coerce"),
                        "inflow":pd.to_numeric(subset["inflow_cumecs"],errors="coerce"),
                        "outflow":pd.to_numeric(subset["total_outflow_cumecs"],errors="coerce"),
                        "rainfall":pd.to_numeric(subset["rainfall_mm"],errors="coerce")
                    })
                    df=df.dropna(subset=["date","water_level"]).sort_values("date")
                    if not df.empty:
                        return df.drop_duplicates("date",keep="last").reset_index(drop=True)
        except Exception:
            pass

    # 2) Public machine-readable mirror fallback used by the prototype.
    if not mirror_name:
        return pd.DataFrame()
    url=KSEB_MIRROR_HISTORY_BASE+_history_filename(mirror_name)
    try:
        r=requests.get(url,timeout=10)
        r.raise_for_status()
        payload=r.json()
        rows=[]
        for item in payload.get("data",[]):
            rows.append({
                "date":pd.to_datetime(item.get("date"),dayfirst=True,errors="coerce"),
                "water_level":_number(item.get("waterLevel")),
                "storage_pct":_number(item.get("storagePercentage")),
                "inflow":_mcm_day_to_cumecs(item.get("inflow")),
                "outflow":_mcm_day_to_cumecs(item.get("totalOutflow")),
                "rainfall":_number(item.get("rainfall"))
            })
        df=pd.DataFrame(rows).dropna(subset=["date","water_level"]).sort_values("date")
        return df.drop_duplicates("date",keep="last").reset_index(drop=True)
    except Exception:
        return pd.DataFrame()

@st.cache_resource(ttl=21600,show_spinner=False)
def train_kseb_rf(name,mirror_name):
    history=fetch_kseb_history(mirror_name)
    if history.empty or len(history)<35:
        return {"available":False,"reason":f"Only {len(history)} historical observations available; at least 35 are required for the prototype model." if len(history) else "Historical series unavailable."}
    df=history.copy()
    df["next_rainfall"]=df["rainfall"].shift(-1)
    doy=df["date"].dt.dayofyear
    df["month_sin"]=np.sin(2*np.pi*doy/365.25)
    df["month_cos"]=np.cos(2*np.pi*doy/365.25)
    df["target_next_level"]=df["water_level"].shift(-1)
    df=df.dropna(subset=["target_next_level","water_level","storage_pct","inflow","outflow","rainfall","next_rainfall"])
    if len(df)<35:
        return {"available":False,"reason":f"Only {len(df)} usable historical observations remain after cleaning."}
    features=["water_level","storage_pct","inflow","outflow","rainfall","next_rainfall","month_sin","month_cos"]
    split=max(25,int(len(df)*0.80))
    if split>=len(df): split=len(df)-8
    train=df.iloc[:split]
    test=df.iloc[split:]
    model=RandomForestRegressor(n_estimators=250,max_depth=12,min_samples_leaf=2,random_state=42,n_jobs=-1)
    model.fit(train[features],train["target_next_level"])
    pred=model.predict(test[features])
    mae=float(mean_absolute_error(test["target_next_level"],pred))
    r2=float(r2_score(test["target_next_level"],pred)) if len(test)>=2 else float("nan")
    return {"available":True,"model":model,"features":features,"mae":mae,"r2":r2,"train_rows":len(train),"test_rows":len(test),"history_rows":len(history),"history":history,"name":name}

def ml_next_level(name,dam,next_rain_mm):
    mirror=dam.get("mirror_name","")
    result=train_kseb_rf(name,mirror)
    if not result.get("available"):
        return result
    history=result["history"]
    latest=history.iloc[-1].copy()
    doy=pd.Timestamp.now().dayofyear
    def _feature_value(current, fallback):
        try:
            current=float(current)
            if np.isfinite(current):
                return current
        except (TypeError,ValueError):
            pass
        return float(fallback) if np.isfinite(float(fallback)) else 0.0

    row=pd.DataFrame([{
        "water_level":_feature_value(dam.get("water_level"),latest["water_level"]),
        "storage_pct":_feature_value(dam.get("storage_pct"),latest["storage_pct"]),
        "inflow":_feature_value(dam.get("inflow"),latest["inflow"]),
        "outflow":_feature_value(dam.get("outflow"),latest["outflow"]),
        "rainfall":_feature_value(dam.get("rainfall"),latest["rainfall"]),
        "next_rainfall":_feature_value(next_rain_mm,latest["rainfall"]),
        "month_sin":math.sin(2*math.pi*doy/365.25),
        "month_cos":math.cos(2*math.pi*doy/365.25),
    }])
    pred=float(result["model"].predict(row[result["features"]])[0])
    return {**result,"prediction":round(pred,2),"forecast_rainfall":round(float(next_rain_mm),1)}




def render_dam_profile(name, dam=None, mode="Authority"):
    """Show the same dam profile wherever a dam is selected.

    Registry information is always available for every listed dam. Operational
    values are shown only when connected to the prototype demo record.
    """
    meta=KERALA_DAM_REGISTRY[name]
    if dam is None:
        dam=authority_dam_record(name)
    st.markdown('<div class="hs-section">Dam Details</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    a,b,c,d=st.columns(4)
    a.metric("Dam",name)
    b.metric("District",meta["district"])
    c.metric("Operator",meta["operator"])
    d.metric("Data status",dam.get("status","REGISTRY ONLY"))
    a,b,c,d=st.columns(4)
    a.metric("River / system",meta["river"])
    b.metric("Completion year",str(meta["year"]))
    c.metric("Latitude",f"{meta['lat']:.4f}")
    d.metric("Longitude",f"{meta['lon']:.4f}")
    if dam.get("data_available"):
        level=dam.get("water_level",float("nan")); storage=dam.get("storage_pct",float("nan")); inflow=dam.get("inflow",float("nan")); outflow=dam.get("outflow",float("nan"))
        st.caption(
            f"Published observation: {dam.get('observed_at','')}  ·  Source: {dam.get('data_source','')}"
        )
        if dam.get("source_url"):
            st.caption(f"Source record: {dam['source_url']}")
    else:
        st.caption("No published operational observation is connected for this dam in the current prototype. Registry information remains available.")

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
# AUTHORITY STRUCTURAL SAFETY — evidence + real-data analysis
# ============================================================
# Structural-health numbers are NEVER invented here. The module separates:
# 1) documented public safety-audit / inspection evidence,
# 2) actual structural/instrumentation time-series supplied to the app, and
# 3) current reservoir loading from the KSEB/KSDMA operational layer.
#
# CWC/DRIP safety-audit evidence below is documentary evidence, not a structural
# condition score. Actual crack/seepage/deformation measurements require the
# underlying authorised inspection/instrumentation records.
STRUCTURAL_AUDIT_SOURCE_URL="https://rsdebate.nic.in/bitstream/123456789/723090/1/PQ_255_13122021_S156_p34_p42.pdf"
CWC_INSPECTION_GUIDELINE_URL="https://drip.cwc.gov.in/ecm-includes/PDFs/Guidelines_for_Safety_Inspection_of_Dams.pdf"
CWC_STRUCTURAL_SAFETY_URL="https://drip.cwc.gov.in/ecm-includes/PDFs/Manual_for_Assessing_Structural_Safety.pdf"
KSDMA_DAM_MANAGEMENT_URL="https://sdma.kerala.gov.in/dam-management/"
MULLAPERIYAR_REPORT_URL="https://sdma.kerala.gov.in/wp-content/uploads/2019/08/Report-of-the-Expert-Group-Mullaperiyar-22-Nov-2011.pdf"

# Dams recorded in the Government of India / DRIP-II & III preparatory safety-audit
# list for November 2018-November 2021, mapped to our registry names.
STRUCTURAL_AUDIT_DAMS={
    "Anayirankal Dam":"DRIP safety audit recorded",
    "Idamalayar Dam":"DRIP safety audit recorded",
    "Idukki Dam":"DRIP safety audit recorded",
    "Cheruthoni Dam":"DRIP safety audit recorded",
    "Kulamavu Dam":"DRIP safety audit recorded",
    "Kuttiyadi HE Project Dam":"DRIP safety audit recorded",
    "Kakki Dam":"DRIP safety audit recorded",
    "Anathode Dam":"DRIP safety audit recorded",
    "Kallarkutty Dam":"DRIP safety audit recorded",
    "Kundala Dam":"DRIP safety audit recorded",
    "Mattupetty Dam":"DRIP safety audit recorded",
    "Kuttiyadi Augmentation Main Dam":"DRIP safety audit recorded",
    "Kuttiyadi Augmentation Spillway Dam":"DRIP safety audit recorded",
    "Pambla Dam (Lower Periyar)":"DRIP safety audit recorded",
    "Moozhiyar Dam":"DRIP safety audit recorded",
    "Pamba Dam":"DRIP safety audit recorded",
    "Ponmudi Dam":"DRIP safety audit recorded",
    "Poringalkuthu Dam":"DRIP safety audit recorded",
    "Sholayar Main Dam":"DRIP safety audit recorded",
    "Sholayar Flanking Dam":"DRIP safety audit recorded",
    "Sholayar Saddle Dam":"DRIP safety audit recorded",
    "Kallada Dam (Parappar)":"DRIP safety audit recorded",
    "Kanjirappuzha Dam":"DRIP safety audit recorded",
    "Karapuzha Dam":"DRIP safety audit recorded",
    "Malampuzha Dam":"DRIP safety audit recorded",
    "Malankara Dam":"DRIP safety audit recorded",
    "Mangalam Dam":"DRIP safety audit recorded",
    "Neyyar Dam":"DRIP safety audit recorded",
    "Maniyar Dam":"DRIP safety audit recorded",
    "Periyar Valley Barrage":"DRIP safety audit recorded",
    "Walayar Dam":"DRIP safety audit recorded",
}

MULLAPERIYAR_EVIDENCE={
    "report_date":"22 Nov 2011",
    "source":"Kerala Expert Group report",
    "observations":[
        "The report could not confirm whether new cracks on the dam were specifically caused by the 18 November earthquake.",
        "Seepage data were not available to the expert group at the time of the visit, so an increase in total seepage could not be established.",
        "Lime-leaching deposits/stalactite-like formations were observed in weeping holes, and deposits of leached surki mixture were observed in seepage channels.",
        "The report noted concerns about piezometer instrumentation because gauges were present but measurements were not available from the standpipe piezometers reviewed."
    ],
}

STRUCTURAL_REQUIRED_COLUMNS=[
    "dam","date","seepage","uplift","pore_pressure","deformation",
    "crack_width","material_strength","reservoir_level"
]
STRUCTURAL_NUMERIC_COLUMNS=[
    "seepage","uplift","pore_pressure","deformation",
    "crack_width","material_strength","reservoir_level"
]


def _structural_history_paths():
    base=Path(__file__).resolve().parent / "data"
    return [base / "structural_history.csv", base / "structural_history_data.csv"]

@st.cache_data(ttl=900,show_spinner=False)
def load_structural_history():
    """Load an actual structural/instrumentation CSV if present in data/."""
    for path in _structural_history_paths():
        if not path.exists():
            continue
        try:
            df=pd.read_csv(path)
            cols={str(c).strip().lower():str(c) for c in df.columns}
            rename={cols[c]:c for c in STRUCTURAL_REQUIRED_COLUMNS if c in cols}
            df=df.rename(columns=rename)
            if "dam" not in df.columns:
                continue
            df["dam"]=df["dam"].astype(str).str.strip()
            if "date" in df.columns:
                df["date"]=pd.to_datetime(df["date"],errors="coerce",dayfirst=True)
            else:
                df["date"]=pd.NaT
            for c in STRUCTURAL_NUMERIC_COLUMNS:
                if c not in df.columns:
                    df[c]=np.nan
                df[c]=pd.to_numeric(df[c],errors="coerce")
            return df.sort_values(["dam","date"],na_position="last").reset_index(drop=True), str(path)
        except Exception:
            continue
    return pd.DataFrame(columns=STRUCTURAL_REQUIRED_COLUMNS), ""


def structural_history_for_dam(dam_name, uploaded_df=None):
    if uploaded_df is not None and not uploaded_df.empty:
        df=uploaded_df.copy()
    else:
        df,_=load_structural_history()
    if df.empty or "dam" not in df.columns:
        return pd.DataFrame(columns=STRUCTURAL_REQUIRED_COLUMNS)
    names=df["dam"].astype(str)
    mask=names.map(_norm_name)==_norm_name(dam_name)
    return df.loc[mask].copy().sort_values("date",na_position="last").reset_index(drop=True)


def structural_ml_anomaly(history):
    """Unsupervised anomaly screening for actual structural measurements.

    This model is intentionally not a failure-probability model. It identifies
    unusual multivariate observations relative to the supplied historical record.
    """
    if history.empty:
        return {"available":False,"reason":"No structural-history records loaded."}
    available=[c for c in STRUCTURAL_NUMERIC_COLUMNS if c in history.columns and history[c].notna().sum()>=6]
    if len(history)<12 or len(available)<2:
        return {"available":False,"reason":f"Need at least 12 records and 2 measured structural variables; found {len(history)} records and {len(available)} usable variables."}
    data=history[available].dropna()
    if len(data)<12:
        return {"available":False,"reason":f"Only {len(data)} complete multivariate records are available."}
    pipe=Pipeline([
        ("scale",StandardScaler()),
        ("model",IsolationForest(n_estimators=200,contamination="auto",random_state=42))
    ])
    pipe.fit(data)
    labels=pipe.predict(data)
    latest=data.iloc[-1:]
    latest_label=int(pipe.predict(latest)[0])
    score=float(-pipe.decision_function(latest)[0])
    return {
        "available":True,
        "features":available,
        "records":len(data),
        "latest_anomaly":latest_label==-1,
        "anomaly_score":round(score,4),
    }


def structural_evidence(dam_name, dam, uploaded_df=None):
    history=structural_history_for_dam(dam_name,uploaded_df)
    audit=dam_name in STRUCTURAL_AUDIT_DAMS
    has_mullaperiyar=(dam_name=="Mullaperiyar Dam")
    ml=structural_ml_anomaly(history)
    current_year=pd.Timestamp.now().year
    age=max(0,current_year-KERALA_DAM_REGISTRY[dam_name]["year"])
    return {
        "age":age,
        "audit":audit,
        "audit_text":STRUCTURAL_AUDIT_DAMS.get(dam_name,"No linked DRIP safety-audit record in the connected public source"),
        "history_rows":len(history),
        "history":history,
        "ml":ml,
        "mullaperiyar":has_mullaperiyar,
        "data_status":"STRUCTURAL RECORDS LOADED" if len(history)>0 else ("DOCUMENTARY SAFETY EVIDENCE" if audit or has_mullaperiyar else "NO STRUCTURED STRUCTURAL DATA"),
    }

# Keep the old function name for compatibility with any existing callers.
def structural_assessment(dam_name, dam, uploaded_df=None):
    e=structural_evidence(dam_name,dam,uploaded_df)
    return {"status":e["data_status"],"evidence":e}

# ============================================================
# HELPERS
# ============================================================
def distance_km(lat1,lon1,lat2,lon2):
    R=6371.0; p1=math.radians(lat1); p2=math.radians(lat2); dp=math.radians(lat2-lat1); dl=math.radians(lon2-lon1)
    a=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.atan2(math.sqrt(a),math.sqrt(1-a))

def nearby_dams(location,radius=120):
    """Return all registered Kerala dams within the selected radius.

    The registry contains the full dam reference set. Only the small demo subset
    has prototype operational telemetry; registry-only dams are still searchable
    and mappable, with their operational fields shown as unavailable.
    """
    lat,lon=LOCATIONS[location]; out=[]
    for name,meta in KERALA_DAM_REGISTRY.items():
        dist=distance_km(lat,lon,meta["lat"],meta["lon"])
        if dist<=radius:
            d=_published_record(name) or _demo_record(name,meta) or {}
            x={
                "name":name,
                "district":meta["district"],
                "operator":meta["operator"],
                "construction_year":meta["year"],
                "river":meta["river"],
                "lat":meta["lat"],
                "lon":meta["lon"],
                "water_level":d.get("water_level",float("nan")),
                "frl":d.get("frl",float("nan")),
                "rule_level":d.get("rule_level",float("nan")),
                "blue_level":d.get("blue_level",float("nan")),
                "orange_level":d.get("orange_level",float("nan")),
                "red_level":d.get("red_level",float("nan")),
                "live_storage":d.get("live_storage",float("nan")),
                "storage_pct":d.get("storage_pct",float("nan")),
                "level_pct_of_frl":d.get("level_pct_of_frl",float("nan")),
                "inflow":d.get("inflow",float("nan")),
                "outflow":d.get("outflow",float("nan")),
                "spillway_release":d.get("spillway_release",float("nan")),
                "rainfall":d.get("rainfall",float("nan")),
                "total_shutters":d.get("total_shutters",0),
                "open_shutters":d.get("open_shutters",0),
                "opening_percent":d.get("opening_percent",0),
                "shutter_status":d.get("shutter_status","Not published in source dataset"),
                "risk":d.get("risk","Data unavailable"),
                "status":d.get("status","REGISTRY ONLY"),
                "data_available":bool(d.get("data_available",False)),
                "observed_at":d.get("observed_at",""),
                "data_source":d.get("data_source",""),
                "source_url":d.get("source_url",""),
                "mirror_name":d.get("mirror_name", ""),
                "distance":dist,
            }
            out.append(x)
    return sorted(out,key=lambda x:x["distance"])

def location_options(district="All districts", search=""):
    names=[n for n in LOCATIONS if district=="All districts" or LOCATION_DISTRICTS.get(n)==district]
    search=search.strip().lower()
    if search:
        names=[n for n in names if search in n.lower()]
    return names

def risk_score(d):
    level_pct=d.get("level_pct_of_frl",float("nan"))
    if not np.isfinite(level_pct):
        level_pct=0
    flow=min(100,max(0,d.get("inflow",0)/20))
    opening=min(100,d.get("opening_percent",0)*2)
    return int(min(100,round(min(100,level_pct)*.45+flow*.35+opening*.20)))

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
    frl=d.get("frl",float("nan"))
    current_ratio=(d.get("water_level",0)/frl) if np.isfinite(frl) and frl>0 else 0
    pred_ratio=(pred/frl) if np.isfinite(frl) and frl>0 else 0
    inflow=min(1,max(0,d.get("inflow",0)/50))
    score=100*(0.35*min(1,current_ratio)+0.35*min(1,pred_ratio)+0.30*inflow)
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

    spillway=float(d.get("spillway_release",0) if np.isfinite(d.get("spillway_release",float("nan"))) else 0)
    current_release=spillway>0
    heavy24=r24>=50
    heavy48=r48>=80
    elevated=d["risk"] in {"Moderate","High"}

    if current_release:
        outlook="Spillway release currently reported"
        detail="The published reservoir record reports a non-zero spillway release. Continued or adjusted release depends on authorised reservoir operations."
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

# Add registry-wide illustrative downstream corridors after the curated entries above.
for _name, _meta in KERALA_DAM_REGISTRY.items():
    _city = {
        "Idukki":"Idukki district downstream corridor",
        "Pathanamthitta":"Pamba basin downstream corridor",
        "Wayanad":"Wayanad downstream river corridor",
        "Palakkad":"Palakkad downstream corridor",
        "Thrissur":"Thrissur downstream river corridor",
        "Ernakulam":"Periyar/Ernakulam downstream corridor",
        "Kollam":"Kollam downstream corridor",
        "Thiruvananthapuram":"Thiruvananthapuram downstream corridor",
        "Kannur":"Kannur downstream corridor",
    }.get(_meta["district"], f"{_meta['district']} downstream corridor")
    DOWNSTREAM_ZONES.setdefault(_name, [_city, f"Low-lying areas along the {_meta['river']} downstream reach"])

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
    has_data=bool(dam.get("data_available",True)) and not pd.isna(dam.get("water_level",float("nan")))
    raw_pct=dam.get("level_pct_of_frl",float("nan"))
    if not np.isfinite(raw_pct):
        raw_level=dam.get("water_level",float("nan"))
        raw_pct=35.0 if not np.isfinite(raw_level) else min(94.0,max(8.0,float(raw_level)))
    pct=max(8,min(94,float(raw_pct))) if has_data else 35
    gates=[]
    total=int(dam.get("total_shutters",4)) if has_data else 4
    opened=int(dam.get("open_shutters",0)) if has_data else 0
    for i in range(total):
        gates.append('<span class="hs-gate open"></span>' if i < opened else '<span class="hs-gate"></span>')
    name=dam.get("name","Idukki Dam")
    level_text=f'{float(dam["water_level"]):.1f} m' if has_data else 'Telemetry unavailable'
    level_sub='published reservoir level' if has_data else 'registry reference only'
    return f"""<div class="hs-dam-scene">
      <div class="hs-dam-sky"></div><div class="hs-moon"></div>
      <div class="hs-mountain m1"></div><div class="hs-mountain m2"></div>
      <div class="hs-scene-label"><div class="small">Interactive reservoir view</div><div class="big">{name}</div></div>
      <div class="hs-scene-level"><strong>{level_text}</strong><span>{level_sub}</span></div>
      <div class="hs-reservoir"><div class="hs-waterline"></div><div class="hs-reservoir-fill" style="height:{pct}%"></div></div>
      <div class="hs-dam-wall"></div><div class="hs-gates">{''.join(gates)}</div>
      <div class="hs-river"></div>
    </div>"""


def flood_ready_challenge():
    """Interactive public flood-awareness decision challenge."""
    scenarios=[
        {"title":"Scenario 1 · Rising water","icon":"🌧️","text":"Heavy rain is continuing and your local reservoir dashboard shows a rising water level. An official weather warning is active.","q":"What is the safest first response?","opts":["Wait until water enters the street","Check official alerts and prepare to move to a safer location if instructed","Drive toward the dam to see what is happening","Cross a flooded road quickly before it rises"],"answer":1,"why":"Official alerts and evacuation instructions should guide action. Do not approach dams or enter floodwater."},
        {"title":"Scenario 2 · Flooded road","icon":"🚧","text":"You are travelling and reach a road covered by moving floodwater. You cannot see the road surface clearly.","q":"What should you do?","opts":["Turn around and use a safe alternative","Drive slowly through it","Follow another vehicle through","Walk through first and then drive"],"answer":0,"why":"Moving or unseen floodwater can hide washouts, debris and unsafe depths. Avoid entering it."},
        {"title":"Scenario 3 · Emergency preparation","icon":"🎒","text":"A flood warning has been issued for your area. You have a short time to prepare before leaving if authorities instruct evacuation.","q":"Which action is useful?","opts":["Charge your phone and keep essential medicines/documents ready","Turn off all communication devices","Wait for social-media rumours before acting","Move to a bridge to watch the river"],"answer":0,"why":"Keeping communication available and essential items ready improves preparedness."},
        {"title":"Scenario 4 · Information check","icon":"📡","text":"Two messages are circulating: one from an official disaster-management channel and one from an unverified social-media account.","q":"Which should you rely on for evacuation instructions?","opts":["The message with the most shares","The official disaster-management/authority communication","A random forwarded message","Whichever message sounds more urgent"],"answer":1,"why":"For emergency instructions, use verified communications from authorised agencies."},
        {"title":"Scenario 5 · After the water rises","icon":"🏠","text":"Floodwater is approaching your neighbourhood and an official evacuation instruction has been issued.","q":"What is the appropriate response?","opts":["Follow the official evacuation route/instructions","Stay behind to protect property","Return after leaving to check the house","Stand near the river for updates"],"answer":0,"why":"Follow authorised evacuation instructions and avoid returning until authorities indicate it is safe."},
    ]
    if "frc_index" not in st.session_state: st.session_state.frc_index=0
    if "frc_score" not in st.session_state: st.session_state.frc_score=0
    if "frc_answered" not in st.session_state: st.session_state.frc_answered=False
    i=st.session_state.frc_index
    if i>=len(scenarios):
        score=st.session_state.frc_score
        st.markdown('<div class="hs-card" style="text-align:center;padding:34px"><div class="hs-card-label">CHALLENGE COMPLETE</div><div class="hs-card-title">Flood Ready Check</div><div style="font-size:52px;font-weight:900;color:#79e5ff;margin:14px 0">'+str(score)+' / '+str(len(scenarios))+'</div><p class="hs-card-copy">You completed a public flood-awareness scenario challenge. The goal is preparedness and safe decision-making, not dam-operation control.</p></div>',unsafe_allow_html=True)
        if st.button("Play Again",key="frc_restart",type="primary"):
            st.session_state.frc_index=0; st.session_state.frc_score=0; st.session_state.frc_answered=False; st.rerun()
        return
    sc=scenarios[i]
    st.markdown(f'<div class="hs-section">Flood Ready Challenge</div><div class="hs-section-line"></div><div class="hs-note">Scenario {i+1} of {len(scenarios)} · Learn how to interpret flood situations and choose safer public responses.</div>',unsafe_allow_html=True)
    st.progress(i/len(scenarios))
    st.markdown(f'<div class="hs-card"><div style="font-size:34px">{sc["icon"]}</div><div class="hs-card-label">{sc["title"]}</div><div class="hs-card-title">{sc["text"]}</div><p class="hs-card-copy">{sc["q"]}</p></div>',unsafe_allow_html=True)
    choice=st.radio("Choose your response",sc["opts"],index=None,key=f"frc_choice_{i}")
    if not st.session_state.frc_answered:
        if st.button("Check Answer",key=f"frc_check_{i}",type="primary",disabled=choice is None):
            selected=sc["opts"].index(choice)
            st.session_state.frc_answered=True
            if selected==sc["answer"]: st.session_state.frc_score+=1
            st.rerun()
    else:
        selected=sc["opts"].index(choice) if choice in sc["opts"] else -1
        if selected==sc["answer"]:
            st.success("Correct — safe choice.")
        else:
            st.warning("Review the safer response before continuing.")
        st.info(sc["why"])
        if st.button("Next Scenario →",key=f"frc_next_{i}",type="primary"):
            st.session_state.frc_index+=1; st.session_state.frc_answered=False; st.rerun()


def dam_map(location):
    lat,lon=LOCATIONS[location]
    m=folium.Map(location=[lat,lon],zoom_start=8,tiles="OpenStreetMap",control_scale=True)
    folium.Circle([lat,lon],radius=120000,color="#25b9ff",fill=True,fill_opacity=.05).add_to(m)
    folium.Marker([lat,lon],tooltip=location,icon=folium.Icon(color="blue",icon="info-sign")).add_to(m)
    # Plot the complete registered Kerala dam set, not only the demo telemetry subset.
    for name,meta in KERALA_DAM_REGISTRY.items():
        dist=distance_km(lat,lon,meta["lat"],meta["lon"])
        d=_published_record(name) or _demo_record(name,meta) or {}
        risk=d.get("risk","Data unavailable")
        c="red" if risk=="High" else "orange" if risk=="Moderate" else "green" if risk=="Normal" else "blue"
        if d:
            txt=(f"<b>{name}</b><br>District: {meta['district']}<br>"
                 f"Operator: {meta['operator']}<br>River: {meta['river']}<br>"
                 f"Water level: {d['water_level']:.1f}<br>"
                 f"Shutters: {d['open_shutters']}/{d['total_shutters']}<br>"
                 f"Risk: {risk}<br>Distance: {dist:.1f} km")
        else:
            txt=(f"<b>{name}</b><br>District: {meta['district']}<br>"
                 f"Operator: {meta['operator']}<br>River: {meta['river']}<br>"
                 f"Completion year: {meta['year']}<br>"
                 f"Operational telemetry: registry only<br>Distance: {dist:.1f} km")
        folium.Marker(
            [meta["lat"],meta["lon"]],
            tooltip=name,
            popup=folium.Popup(txt,max_width=300),
            icon=folium.Icon(color=c,icon="tint")
        ).add_to(m)
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
st.markdown('<div class="hs-topbar"><div class="hs-topbar-copy">Kerala water intelligence interface</div><div class="hs-topbar-live"><span class="hs-live-line"></span>Live weather connection</div></div>',unsafe_allow_html=True)

nav=["Home","Public Dashboard","Flood Ready Challenge","Authority Access"]
if st.session_state.authority: nav += ["Prediction","Authority Console","Structural Safety","Hydraulic Simulation"]
cols=st.columns(len(nav))
for c,name in zip(cols,nav):
    with c:
        active = st.session_state.page == name
        if st.button(name,key="nav_"+name,type="primary" if active else "secondary"):
            st.session_state.page=name; st.rerun()

st.divider()

# ============================================================
# HOME
# ============================================================
if st.session_state.page=="Home":
    home_dam=authority_dam_record("Idukki Dam")
    if not home_dam.get("data_available"):
        home_dam=DAM_DATABASE["Idukki Dam"]
    st.markdown("""<div class="hs-hero">
      <div class="hs-hero-orbit"></div>
      <div class="hs-hero-copywrap">
        <div class="hs-kicker">Public water intelligence</div>
        <div class="hs-hero-title">See the water.<br><span>Understand what comes next.</span></div>
        <div class="hs-hero-copy">HYDROSCOPE connects rainfall, reservoir conditions and downstream awareness in one interactive public interface. Explore a dam, inspect its 24–48 hour outlook, or pilot the fictional Flood Ready Challenge game.</div>
        <div class="hs-hero-actions"><span class="hs-action">DAM MONITORING</span><span class="hs-action">RAINFALL OUTLOOK</span><span class="hs-action">PUBLIC SAFETY</span></div>
      </div>
    </div>""",unsafe_allow_html=True)
    st.write("")
    a,b=st.columns([1.35,.65])
    with a:
        st.markdown(interactive_dam_visual(home_dam),unsafe_allow_html=True)
    with b:
        level_pct=min(100,max(5,home_dam["water_level"]))
        rain_pct=min(100,max(5,home_dam["rainfall"]))
        st.markdown(f"""<div class="hs-command-panel" style="height:100%;box-sizing:border-box;">
          <div class="hs-command-label">Current reservoir state</div>
          <div class="hs-command-value">{home_dam["water_level"]:.1f} m</div>
          <div class="hs-command-copy">Reservoir level · {home_dam["risk"]} condition</div>
          <div class="hs-signal"><span style="width:{level_pct:.0f}%"></span></div>
          <div style="height:18px"></div>
          <div class="hs-command-label">Rainfall input</div>
          <div class="hs-command-value">{home_dam["rainfall"]:.0f} mm</div>
          <div class="hs-command-copy">Published rainfall input · source status {home_dam.get("status","Prototype")}</div>
          <div class="hs-signal"><span style="width:{rain_pct:.0f}%"></span></div>
        </div>""",unsafe_allow_html=True)
    st.write("")
    a,b,c,d=st.columns(4)
    a.metric("Water level",f'{home_dam["water_level"]:.1f} m')
    b.metric("Rainfall input",f'{home_dam["rainfall"]:.0f} mm')
    c.metric("Storage",f'{home_dam.get("storage_pct",0):.1f}%')
    d.metric("Risk state",home_dam["risk"])
    st.write("")
    a,b,c=st.columns(3)
    with a:
        st.markdown('<div class="hs-card"><div class="hs-card-label">01 / DISCOVER</div><div class="hs-card-title">Inspect nearby dams</div><p class="hs-card-copy">Find monitored prototype dams around a Kerala location and open a focused 24–48 hour public release outlook.</p></div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="hs-card"><div class="hs-card-label">02 / UNDERSTAND</div><div class="hs-card-title">Follow the water story</div><p class="hs-card-copy">Reservoir level, gates and downstream flow become one connected visual story instead of isolated numbers.</p></div>',unsafe_allow_html=True)
    with c:
        st.markdown('<div class="hs-card"><div class="hs-card-label">03 / EXPERIENCE</div><div class="hs-card-title">Try Flood Ready Challenge</div><p class="hs-card-copy">Test your flood-awareness decisions through short, realistic public-safety scenarios and learn why each response matters.</p></div>',unsafe_allow_html=True)
    st.write("")
    x,y=st.columns(2)
    if x.button("Explore Public Dashboard",key="home_public",type="primary"): st.session_state.page="Public Dashboard"; st.rerun()
    if y.button("Try Flood Ready Challenge",key="home_flood_challenge"): st.session_state.page="Flood Ready Challenge"; st.rerun()

# ============================================================
# PUBLIC DASHBOARD
# ============================================================
elif st.session_state.page=="Public Dashboard":
    st.markdown('<div class="hs-dashboard-head"><div><div class="hs-dashboard-title">Public Safety Dashboard</div><div class="hs-dashboard-sub">A location-first view of dams, weather and downstream awareness.</div></div><div class="hs-location-badge">PUBLIC MODE · READ ONLY</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="hs-section-line" style="margin-top:14px"></div>',unsafe_allow_html=True)
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
                if d.get("data_available"):
                    gate_text=(f'Spillway release <b>{d["spillway_release"]:.2f} m³/s</b>' if np.isfinite(d.get("spillway_release",float("nan"))) else 'Gate status <b>Not published</b>')
                    card_copy=(f'Water level <b>{d["water_level"]:.1f} m</b>  |  Storage <b>{d.get("storage_pct",float("nan")):.1f}%</b><br>'
                               f'{gate_text}  |  Rainfall <b>{d.get("rainfall",float("nan")):.1f} mm</b>')
                else:
                    card_copy=(f'River <b>{d["river"]}</b>  |  Operator <b>{d["operator"]}</b><br>'
                               f'Operational telemetry <b>Registry only</b>')
                st.markdown(f'<div class="hs-card" style="{border}"><span class="hs-pill">{d["risk"]}  /  {d["distance"]:.1f} km</span><div class="hs-card-title" style="margin-top:12px">{d["name"]}</div><div class="hs-card-copy">{card_copy}</div></div>',unsafe_allow_html=True)
                if st.button("Inspect",key=f"inspect_{d['name']}",use_container_width=True):
                    st.session_state.public_dam_focus_pending=d["name"]
                    st.rerun()

        selected=st.session_state.get("public_dam_focus")
        if selected in dam_names:
            focus=next(d for d in dams if d["name"]==selected)
            st.markdown('<div class="hs-section">Dam Release Outlook</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
            if not focus.get("data_available"):
                st.markdown(f'<div class="hs-interactive"><div class="hs-mini">Public inspection</div><div class="hs-big">{focus["name"]}</div><div class="hs-click">{focus["district"]}  |  {focus["river"]}  |  {focus["operator"]}  |  Distance {focus["distance"]:.1f} km</div></div>',unsafe_allow_html=True)
                st.info("This dam is included in the Kerala registry. Verified operational telemetry is not connected to the prototype, so current reservoir/gate values are not displayed as live data.")
                render_dam_profile(focus["name"], authority_dam_record(focus["name"]), mode="Public")
                f=forecast(focus["lat"],focus["lon"])
                if f["success"] and not f["data"].empty:
                    rs=rainfall_summary(f["data"])
                    x,y,z=st.columns(3)
                    x.metric("Forecast rain — 6 h",f"{rs['rain_6h']} mm")
                    y.metric("Forecast rain — 12 h",f"{rs['rain_12h']} mm")
                    z.metric("Forecast rain — 24 h",f"{rs['rain_24h']} mm")
                zones=DOWNSTREAM_ZONES.get(focus["name"],["Downstream river corridor","Nearby low-lying areas"])
                st.markdown('<div class="hs-card"><div class="hs-card-label">Potential downstream awareness</div><div class="hs-card-title">Areas to examine in a hypothetical scenario</div><p class="hs-card-copy">' + " • ".join(zones) + '</p></div>',unsafe_allow_html=True)
            else:
                gate_line=(f'Spillway release {focus.get("spillway_release",0):.2f} m³/s' if np.isfinite(focus.get("spillway_release",float("nan"))) else 'Gate status not published')
                st.markdown(f'<div class="hs-interactive"><div class="hs-mini">Public inspection</div><div class="hs-big">{focus["name"]}</div><div class="hs-click">Current level {focus["water_level"]:.1f} m  |  Storage {focus.get("storage_pct",0):.1f}%  |  {gate_line}  |  Distance {focus["distance"]:.1f} km</div></div>',unsafe_allow_html=True)

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
        st.info("No registered Kerala dams are within this radius. Increase the monitoring radius or select a dam from the All Kerala Dams directory.")

    st.markdown('<div class="hs-section">All Kerala Dams</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    public_all_name=st.selectbox("Select any registered Kerala dam",AUTHORITY_DAM_OPTIONS,key="public_all_dam")
    public_all_demo=authority_dam_record(public_all_name)
    render_dam_profile(public_all_name, public_all_demo, mode="Public")
    zones=DOWNSTREAM_ZONES.get(public_all_name,["Downstream river corridor","Nearby low-lying areas"])
    st.markdown(f'<div class="hs-card"><div class="hs-card-label">Potential downstream impact</div><div class="hs-card-title">Areas to monitor in a hypothetical dam-break scenario</div><p class="hs-card-copy">{" • ".join(zones)}</p></div>',unsafe_allow_html=True)

    st.markdown('<div class="hs-section">Kerala Monitoring Map</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    st_folium(dam_map(loc),height=560,width=None,returned_objects=[])
    st.markdown('<div class="hs-note">HYDROSCOPE provides public awareness and safety information. Official warnings and evacuation instructions remain the responsibility of authorized agencies. Reservoir values are shown from published source records when available; otherwise they are clearly marked as prototype/registry data.</div>',unsafe_allow_html=True)

# ============================================================
# HYDRO GUARDIAN
# ============================================================
elif st.session_state.page=="Flood Ready Challenge":
    flood_ready_challenge()

# ============================================================
# PREDICTION
# ============================================================
elif st.session_state.page=="Prediction":
    if not st.session_state.authority:
        st.session_state.page="Public Dashboard"
        st.rerun()
    st.markdown('<div class="hs-section">Water-Level Prediction</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    name=st.selectbox("Select Dam",AUTHORITY_DAM_OPTIONS,key="pred_dam")
    dam=authority_dam_record(name)
    if not dam["data_available"]:
        st.info(f"{name} is present in the Kerala authority registry, but verified reservoir telemetry is not connected to this prototype. Weather forecasting remains available from the dam coordinates.")
        render_dam_profile(name,dam)
        f=forecast(dam["lat"],dam["lon"])
        if f["success"] and not f["data"].empty:
            s=rainfall_summary(f["data"])
            st.subheader("Weather forecast available")
            a,b,c=st.columns(3)
            a.metric("6h rainfall",f"{s['rain_6h']} mm")
            b.metric("12h rainfall",f"{s['rain_12h']} mm")
            c.metric("24h rainfall",f"{s['rain_24h']} mm")
            fig=go.Figure(go.Bar(x=f["data"]["datetime"],y=f["data"]["rainfall"]))
            fig.update_layout(template="plotly_dark",height=350,title="Forecast Rainfall",xaxis_title="Time",yaxis_title="mm / 3h")
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.warning("Weather forecast is currently unavailable for this registry location.")
        zones=DOWNSTREAM_ZONES.get(name,["Downstream river corridor","Nearby low-lying areas"])
        st.markdown(f'<div class="hs-card"><div class="hs-card-label">Potential downstream impact</div><div class="hs-card-title">Areas to examine</div><p class="hs-card-copy">{" • ".join(zones)}</p></div>',unsafe_allow_html=True)
    else:
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

        st.markdown('<div class="hs-section">ML Water-Level Forecast</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
        ml=ml_next_level(name,dam,s["rain_24h"])
        if ml.get("available"):
            a,b,c,d4=st.columns(4)
            a.metric("Current level",f"{dam['water_level']:.2f} m")
            b.metric("RF predicted next-day level",f"{ml['prediction']:.2f} m")
            c.metric("Validation MAE",f"{ml['mae']:.2f} m")
            d4.metric("Training records",f"{ml['history_rows']:,}")
            st.caption(f"Random Forest Regression trained on historical KSEB-derived daily observations for {name}. Time-ordered validation: R² = {ml['r2']:.3f} · Test records = {ml['test_rows']:,}.")
            if np.isfinite(ml.get("r2",float("nan"))):
                st.info("The ML forecast is a prototype research prediction, not an operational release instruction. Model performance can vary by reservoir and season.")
        else:
            pred=predict_level(dam,s["rain_24h"])
            a,b,c=st.columns(3)
            a.metric("Current level",f"{dam['water_level']:.2f} m")
            b.metric("Fallback mathematical forecast",f"{pred:.2f} m")
            c.metric("ML status","Unavailable")
            st.warning("Historical KSEB observations are not sufficient for a per-dam Random Forest model yet; the transparent mathematical forecast is retained as fallback.")

        prob=release_probability(dam,ml.get("prediction",predict_level(dam,s["rain_24h"])))
        st.metric("Release-risk indicator",f"{prob}%")
        st.markdown('<div class="hs-note">KSEB-published observations are used as reservoir inputs when available. The Random Forest model learns next-day water-level behaviour from historical observations; it does not determine gate operations or official warnings.</div>',unsafe_allow_html=True)
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
    name=st.selectbox("Dam",AUTHORITY_DAM_OPTIONS,key="auth_dam")
    dam=authority_dam_record(name)
    if not dam["data_available"]:
        render_dam_profile(name,dam)
        st.markdown('<div class="hs-note">Verified reservoir telemetry is not connected for this dam in the current prototype. Operational values must come from an authorised data feed before they are displayed.</div>',unsafe_allow_html=True)
        zones=DOWNSTREAM_ZONES.get(name,["Downstream river corridor","Nearby low-lying areas"])
        st.markdown(f'<div class="hs-card"><div class="hs-card-label">Potential downstream impact</div><div class="hs-card-title">Areas to examine if a hypothetical failure occurs</div><p class="hs-card-copy">{" • ".join(zones)}</p></div>',unsafe_allow_html=True)
        st.markdown('<div class="hs-note">The authority console continues to support every registry dam. Detailed operational calculations activate when verified reservoir inputs are available.</div>',unsafe_allow_html=True)
    else:
        render_dam_profile(name,dam)
        a,b,c,e=st.columns(4)
        a.metric("Water level",f"{dam['water_level']:.2f} m")
        a2=dam.get("storage_pct",float("nan")); b.metric("Live storage",f"{a2:.1f}%" if np.isfinite(a2) else "—")
        c.metric("Average inflow",f"{dam['inflow']:.2f} m³/s" if np.isfinite(dam.get("inflow",float("nan"))) else "—")
        spill=dam.get("spillway_release",float("nan")); e.metric("Spillway release",f"{spill:.2f} m³/s" if np.isfinite(spill) else "—")
        st.markdown('<div class="hs-section">Published reservoir parameters</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
        factors=pd.DataFrame({"Parameter":["FRL","Rule level","Blue alert","Orange alert","Red alert","Water level","Live storage","Storage %","Average inflow","Total outflow (daily average)","Spillway release","Rainfall"],"Value":[dam.get("frl",float("nan")),dam.get("rule_level",float("nan")),dam.get("blue_level",float("nan")),dam.get("orange_level",float("nan")),dam.get("red_level",float("nan")),dam.get("water_level",float("nan")),dam.get("live_storage",float("nan")),dam.get("storage_pct",float("nan")),dam.get("inflow",float("nan")),dam.get("outflow",float("nan")),dam.get("spillway_release",float("nan")),dam.get("rainfall",float("nan"))],"Unit":["m","m","m","m","m","m","MCM","%","m³/s","m³/s","m³/s","mm"]})
        st.dataframe(factors,use_container_width=True,hide_index=True)
        st.markdown('<div class="hs-note">Published reservoir observations are source data. The ML forecast and hydraulic simulation are analytical layers; neither autonomously controls gates nor issues official warnings.</div>',unsafe_allow_html=True)

# ============================================================
# AUTHORITY STRUCTURAL SAFETY
# ============================================================
elif st.session_state.page=="Structural Safety":
    if not st.session_state.authority:
        st.session_state.page="Authority Access"; st.rerun()

    st.markdown('<div class="hs-section">Authority Structural Safety</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    st.markdown(
        '<div class="hs-note"><b>Evidence-based screening.</b> This page does not invent crack, seepage, deformation or material values. It combines documented public safety-audit evidence with any actual structural/instrumentation CSV supplied to HYDROSCOPE and current reservoir loading from the KSEB/KSDMA data layer. It is not a certified dam-safety assessment or a dam-failure probability.</div>',
        unsafe_allow_html=True
    )

    name=st.selectbox("Select Dam",AUTHORITY_DAM_OPTIONS,key="struct_dam")
    dam=authority_dam_record(name)
    render_dam_profile(name,dam)
    evidence=structural_evidence(name,dam)

    st.markdown('<div class="hs-section">Structural Evidence Status</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    a,b,c,d=st.columns(4)
    a.metric("Dam age",f"{evidence['age']} years")
    b.metric("Safety-audit record","Documented" if evidence["audit"] else "Not linked")
    c.metric("Structural time-series",f"{evidence['history_rows']} records")
    d.metric("Analysis state",evidence["data_status"])

    availability_rows=[
        ("Inspection / safety-audit record", "Documented" if evidence["audit"] else "No linked structured record"),
        ("Crack measurements", "Loaded from structural CSV" if "crack_width" in evidence["history"].columns and evidence["history"]["crack_width"].notna().any() else "No measurement series loaded"),
        ("Seepage / leakage", "Loaded from structural CSV" if "seepage" in evidence["history"].columns and evidence["history"]["seepage"].notna().any() else "No measurement series loaded"),
        ("Deformation / movement", "Loaded from structural CSV" if "deformation" in evidence["history"].columns and evidence["history"]["deformation"].notna().any() else "No measurement series loaded"),
        ("Uplift / pore pressure", "Loaded from structural CSV" if (("uplift" in evidence["history"].columns and evidence["history"]["uplift"].notna().any()) or ("pore_pressure" in evidence["history"].columns and evidence["history"]["pore_pressure"].notna().any())) else "No measurement series loaded"),
        ("Material strength / condition", "Loaded from structural CSV" if "material_strength" in evidence["history"].columns and evidence["history"]["material_strength"].notna().any() else "No measurement series loaded"),
        ("Historical trend series", "Available" if evidence["history_rows"] else ("Documentary only" if evidence["audit"] or evidence["mullaperiyar"] else "Not available")),
    ]
    st.dataframe(pd.DataFrame(availability_rows,columns=["Parameter","Status"]),use_container_width=True,hide_index=True)

    st.markdown('<div class="hs-section">Documented Inspection / Safety Evidence</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    if evidence["audit"]:
        st.success("Government of India / DRIP record: this dam appears in the safety-audit list covering preparatory activities from November 2018 to November 2021.")
        st.markdown(f'<div class="hs-note">Record type: <b>Safety audit / inspection activity documented</b><br>Scope: Government of India DRIP-II / DRIP-III preparatory safety audits<br>Source: <a href="{STRUCTURAL_AUDIT_SOURCE_URL}" target="_blank">official Rajya Sabha annexure</a></div>',unsafe_allow_html=True)
    else:
        st.info("No linked DRIP safety-audit entry is currently mapped to this registry record in the connected public source. This does not mean the dam has never been inspected; it means the record is not mapped in this prototype.")
    if evidence["mullaperiyar"]:
        st.markdown(f'<div class="hs-note" style="margin-top:10px">Mullaperiyar also has a public Kerala Expert Group report dated 22 Nov 2011 with historical observations on seepage information, leaching deposits and piezometer instrumentation. <a href="{MULLAPERIYAR_REPORT_URL}" target="_blank">Open report</a></div>',unsafe_allow_html=True)

    st.markdown('<div class="hs-section">Current Reservoir Loading</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    loading_cols=st.columns(5)
    def _fmt(v,suffix=""):
        try:
            v=float(v)
            return f"{v:.2f}{suffix}" if np.isfinite(v) else "—"
        except Exception:
            return "—"
    loading_cols[0].metric("Water level",_fmt(dam.get("water_level")," m"))
    loading_cols[1].metric("Storage",_fmt(dam.get("storage_pct")," %"))
    loading_cols[2].metric("Inflow",_fmt(dam.get("inflow")," m³/s"))
    loading_cols[3].metric("Outflow",_fmt(dam.get("outflow")," m³/s"))
    loading_cols[4].metric("Rainfall",_fmt(dam.get("rainfall")," mm"))
    if dam.get("data_available"):
        st.caption(f"Reservoir observation: {dam.get('observed_at','')} · Source: KSEB/KSDMA published data")
    else:
        st.caption("No connected operational reservoir observation for this dam; registry information is still shown.")

    st.markdown('<div class="hs-section">Structural History & ML Anomaly Screening</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    uploaded=st.file_uploader(
        "Upload an authorised structural/instrumentation history CSV",
        type=["csv"],
        key="structural_csv_upload",
        help="Expected columns: dam, date, seepage, uplift, pore_pressure, deformation, crack_width, material_strength, reservoir_level"
    )
    uploaded_df=None
    if uploaded is not None:
        try:
            uploaded_df=pd.read_csv(uploaded)
            cols={str(c).strip().lower():str(c) for c in uploaded_df.columns}
            uploaded_df=uploaded_df.rename(columns={v:k for k,v in cols.items()})
            if "dam" not in uploaded_df.columns:
                st.error("The uploaded CSV must contain a 'dam' column.")
                uploaded_df=None
            else:
                uploaded_df["dam"]=uploaded_df["dam"].astype(str).str.strip()
                uploaded_df["date"]=pd.to_datetime(uploaded_df.get("date",pd.Series(dtype=str)),errors="coerce",dayfirst=True)
                for col in STRUCTURAL_NUMERIC_COLUMNS:
                    if col not in uploaded_df.columns:
                        uploaded_df[col]=np.nan
                    uploaded_df[col]=pd.to_numeric(uploaded_df[col],errors="coerce")
        except Exception as ex:
            st.error(f"Unable to read the uploaded structural dataset: {ex}")
            uploaded_df=None

    selected_history=structural_history_for_dam(name,uploaded_df)
    if not selected_history.empty:
        st.success(f"{len(selected_history)} structural/instrumentation records loaded for {name}.")
        show_cols=[c for c in ["date"]+STRUCTURAL_NUMERIC_COLUMNS if c in selected_history.columns and selected_history[c].notna().any()]
        if show_cols:
            st.dataframe(selected_history[show_cols].tail(15),use_container_width=True,hide_index=True)
        ml=structural_ml_anomaly(selected_history)
        if ml["available"]:
            s1,s2,s3=st.columns(3)
            s1.metric("ML method","Isolation Forest")
            s2.metric("Features used",str(len(ml["features"])))
            s3.metric("Latest record", "Anomaly flag" if ml["latest_anomaly"] else "Within learned pattern")
            if ml["latest_anomaly"]:
                st.warning("The latest multivariate structural observation is anomalous relative to the supplied historical record. This is an anomaly flag, not a prediction of dam failure.")
            else:
                st.info("The latest multivariate structural observation is within the learned historical pattern. Continue engineering monitoring and review.")
        else:
            st.info(ml["reason"])
    else:
        st.info("No structured structural/instrumentation time-series is loaded for this dam. The module will analyze actual measurements once an authorised history file is supplied.")

    if evidence["mullaperiyar"]:
        st.markdown('<div class="hs-section">Mullaperiyar Historical Structural Evidence</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
        st.caption(f"Source: Kerala Expert Group report · {MULLAPERIYAR_EVIDENCE['report_date']}")
        for item in MULLAPERIYAR_EVIDENCE["observations"]:
            st.markdown(f'<div class="hs-note" style="margin-bottom:8px">{item}</div>',unsafe_allow_html=True)

    st.markdown('<div class="hs-section">Documented Safety-Evidence Sources</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    sources=pd.DataFrame({
        "Source":["Government of India / DRIP safety-audit list","CWC Safety Inspection Guidelines","CWC Manual for Assessing Structural Safety","KSDMA Dam Management / EAP framework"],
        "Use in HYDROSCOPE":["Identifies dams with documented DRIP safety-audit activity","Defines inspection observations and monitoring needs","Defines structural assessment and instrumentation context","Provides dam-specific rule-curve and EAP framework"],
    })
    if evidence["mullaperiyar"]:
        sources.loc[len(sources)]=["Kerala Expert Group — Mullaperiyar report (2011)","Historical structural observations for Mullaperiyar"]
    st.dataframe(sources,use_container_width=True,hide_index=True)

    st.markdown('<div class="hs-section">Potential Downstream Impact if Dam Breaks</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    zones=DOWNSTREAM_ZONES.get(name,["Downstream river corridor","Nearby low-lying areas"])
    st.markdown('<div class="hs-note"><b>Hypothetical impact view:</b> the listed corridors are screening locations only. Exact inundation boundaries require the dam-specific hydraulic model, verified terrain/GIS and the approved Emergency Action Plan.</div>',unsafe_allow_html=True)
    zone_cols=st.columns(2)
    for i,zone in enumerate(zones):
        with zone_cols[i%2]:
            st.markdown(f'<div class="hs-card" style="min-height:110px;margin-bottom:14px"><div class="hs-card-label">Potential impact area {i+1}</div><div class="hs-card-title">{zone}</div><p class="hs-card-copy">Review against the dam-specific hydraulic scenario and approved EAP.</p></div>',unsafe_allow_html=True)

    st.caption(f"Official safety-audit source: {STRUCTURAL_AUDIT_SOURCE_URL}")

# ============================================================
# AUTHORITY HYDRAULIC SIMULATION
# ============================================================
elif st.session_state.page=="Hydraulic Simulation":
    if not st.session_state.authority:
        st.session_state.page="Authority Access"; st.rerun()
    st.markdown('<div class="hs-section">Authority Hydraulic Simulation</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
    st.markdown('<div class="hs-note">Restricted technical scenario analysis. The current solver is an educational prototype and is not an operational flood forecast.</div>',unsafe_allow_html=True)
    name=st.selectbox("Dam",AUTHORITY_DAM_OPTIONS,key="hyd_dam")
    dam=authority_dam_record(name)
    if not dam["data_available"]:
        st.info(f"{name} is in the authority registry. Reservoir telemetry and hydraulic geometry are not connected for this dam in the current prototype, so the 2-D solver cannot be run without inventing inputs.")
        render_dam_profile(name,dam)
        st.markdown('<div class="hs-section">Potential Downstream Impact</div><div class="hs-section-line"></div>',unsafe_allow_html=True)
        zones=DOWNSTREAM_ZONES.get(name,["Downstream river corridor","Nearby low-lying areas"])
        zone_cols=st.columns(2)
        for i,zone in enumerate(zones):
            with zone_cols[i%2]:
                st.markdown(f'<div class="hs-card" style="min-height:110px;margin-bottom:14px"><div class="hs-card-label">Potential impact area {i+1}</div><div class="hs-card-title">{zone}</div><p class="hs-card-copy">Hypothetical area for review; exact flood extent requires verified terrain and dam-specific modelling.</p></div>',unsafe_allow_html=True)
        st.markdown('<div class="hs-note">The hydraulic controls remain available for dams with connected prototype reservoir inputs. For this dam, the registry profile and potential downstream areas are shown without fabricating hydraulic results.</div>',unsafe_allow_html=True)
    else:
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
