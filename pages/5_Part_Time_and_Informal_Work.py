import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Part-Time & Informal Work", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("gender_clean.csv")

df = load_data()

st.markdown(
    "<h1 style='text-align: center;'>Part-Time & Informal Work</h1>",
    unsafe_allow_html=True
)
st.divider()

tab1, tab2 = st.tabs(
    ["Part-Time Employment", "Informal Employment"]
)

# ══════════════════════════════════════════════════════════════
# TAB 1 — Part-Time Employment
# ══════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════
# TAB 2 — Informal Employment
# ══════════════════════════════════════════════════════════════
