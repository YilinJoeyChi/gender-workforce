import streamlit as st
import pandas as pd

st.set_page_config(page_title="Unemployment", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("gender_clean.csv")

df = load_data()

st.markdown("<h1 style='text-align: center;'>Unemployment</h1>", unsafe_allow_html=True)
st.divider()

# ── Filters ───────────────────────────────────────────────────
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        regions = ["Global Average"] + sorted(df["REGION"].dropna().unique().tolist())
        selected_region = st.selectbox("Select Region", regions)
    with col2:
        year_range = st.slider("Year Range", 1990, 2023, (1990, 2023))

# ── Prepare data ──────────────────────────────────────────────
unemp = df[
    (df["INDICATOR"] == "Unemployment Rate , Rate") &
    (df["AGE_GROUP"] == "Not Applicable") &
    (df["GS_MS"] == "Total") &
    (df["GENDER"].isin(["Female", "Male"]))
].copy()

unemp = unemp[unemp["YEAR"].between(year_range[0], year_range[1])]

if selected_region != "Global Average":
    unemp = unemp[unemp["REGION"] == selected_region]

unemp_avg = unemp.groupby(["YEAR", "GENDER"])["VALUE"].mean().reset_index()

# Pivot to wide format — st.area_chart needs Female and Male as separate columns
unemp_wide = unemp_avg.pivot(
    index="YEAR", columns="GENDER", values="VALUE"
).reset_index()
unemp_wide.columns.name = None

# ── Chart ─────────────────────────────────────────────────────
st.subheader(f"Female vs Male Unemployment Rate — {selected_region}")

st.area_chart(
    unemp_wide,
    x="YEAR",
    y=["Female", "Male"],
    color=["#b7e1ff", "#3daeff"],
    y_label="Unemployment Rate (%)",
    x_label="Year"
)