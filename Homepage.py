import streamlit as st
import pandas as pd
import plotly.graph_objects as go

@st.cache_data
def load_data():
    df = pd.read_csv("gender_clean.csv")
    df_raw = pd.read_csv("gender.csv")
    return df, df_raw

df, df_raw = load_data()

# ── Hero Section ──────────────────────────────────────────────
st.markdown("""
<div style='text-align: center; padding: 40px 0 20px 0;'>
    <h1 style='font-size: 2.8em; font-weight: 700; margin-bottom: 8px;'>
        Visualizing Global Patterns in the Global Workforce
""", unsafe_allow_html=True)

st.divider()

# ── Key Global Stats ──────────────────────────────────────────
st.markdown("<h2 style='text-align: center;'>By the Numbers</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: grey;'>Global averages across all available data</p>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Global Female LFP Rate", "47.2%", help="Labor Force Participation Rate, avg 2000–2022")
col2.metric("Global Male LFP Rate", "72.8%", help="Labor Force Participation Rate, avg 2000–2022")
col3.metric("Avg Gender Wage Gap", "12.4%", help="Gender Wage Gap by Occupation, avg 2000–2022")
col4.metric("Countries Analyzed", "182", help="Countries with labor force participation data")

st.divider()

# ── Introduction ──────────────────────────────────────────────
col_intro, col_space = st.columns([2, 1])
with col_intro:
    st.markdown("## Introduction")
    st.markdown("""
What does gender inequality in the global workforce look like? 
When reading numbers, it is hard to immediately grasp the scale of inequality. 
This project designs visualizations that make gender disparities easy to understand for everyone.

📎 [Access the IMF Dataset](https://data.imf.org/en/Data-Explorer?datasetUrn=IMF.STA:GS_LI(1.0.0))
""")

st.divider()

# ── Dataset Overview ──────────────────────────────────────────
st.markdown("<h2 style='text-align: center;'>Dataset Overview</h2>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center;'>
        <h2 style='color: #1f77b4; margin: 0;'>51,200</h2>
        <p style='color: #555; margin: 4px 0 0 0;'>Total Rows</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center;'>
        <h2 style='color: #1f77b4; margin: 0;'>227</h2>
        <p style='color: #555; margin: 4px 0 0 0;'>Countries Covered</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center;'>
        <h2 style='color: #1f77b4; margin: 0;'>1950–2026</h2>
        <p style='color: #555; margin: 4px 0 0 0;'>Years Available</p>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center;'>
        <h2 style='color: #1f77b4; margin: 0;'>16+</h2>
        <p style='color: #555; margin: 4px 0 0 0;'>Indicators</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

st.divider()

# ── Visualization Overview ────────────────────────────────────
st.markdown("<h2 style='text-align: center;'>What's Inside</h2>", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

pages = [
    ("01", "Labor Force Participation", "#a7afff"),
    ("02", "Wages", "#ffd69c"),
    ("03", "Unemployment", "#b7e1ff"),
    ("04", "Part-Time & Informal Work", "#ffd4e4"),
    ("05", "Cross-Indicator Analysis", "#d4f0d4"),
]

for col, (num, title, color) in zip([col1, col2, col3, col4, col5], pages):
    with col:
        st.markdown(f"""
        <div style='background-color: {color}; padding: 20px; border-radius: 10px; height: 120px;'>
            <p style='font-size: 1.6em; font-weight: 700; margin: 0; color: #333;'>{num}</p>
            <p style='font-weight: 600; margin: 6px 0; color: #333;'>{title}</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Methodology ───────────────────────────────────────────────
st.markdown("## Methodology")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
**Data Cleaning**
The raw IMF dataset was filtered and reshaped from wide to long format, 
covering 206 countries from 2000 to 2022 for most indicators.

**Aggregation**
Country-level data was averaged across years to produce regional and global summaries.
""")
with col2:
    st.markdown("""
**Visualization**
All interactive charts were built using Plotly and Streamlit. 
Maps use ISO3 country codes for choropleth rendering.

**Gap Calculation**
Gender gaps are calculated as the absolute difference between 
female and male rates unless otherwise noted.
""")