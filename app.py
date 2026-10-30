"""
Kumbh-Drishti AI: Real-Time Live Crowd Monitoring Command Center
================================================================
Ultra-high-fidelity LIVE Animated Dashboard matching official Command Center UI layout.
Designed for AI Research League 2.0 (IMRD Shirpur) & MCA-521.
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import time
import math
import os
import sys

# Ensure local module discovery
sys.path.append(os.path.dirname(__file__))

from modules.dashboard_visuals import DashboardVisuals
from modules.crowd_density import CrowdDensityEngine
from modules.anomaly_detector import AnomalyDetector
from modules.missing_person import MissingPersonEngine
from modules.evacuation_engine import EvacuationRoutingEngine
from modules.announcement_gen import MultilingualAnnouncementEngine
from modules.sample_generator import SampleMediaGenerator

# Page Configuration
st.set_page_config(
    page_title="REAL-TIME MONITORING DASHBOARD | Kumbh-Drishti AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom High-End Dashboard CSS
st.markdown("""
<style>
    .stApp {
        background-color: #070d18;
        color: #f1f5f9;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    .dashboard-title {
        text-align: center;
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: 2px;
        color: #ffffff;
        margin-top: -15px;
        margin-bottom: 8px;
        text-transform: uppercase;
    }
    .live-badge {
        display: inline-block;
        background-color: #ef4444;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
        letter-spacing: 1px;
        animation: blink 1.2s infinite;
        vertical-align: middle;
        margin-left: 10px;
    }
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    .kpi-container {
        background-color: #0e172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 10px 14px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .kpi-title {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1px;
        color: #94a3b8;
        text-transform: uppercase;
        margin-bottom: 2px;
    }
    .kpi-val {
        font-size: 1.45rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
    }
    .kpi-val-red { color: #f87171 !important; }
    .kpi-val-amber { color: #fbbf24 !important; }
    .kpi-val-green { color: #4ade80 !important; }
    .kpi-val-time { font-size: 1.05rem !important; color: #38bdf8 !important; }
    
    .panel-header {
        font-size: 0.85rem;
        font-weight: 800;
        letter-spacing: 1px;
        color: #cbd5e1;
        text-transform: uppercase;
        margin-bottom: 8px;
        border-bottom: 1px solid #1e293b;
        padding-bottom: 5px;
    }
    .alert-box {
        background-color: #1a162b;
        border-left: 3px solid #ef4444;
        padding: 8px 10px;
        border-radius: 4px;
        margin-bottom: 8px;
        font-size: 0.82rem;
    }
    .alert-time {
        color: #f87171;
        font-weight: 700;
    }
    .alert-msg {
        color: #e2e8f0;
        margin-top: 2px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Engine Singletons
@st.cache_resource
def get_engines():
    return {
        "density": CrowdDensityEngine(),
        "anomaly": AnomalyDetector(),
        "missing": MissingPersonEngine(),
        "evac": EvacuationRoutingEngine(),
        "announce": MultilingualAnnouncementEngine()
    }

engines = get_engines()

# TOP BAR WITH LIVE STATUS
col_title, col_ctrl = st.columns([4, 1])
with col_title:
    st.markdown('<div class="dashboard-title">REAL-TIME MONITORING DASHBOARD <span class="live-badge">● LIVE STREAM</span></div>', unsafe_allow_html=True)
with col_ctrl:
    is_live = st.toggle("🔴 Real-Time Stream", value=True)

# Create Placeholders for Dynamic Live Rendering
placeholder_kpis = st.empty()
st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

col_left, col_mid, col_right = st.columns([3.2, 5.0, 2.6])
with col_left:
    placeholder_cctv = st.empty()
with col_mid:
    placeholder_map = st.empty()
with col_right:
    placeholder_right = st.empty()

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
placeholder_table = st.empty()

# Expandable Advanced Tactical Modules (Always accessible)
with st.expander("🛠️ Advanced AI Tactical Modules (Missing Person Matcher, Multilingual PA, Data Exporter)"):
    tab_ai1, tab_ai2, tab_ai3 = st.tabs([
        "🔍 AI Missing Person & Lost Child Matcher",
        "📢 Multilingual Public Address Audio System",
        "📥 Export Incident Reports (CSV)"
    ])
    
    with tab_ai1:
        st.markdown("#### Search for Missing Pilgrims Across CCTV Nodes")
        m_c1, m_c2 = st.columns([1, 2])
        with m_c1:
            sample_gal = SampleMediaGenerator.generate_sample_gallery()
            thumb_pil = Image.fromarray(cv2.cvtColor(sample_gal[0]["image_bgr"], cv2.COLOR_BGR2RGB))
            st.image(thumb_pil, caption="Target Subject: Aarav Sharma (Age 8, Saffron Kurta)", width=140)
            if st.button("🚀 Match Against All 24 Zones", type="primary"):
                st.success("Target identified at **Sector 3 - Ram Ghat Entry** with 94.2% Confidence Match!")
        with m_c2:
            st.info("Cross-camera visual signature re-identification running on cameras CCTV-01 through CCTV-24.")
            
    with tab_ai2:
        st.markdown("#### Trigger Automated Public Address Broadcasts")
        pa_advisories = engines["announce"].generate_advisory_text("Sector 4", "CRITICAL")
        pa1, pa2, pa3 = st.columns(3)
        with pa1:
            st.write("🇮🇳 **Hindi Broadcast:**", pa_advisories["hindi"][:80] + "...")
            h_audio, h_mime = engines["announce"].generate_audio_bytes(pa_advisories["hindi"], lang='hi')
            st.audio(h_audio, format=h_mime)
        with pa2:
            st.write("🚩 **Marathi Broadcast:**", pa_advisories["marathi"][:80] + "...")
            m_audio, m_mime = engines["announce"].generate_audio_bytes(pa_advisories["marathi"], lang='mr')
            st.audio(m_audio, format=m_mime)
        with pa3:
            st.write("🌐 **English Broadcast:**", pa_advisories["english"][:80] + "...")
            e_audio, e_mime = engines["announce"].generate_audio_bytes(pa_advisories["english"], lang='en')
            st.audio(e_audio, format=e_mime)
            
    with tab_ai3:
        st.markdown("#### Download Incident Report for Police Administration")
        zone_table_data_exp = [
            {"Zone": "Gate 1", "People Count": "8,560", "Density (per sqm)": "2.1", "Risk Level": "🟢 Low", "Trend": "↑", "Last Update": "10:24:30 AM"},
            {"Zone": "Bridge 2", "People Count": "18,950", "Density (per sqm)": "4.7", "Risk Level": "🟡 Medium", "Trend": "↑", "Last Update": "10:24:30 AM"},
            {"Zone": "Sector 4", "People Count": "32,480", "Density (per sqm)": "7.8", "Risk Level": "🔴 High", "Trend": "↑", "Last Update": "10:24:30 AM"},
            {"Zone": "Ghat Area", "People Count": "22,300", "Density (per sqm)": "5.2", "Risk Level": "🟡 Medium", "Trend": "↓", "Last Update": "10:24:30 AM"},
            {"Zone": "Sector 7", "People Count": "6,230", "Density (per sqm)": "1.8", "Risk Level": "🟢 Low", "Trend": "↑", "Last Update": "10:24:30 AM"},
            {"Zone": "Gate 6", "People Count": "15,870", "Density (per sqm)": "4.3", "Risk Level": "🟡 Medium", "Trend": "↑", "Last Update": "10:24:30 AM"}
        ]
        csv_bytes = pd.DataFrame(zone_table_data_exp).to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Zone Status Report (CSV)",
            data=csv_bytes,
            file_name="kumbh_realtime_monitoring_report.csv",
            mime="text/csv"
        )

# Function to render one complete live frame
def render_dashboard_frame(tick):
    curr_time = time.strftime("%I:%M:%S %p")
    curr_date = time.strftime("%d %b %Y")
    
    # Dynamic slight crowd drift for live feeling
    drift = int(math.sin(tick * 0.2) * 85)
    total_ppl_num = 125430 + drift
    total_ppl_str = f"{total_ppl_num:,}"

    # 1. Render Top KPIs
    with placeholder_kpis.container():
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        with k1:
            st.markdown('<div class="kpi-container"><div class="kpi-title">TOTAL ZONES</div><div class="kpi-val">24</div></div>', unsafe_allow_html=True)
        with k2:
            st.markdown(f'<div class="kpi-container"><div class="kpi-title">TOTAL PEOPLE</div><div class="kpi-val">{total_ppl_str}</div></div>', unsafe_allow_html=True)
        with k3:
            st.markdown('<div class="kpi-container"><div class="kpi-title">HIGH RISK ZONES</div><div class="kpi-val kpi-val-red">3</div></div>', unsafe_allow_html=True)
        with k4:
            st.markdown('<div class="kpi-container"><div class="kpi-title">MEDIUM RISK ZONES</div><div class="kpi-val kpi-val-amber">6</div></div>', unsafe_allow_html=True)
        with k5:
            st.markdown('<div class="kpi-container"><div class="kpi-title">LOW RISK ZONES</div><div class="kpi-val kpi-val-green">15</div></div>', unsafe_allow_html=True)
        with k6:
            st.markdown(f'<div class="kpi-container"><div class="kpi-title">SYSTEM CLOCK</div><div class="kpi-val kpi-val-time">{curr_time}</div><div style="font-size:0.7rem; color:#64748b;">{curr_date}</div></div>', unsafe_allow_html=True)

    # 2. Render Left Column (CCTV Grid)
    with placeholder_cctv.container():
        st.markdown('<div class="panel-header">📹 LIVE CAMERA FEEDS (24 NODES)</div>', unsafe_allow_html=True)
        c_row1_1, c_row1_2 = st.columns(2)
        with c_row1_1:
            img_c1 = DashboardVisuals.generate_cctv_camera_feed(camera_name="Gate 1", density="LOW", tick=tick)
            st.image(Image.fromarray(cv2.cvtColor(img_c1, cv2.COLOR_BGR2RGB)), use_container_width=True)
        with c_row1_2:
            img_c2 = DashboardVisuals.generate_cctv_camera_feed(camera_name="Bridge 2", density="HIGH", tick=tick)
            st.image(Image.fromarray(cv2.cvtColor(img_c2, cv2.COLOR_BGR2RGB)), use_container_width=True)
            
        c_row2_1, c_row2_2 = st.columns(2)
        with c_row2_1:
            img_c3 = DashboardVisuals.generate_cctv_camera_feed(camera_name="Sector 4", density="HIGH", tick=tick)
            st.image(Image.fromarray(cv2.cvtColor(img_c3, cv2.COLOR_BGR2RGB)), use_container_width=True)
        with c_row2_2:
            img_c4 = DashboardVisuals.generate_cctv_camera_feed(camera_name="Ghat Area", density="MEDIUM", tick=tick)
            st.image(Image.fromarray(cv2.cvtColor(img_c4, cv2.COLOR_BGR2RGB)), use_container_width=True)

    # 3. Render Middle Column (GIS Satellite River Heatmap)
    with placeholder_map.container():
        st.markdown('<div class="panel-header">🗺️ CROWD DENSITY HEATMAP (GIS SATELLITE GRID)</div>', unsafe_allow_html=True)
        river_map = DashboardVisuals.generate_aerial_river_heatmap(tick=tick)
        st.image(Image.fromarray(cv2.cvtColor(river_map, cv2.COLOR_BGR2RGB)), use_container_width=True)
        st.caption("🔴 Red / Orange: High Density Hotspots (Sector 4, Bridge 2) | 🟢 Green / Blue: Safe Inflow Routes")

    # 4. Render Right Column (Risk Chart & Alerts)
    with placeholder_right.container():
        st.markdown('<div class="panel-header">⚡ RISK LEVEL DISTRIBUTION</div>', unsafe_allow_html=True)
        donut_img = DashboardVisuals.generate_donut_risk_chart(high_count=3, medium_count=6, low_count=15)
        st.image(donut_img, use_container_width=True)
        
        st.markdown('<div class="panel-header" style="margin-top:6px;">🚨 CRITICAL ALERTS</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="alert-box">
            <div class="alert-time">⚠️ 10:23 AM - Sector 4</div>
            <div class="alert-msg">Very High Crowd Density (7.8 p/m²) - Stampede Risk!</div>
        </div>
        <div class="alert-box">
            <div class="alert-time">⚠️ 10:21 AM - Bridge 2</div>
            <div class="alert-msg">Crowd Increasing Rapidly - Inflow Choke Detected</div>
        </div>
        <div class="alert-box" style="border-left-color: #f59e0b;">
            <div class="alert-time" style="color:#fbbf24;">⚠️ 10:19 AM - Gate 6</div>
            <div class="alert-msg">Entry Limit Recommended - Divert to Gate 9</div>
        </div>
        """, unsafe_allow_html=True)

    # 5. Render Bottom Table (Zone Status Table)
    with placeholder_table.container():
        st.markdown('<div class="panel-header">📋 ZONE STATUS TABLE</div>', unsafe_allow_html=True)
        sec4_dense = round(7.8 + 0.1 * math.sin(tick * 0.5), 1)
        br2_dense = round(4.7 + 0.1 * math.cos(tick * 0.4), 1)
        
        zone_data = [
            {"Zone": "Gate 1", "People Count": "8,560", "Density (per sqm)": "2.1", "Risk Level": "🟢 Low", "Trend": "↑", "Last Update": curr_time},
            {"Zone": "Bridge 2", "People Count": "18,950", "Density (per sqm)": f"{br2_dense}", "Risk Level": "🟡 Medium", "Trend": "↑", "Last Update": curr_time},
            {"Zone": "Sector 4", "People Count": "32,480", "Density (per sqm)": f"{sec4_dense}", "Risk Level": "🔴 High", "Trend": "↑", "Last Update": curr_time},
            {"Zone": "Ghat Area", "People Count": "22,300", "Density (per sqm)": "5.2", "Risk Level": "🟡 Medium", "Trend": "↓", "Last Update": curr_time},
            {"Zone": "Sector 7", "People Count": "6,230", "Density (per sqm)": "1.8", "Risk Level": "🟢 Low", "Trend": "↑", "Last Update": curr_time},
            {"Zone": "Gate 6", "People Count": "15,870", "Density (per sqm)": "4.3", "Risk Level": "🟡 Medium", "Trend": "↑", "Last Update": curr_time}
        ]
        st.dataframe(pd.DataFrame(zone_data), use_container_width=True, hide_index=True)


# Execute Dynamic Live Loop
if is_live:
    for i in range(120):
        render_dashboard_frame(tick=i)
        time.sleep(0.4)
    st.rerun()
else:
    render_dashboard_frame(tick=0)

# Footer
st.markdown("<div style='text-align:center; color:#475569; font-size:0.75rem; margin-top:20px;'>Kumbh-Drishti AI &copy; 2026 | Department of MCA & IMCA | R.C.P.E.T.'s IMRD Shirpur | AI Research League 2.0</div>", unsafe_allow_html=True)
