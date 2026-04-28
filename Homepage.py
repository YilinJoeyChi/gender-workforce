import streamlit as st
import pandas as pd

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Visualizing Global Patterns in the Global Workforce",
    layout="wide"
)

# ── Load data ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("gender_clean.csv")
    df_raw = pd.read_csv("gender.csv")
    return df, df_raw

df, df_raw = load_data()

# ── Homepage ──────────────────────────────────────────────────
st.title("Visualizing Global Patterns in the Global Workforce")