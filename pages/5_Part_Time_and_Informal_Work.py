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

# ── Key Statistics ─────────────────────────────────────────────
st.markdown("### Key Findings")

pt_female = df[
    (df["INDICATOR"] == "Part-Time Employment, Percent of total employment") &
    (df["GENDER"] == "Female")
]["VALUE"].mean()

pt_male = df[
    (df["INDICATOR"] == "Part-Time Employment, Percent of total employment") &
    (df["GENDER"] == "Male")
]["VALUE"].mean()

inf_female = df[
    (df["INDICATOR"] == "Informal Employment by Economic Activity") &
    (df["GS_LI_EA"] == "Total Agriculture and Non-agriculture") &
    (df["GENDER"] == "Female")
]["VALUE"].mean()

inf_male = df[
    (df["INDICATOR"] == "Informal Employment by Economic Activity") &
    (df["GS_LI_EA"] == "Total Agriculture and Non-agriculture") &
    (df["GENDER"] == "Male")
]["VALUE"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Female Part-Time", f"{pt_female:.1f}%")
col2.metric("Avg Male Part-Time", f"{pt_male:.1f}%")
col3.metric("Avg Female Informal", f"{inf_female:.1f}%")
col4.metric("Avg Male Informal", f"{inf_male:.1f}%")

st.divider()

tab1, tab2 = st.tabs(["Part-Time Employment", "Informal Employment"])

# ══════════════════════════════════════════════════════════════
# TAB 1 — Part-Time Employment
# ══════════════════════════════════════════════════════════════
with tab1:
    st.markdown("""
    **How to read this tab:**
    - **Dumbbell chart** — each line shows the gap between female and male part-time rates per country
    - **Time slider** — drag to see how the gap changed over time
    """)

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            pt_year = st.slider("Select Year", 2000, 2022, 2022, key="pt_year")
        with col2:
            pt_region = st.selectbox("Select Region",
                ["All Regions"] + sorted(df["REGION"].dropna().unique().tolist()),
                key="pt_region")

    # Prepare data
    pt = df[
        (df["INDICATOR"] == "Part-Time Employment, Percent of total employment") &
        (df["AGE_GROUP"] == "Not Applicable") &
        (df["GS_MS"] == "Not Applicable") &
        (df["YEAR"] == pt_year)
    ].copy()

    if pt_region != "All Regions":
        pt = pt[pt["REGION"] == pt_region]

    pt_pivot = pt.pivot_table(
        index=["COUNTRY", "REGION"], columns="GENDER", values="VALUE"
    ).reset_index()
    pt_pivot.columns.name = None
    pt_pivot = pt_pivot.dropna(subset=["Female", "Male"])
    pt_pivot["gap"] = pt_pivot["Female"] - pt_pivot["Male"]
    pt_pivot = pt_pivot.sort_values("gap", ascending=False).head(30)

    # ── Dumbbell Chart ────────────────────────────────────────
    st.subheader(f"Female vs Male Part-Time Employment — {pt_year}")

    fig_db = go.Figure()

    for _, row in pt_pivot.iterrows():
        fig_db.add_shape(
            type="line",
            x0=row["Male"], x1=row["Female"],
            y0=row["COUNTRY"], y1=row["COUNTRY"],
            line=dict(color="lightgrey", width=2)
        )

    fig_db.add_trace(go.Scatter(
        x=pt_pivot["Male"], y=pt_pivot["COUNTRY"],
        mode="markers", name="Male",
        marker=dict(size=10, color="#a7afff"),
        hovertemplate="<b>%{y}</b><br>Male: %{x:.1f}%<extra></extra>"
    ))
    fig_db.add_trace(go.Scatter(
        x=pt_pivot["Female"], y=pt_pivot["COUNTRY"],
        mode="markers", name="Female",
        marker=dict(size=10, color="#ffd69c"),
        hovertemplate="<b>%{y}</b><br>Female: %{x:.1f}%<extra></extra>"
    ))

    fig_db.update_layout(
        height=700, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Arial", size=12),
        xaxis=dict(title="Part-Time Employment (%)", gridcolor="lightgrey"),
        yaxis=dict(categoryorder="total ascending", showgrid=False),
        legend=dict(bgcolor="white", bordercolor="lightgrey", borderwidth=1),
        margin=dict(l=150, r=40, t=30, b=40)
    )
    st.plotly_chart(fig_db, use_container_width=True)
    st.caption(f"Top 30 countries by female−male gap | {pt_year}")

    # ── Small Multiples — Regional Trend ──────────────────────
    st.subheader("Part-Time Employment Trend by Region")
    st.markdown("How female part-time employment changed over time in each region.")

    pt_trend = df[
        (df["INDICATOR"] == "Part-Time Employment, Percent of total employment") &
        (df["AGE_GROUP"] == "Not Applicable") &
        (df["GS_MS"] == "Not Applicable") &
        (df["GENDER"].isin(["Female", "Male"]))
    ].groupby(["YEAR", "REGION", "GENDER"])["VALUE"].mean().reset_index()

    all_regions = sorted(pt_trend["REGION"].dropna().unique())

    for i in range(0, len(all_regions), 3):
        cols = st.columns(3)
        for j, region in enumerate(all_regions[i:i+3]):
            with cols[j]:
                rdata = pt_trend[pt_trend["REGION"] == region]
                f_data = rdata[rdata["GENDER"] == "Female"].sort_values("YEAR")
                m_data = rdata[rdata["GENDER"] == "Male"].sort_values("YEAR")

                fig_sm = go.Figure()
                fig_sm.add_trace(go.Scatter(
                    x=m_data["YEAR"], y=m_data["VALUE"],
                    mode="lines", name="Male",
                    line=dict(color="#a7afff", width=1.5)
                ))
                fig_sm.add_trace(go.Scatter(
                    x=f_data["YEAR"], y=f_data["VALUE"],
                    mode="lines", name="Female",
                    line=dict(color="#ffd69c", width=1.5),
                    fill="tonexty",
                    fillcolor="rgba(255, 214, 156, 0.15)"
                ))
                fig_sm.update_layout(
                    height=150,
                    title=dict(text=region, font=dict(size=10), x=0.5),
                    plot_bgcolor="white", paper_bgcolor="white",
                    margin=dict(t=30, b=20, l=30, r=10),
                    xaxis=dict(showgrid=False, tickmode="linear",
                               dtick=5, tickfont=dict(size=8)),
                    yaxis=dict(showgrid=False, tickfont=dict(size=8)),
                    showlegend=False
                )
                st.plotly_chart(fig_sm, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 2 — Informal Employment
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    **How to read this tab:**
    - **Lollipop chart** — countries with the largest female informal employment gap
    - **Scatter plot** — relationship between informal and part-time work by country
    """)

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            inf_year = st.slider("Select Year", 2000, 2022, 2022, key="inf_year")
        with col2:
            inf_activity = st.selectbox("Activity Type", [
                "Total Agriculture and Non-agriculture",
                "Agriculture",
                "Non-agriculture"
            ], key="inf_activity")

    # Prepare data
    inf = df[
        (df["INDICATOR"] == "Informal Employment by Economic Activity") &
        (df["AGE_GROUP"] == "Not Applicable") &
        (df["GS_LI_EA"] == inf_activity) &
        (df["YEAR"] == inf_year)
    ].copy()

    inf_pivot = inf.pivot_table(
        index=["COUNTRY", "REGION"], columns="GENDER", values="VALUE"
    ).reset_index()
    inf_pivot.columns.name = None
    inf_pivot = inf_pivot.dropna(subset=["Female", "Male"])
    inf_pivot["gap"] = inf_pivot["Female"] - inf_pivot["Male"]
    inf_pivot = inf_pivot.sort_values("gap", ascending=False).head(25)

    # ── Lollipop Chart ────────────────────────────────────────
    st.subheader(f"Top 25 — Female vs Male Informal Employment ({inf_year})")

    fig_lol = go.Figure()

    for _, row in inf_pivot.iterrows():
        fig_lol.add_shape(
            type="line",
            x0=row["Male"], x1=row["Female"],
            y0=row["COUNTRY"], y1=row["COUNTRY"],
            line=dict(color="lightgrey", width=2)
        )

    fig_lol.add_trace(go.Scatter(
        x=inf_pivot["Male"], y=inf_pivot["COUNTRY"],
        mode="markers", name="Male",
        marker=dict(size=10, color="#a7afff"),
        hovertemplate="<b>%{y}</b><br>Male: %{x:.1f}%<extra></extra>"
    ))
    fig_lol.add_trace(go.Scatter(
        x=inf_pivot["Female"], y=inf_pivot["COUNTRY"],
        mode="markers", name="Female",
        marker=dict(size=10, color="#ffd69c"),
        hovertemplate="<b>%{y}</b><br>Female: %{x:.1f}%<extra></extra>"
    ))

    fig_lol.update_layout(
        height=650, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Arial", size=12),
        xaxis=dict(title="Informal Employment (%)", gridcolor="lightgrey"),
        yaxis=dict(categoryorder="total ascending", showgrid=False),
        legend=dict(bgcolor="white", bordercolor="lightgrey", borderwidth=1),
        margin=dict(l=150, r=40, t=30, b=40)
    )
    st.plotly_chart(fig_lol, use_container_width=True)

    # ── Scatter Plot ──────────────────────────────────────────
    st.subheader("Informal vs Part-Time Employment by Country")
    st.markdown("Does high informal employment correlate with high part-time work?")

    scatter_gender = st.radio("Gender", ["Female", "Male"],
                              horizontal=True, key="scatter_gender")

    pt_scatter = df[
        (df["INDICATOR"] == "Part-Time Employment, Percent of total employment") &
        (df["AGE_GROUP"] == "Not Applicable") &
        (df["GS_MS"] == "Not Applicable") &
        (df["GENDER"] == scatter_gender) &
        (df["YEAR"] == inf_year)
    ][["COUNTRY", "VALUE"]].rename(columns={"VALUE": "Part-Time"})

    inf_scatter = df[
        (df["INDICATOR"] == "Informal Employment by Economic Activity") &
        (df["AGE_GROUP"] == "Not Applicable") &
        (df["GS_LI_EA"] == "Total Agriculture and Non-agriculture") &
        (df["GENDER"] == scatter_gender) &
        (df["YEAR"] == inf_year)
    ][["COUNTRY", "REGION", "VALUE"]].rename(columns={"VALUE": "Informal"})

    scatter_data = pt_scatter.merge(inf_scatter, on="COUNTRY").dropna()

    fig_sc = px.scatter(
        scatter_data,
        x="Part-Time",
        y="Informal",
        color="REGION",
        hover_name="COUNTRY",
        trendline="ols",
        labels={
            "Part-Time": "Part-Time Employment (%)",
            "Informal": "Informal Employment (%)"
        }
    )
    fig_sc.update_traces(marker=dict(size=9, opacity=0.8))
    fig_sc.update_layout(
        height=500,
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Arial", size=13),
        xaxis=dict(gridcolor="lightgrey"),
        yaxis=dict(gridcolor="lightgrey"),
        legend=dict(title="Region", bgcolor="white",
                    bordercolor="lightgrey", borderwidth=1),
        margin=dict(t=30)
    )
    st.plotly_chart(fig_sc, use_container_width=True)
    st.caption(f"Data: {inf_year} | Source: IMF Gender Statistics")