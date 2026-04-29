import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Gender Wage", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("gender_clean.csv")

df = load_data()

st.markdown("<h1 style='text-align: center;'>Gender Wage Gap</h1>", unsafe_allow_html=True)
st.divider()

# ── Key Statistics ────────────────────────────────────────────
st.markdown("### Key Findings")

# Global average wage gap
global_gap = df[
    (df["INDICATOR"] == "Gender Wage Gap by Occupation, Rate") &
    (df["GS_LI_OCC"] == "Total (By ICSO 08 Classification)")
]["VALUE"].mean()

# Latest year gap (2022)
latest_gap = df[
    (df["INDICATOR"] == "Gender Wage Gap by Occupation, Rate") &
    (df["GS_LI_OCC"] == "Total (By ICSO 08 Classification)") &
    (df["YEAR"] == 2022)
]["VALUE"].mean()

# Private sector wage ratio
private_ratio = df[
    df["INDICATOR"] == "Female To Male Wage Ratio, Private Sector, Mean"
]["VALUE"].mean()

# Public sector wage ratio
public_ratio = df[
    df["INDICATOR"] == "Female To Male Wage Ratio, Public Sector, Mean"
]["VALUE"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Gender Wage Gap", f"{global_gap:.1f}%")
col2.metric("Latest Gap (2022)", f"{latest_gap:.1f}%")
col3.metric("Private Sector Ratio", f"{private_ratio:.2f}")
col4.metric("Public Sector Ratio", f"{public_ratio:.2f}")

st.divider()

selected_region = "All Regions"

base = df[
    (df["INDICATOR"] == "Gender Wage Gap by Occupation, Rate") &
    (df["GS_LI_OCC"] == "Total (By ICSO 08 Classification)")
].copy()

tab1, tab2 = st.tabs(["Animated Over Time", "Private vs Public Sector"])

# ══════════════════════════════════════════════════════════════
# TAB 1 — Global Gender Wage Gap Over Time
# ══════════════════════════════════════════════════════════════

with tab1:
    st.subheader("Global Gender Wage Gap Over Time")

    with st.container(border=True):
        regions_t1 = ["All Regions"] + sorted(df["REGION"].dropna().unique().tolist())
        selected_region_t1 = st.selectbox("Select Region", regions_t1, key="region_t1")

    anim_data = df[
        (df["INDICATOR"] == "Gender Wage Gap by Occupation, Rate") &
        (df["GS_LI_OCC"] == "Total (By ICSO 08 Classification)")
    ].copy()
    anim_data = anim_data.dropna(subset=["VALUE"])

    if selected_region_t1 != "All Regions":
        anim_data = anim_data[anim_data["REGION"] == selected_region_t1]

    if selected_region_t1 == "Central Asia":
        st.warning("Central Asia has limited wage gap data and cannot be displayed. Please select another region.")
    else:
        global_trend = (
            anim_data.groupby("YEAR", as_index=False)["VALUE"]
            .mean()
            .sort_values("YEAR")
        )

        fig_anim = px.bar(
            global_trend,
            x="VALUE",
            y=["Global Average"] * len(global_trend),
            animation_frame="YEAR",
            orientation="h",
            range_x=[
                global_trend["VALUE"].min() - 2,
                global_trend["VALUE"].max() + 2
            ],
            text=global_trend["VALUE"].round(1),
            labels={"VALUE": "Gender Wage Gap (%)"},
            title="Global Gender Wage Gap Over Time"
                if selected_region_t1 == "All Regions"
                else f"{selected_region_t1} — Gender Wage Gap Over Time"
        )

        fig_anim.update_traces(
            marker_color="#0095ff",
            texttemplate="%{text:.1f}%",
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Year: %{customdata[0]}<br>Gap: %{x:.1f}%<extra></extra>",
            customdata=global_trend[["YEAR"]]
        )

        fig_anim.update_layout(
            height=500,
            plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
            font=dict(family="Arial", size=13),
            xaxis=dict(title="Gender Wage Gap (%)", showgrid=True,
                       gridcolor="rgba(0,0,0,0.08)"),
            yaxis=dict(title="", showgrid=False),
            margin=dict(l=100, r=80, t=60, b=40),
            showlegend=False
        )

        try:
            fig_anim.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 800
            fig_anim.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 400
        except IndexError:
            pass

        fig_anim.add_vline(x=0, line_width=2, line_color="black", line_dash="dash")
        st.plotly_chart(fig_anim, use_container_width=True)

        st.markdown("### Trend Line")
        fig_line = go.Figure()

        fig_line.add_trace(go.Scatter(
            x=global_trend["YEAR"],
            y=global_trend["VALUE"],
            mode="lines+markers",
            line=dict(color="#0095ff", width=3),
            marker=dict(size=7, color="#0095ff"),
            hovertemplate="<b>Year:</b> %{x}<br><b>Gap:</b> %{y:.1f}%<extra></extra>"
        ))
        
        data_range = global_trend["VALUE"].max() - global_trend["VALUE"].min()
        dtick = 2 if data_range < 20 else 5 if data_range < 40 else 10  
        
        fig_line.update_layout(
            height=450,
            plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
            font=dict(family="Arial", size=13),
            xaxis=dict(title="Year", tickmode="linear", dtick=1,
                       tickangle=45, gridcolor="rgba(0,0,0,0.08)"),
            yaxis=dict(
                title="Gender Wage Gap (%)",
                gridcolor="rgba(0,0,0,0.08)",
                range=[
                    global_trend["VALUE"].min() - 4,   # ← dynamic min
                    global_trend["VALUE"].max() + 4    # ← dynamic max
                    ],
                    autorange=False,
                    tickmode="linear",
                    dtick=dtick
                ),
            margin=dict(l=60, r=40, t=30, b=40)
        )

        st.plotly_chart(fig_line, use_container_width=True)

with tab2:
    st.info("Coming soon!")
# ══════════════════════════════════════════════════════════════
# TAB 2 — Private vs Public Sector
# ══════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Female-to-Male Wage Ratio: Private vs Public Sector")
    st.markdown("A ratio of **1.0** means perfect equality. Below 1.0 means women earn less than men.")

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            regions3 = ["Global Average"] + sorted(df["REGION"].dropna().unique().tolist())
            selected_region3 = st.selectbox("Select Region", regions3, key="region3")
        with col2:
            chart_type3 = st.radio("Chart Type", ["Line", "Bar"],
                                   horizontal=True, key="chart3")

    # Filter by region
    if selected_region3 != "Global Average":
        private_vals = df[
            (df["INDICATOR"] == "Female To Male Wage Ratio, Private Sector, Mean") &
            (df["REGION"] == selected_region3)
        ].groupby("YEAR")["VALUE"].mean().reset_index()

        public_vals = df[
            (df["INDICATOR"] == "Female To Male Wage Ratio, Public Sector, Mean") &
            (df["REGION"] == selected_region3)
        ].groupby("YEAR")["VALUE"].mean().reset_index()
    else:
        private_vals = df[
            df["INDICATOR"] == "Female To Male Wage Ratio, Private Sector, Mean"
        ].groupby("YEAR")["VALUE"].mean().reset_index()

        public_vals = df[
            df["INDICATOR"] == "Female To Male Wage Ratio, Public Sector, Mean"
        ].groupby("YEAR")["VALUE"].mean().reset_index()

    private_vals = private_vals.sort_values("YEAR")
    public_vals = public_vals.sort_values("YEAR")

    fig3 = go.Figure()

    if chart_type3 == "Line":
        fig3.add_trace(go.Scatter(
            x=private_vals["YEAR"], y=private_vals["VALUE"],
            name="Private Sector",
            line=dict(color="#ff9989", width=2.5), mode="lines",
            hovertemplate="<b>Private</b><br>Year: %{x}<br>Ratio: %{y:.3f}<extra></extra>"
        ))
        fig3.add_trace(go.Scatter(
            x=public_vals["YEAR"], y=public_vals["VALUE"],
            name="Public Sector",
            line=dict(color="#8bcfff", width=2.5), mode="lines",
            fill="tonexty", fillcolor="rgba(31, 119, 180, 0.1)",
            hovertemplate="<b>Public</b><br>Year: %{x}<br>Ratio: %{y:.3f}<extra></extra>"
        ))
    else:
        fig3.add_trace(go.Bar(
            x=private_vals["YEAR"], y=private_vals["VALUE"],
            name="Private Sector", marker_color="#ff9989",
            hovertemplate="<b>Private</b><br>Year: %{x}<br>Ratio: %{y:.3f}<extra></extra>"
        ))
        fig3.add_trace(go.Bar(
            x=public_vals["YEAR"], y=public_vals["VALUE"],
            name="Public Sector", marker_color="#8bcfff",
            hovertemplate="<b>Public</b><br>Year: %{x}<br>Ratio: %{y:.3f}<extra></extra>"
        ))

    fig3.update_layout(
        height=520, plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        font=dict(family="Arial", size=13),
        barmode="group",
        xaxis=dict(title="Year", tickmode="linear", dtick=1,
                   tickangle=45, gridcolor="lightgrey"),
        yaxis=dict(title="Female-to-Male Wage Ratio",
                   gridcolor="lightgrey", range=[0.6, 1.1],
                   tickmode="linear", tick0=0.6, dtick=0.05),
        legend=dict(title="Sector", bgcolor="white",
                    bordercolor="lightgrey", borderwidth=1),
        hovermode="x unified", margin=dict(t=30)
    )

    st.plotly_chart(fig3, use_container_width=True)