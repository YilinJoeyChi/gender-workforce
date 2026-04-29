import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import numpy as np

st.set_page_config(page_title="Cross Indicator Analysis", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("gender_clean.csv")

df = load_data()

st.markdown("<h1 style='text-align: center;'>Cross-Indicator Analysis</h1>", unsafe_allow_html=True)
st.divider()

# ── Prepare combined data ─────────────────────────────────────
@st.cache_data
def prepare_combined(_df):
    lfp = _df[
        (_df["INDICATOR"] == "Labor Force Participation, Modeled ILO Estimate, Rate") &
        (_df["AGE_GROUP"] == "15+ yrs") &
        (_df["GS_MS"] == "Not Applicable") &
        (_df["GENDER"] == "Female")
    ].groupby("COUNTRY")["VALUE"].mean().rename("LFP")

    unemp = _df[
        (_df["INDICATOR"] == "Unemployment Rate , Rate") &
        (_df["AGE_GROUP"] == "Not Applicable") &
        (_df["GS_MS"] == "Total") &
        (_df["GENDER"] == "Female")
    ].groupby("COUNTRY")["VALUE"].mean().rename("Unemployment")

    wage = _df[
        (_df["INDICATOR"] == "Gender Wage Gap by Occupation, Rate") &
        (_df["GS_LI_OCC"] == "Total (By ICSO 08 Classification)")
    ].groupby("COUNTRY")["VALUE"].mean().rename("Wage Gap")

    parttime = _df[
        (_df["INDICATOR"] == "Part-Time Employment, Percent of total employment") &
        (_df["GENDER"] == "Female")
    ].groupby("COUNTRY")["VALUE"].mean().rename("Part-Time")

    informal = _df[
        (_df["INDICATOR"] == "Informal Employment by Economic Activity") &
        (_df["GS_LI_EA"] == "Total Agriculture and Non-agriculture") &
        (_df["GENDER"] == "Female")
    ].groupby("COUNTRY")["VALUE"].mean().rename("Informal")

    region = _df[["COUNTRY", "REGION"]].drop_duplicates()
    combined = pd.concat([lfp, unemp, wage, parttime, informal], axis=1).reset_index()
    combined = combined.merge(region, on="COUNTRY", how="left")
    return combined

combined = prepare_combined(df)
corr = combined[["LFP", "Unemployment", "Wage Gap", "Part-Time", "Informal"]].corr()

tab1, tab2 = st.tabs(["Scatter Plot", "Heatmap"])

# ══════════════════════════════════════════════════════════════
# TAB 1 — Scatter Plot
# ══════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Relationship Between Two Indicators")
    st.markdown("""
    **How to read this chart:**
    - Each dot = one country
    - X and Y axes = two indicators you select
    - Color = world region
    - Trend line = overall direction of relationship
    - Hover over a dot to see the country name
    """)    
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            x_axis = st.selectbox("X Axis", ["LFP", "Unemployment", "Wage Gap", "Part-Time", "Informal"], index=0)
        with col2:
            y_axis = st.selectbox("Y Axis", ["LFP", "Unemployment", "Wage Gap", "Part-Time", "Informal"], index=1)
        with col3:
            show_trend = st.checkbox("Show Trend Line", value=True)

    scatter_data = combined.dropna(subset=[x_axis, y_axis])

    fig_scatter = px.scatter(
        scatter_data,
        x=x_axis,
        y=y_axis,
        color="REGION",
        hover_name="COUNTRY",
        trendline="ols" if show_trend else None,
        labels={x_axis: x_axis, y_axis: y_axis, "REGION": "Region"},
    )

    corr_val = corr.loc[x_axis, y_axis]
    st.markdown(f"**Correlation:** `{corr_val:.2f}`")

    fig_scatter.update_traces(marker=dict(size=8, opacity=0.7))
    fig_scatter.update_layout(
        height=550,
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Arial", size=13),
        xaxis=dict(title=x_axis, gridcolor="lightgrey"),
        yaxis=dict(title=y_axis, gridcolor="lightgrey"),
        legend=dict(title="Region", bgcolor="white",
                    bordercolor="lightgrey", borderwidth=1),
        margin=dict(t=30)
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 2 — Heatmap
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Correlation Matrix")
    st.markdown("""
    **How to read this table:**
    - Values range from **-1** to **+1**
    - **+1** = perfect positive relationship
    - **-1** = perfect negative relationship
    - **0** = no relationship
    - Dark blue = strong positive | Dark red = strong negative
    """)
    fig_heat = px.imshow(
        corr.round(2),
        text_auto=True,
        color_continuous_scale=["#ffc6c6", "white", "#71c4ff"],
        zmin=-1, zmax=1,
        aspect="auto"
    )
    fig_heat.update_layout(
        height=400,
        paper_bgcolor="white",
        font=dict(family="Arial", size=13),
        margin=dict(t=30)
    )
    st.plotly_chart(fig_heat, use_container_width=True)