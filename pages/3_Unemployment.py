import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import pycountry

st.set_page_config(page_title="Unemployment", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("gender_clean.csv")

df = load_data()

def iso3(name):
    overrides = {
        'Korea, Republic of': 'KOR', 'Russian Federation': 'RUS',
        'Yemen, Republic of': 'YEM', 'Ethiopia, The Federal Democratic Republic of': 'ETH',
        'Belarus, Republic of': 'BLR', 'Iran, Islamic Republic of': 'IRN',
        'Tanzania, United Republic of': 'TZA', 'Congo, Democratic Republic of the': 'COD',
        'Venezuela, República Bolivariana de': 'VEN', 'Türkiye, Republic of': 'TUR',
        'Mozambique, Republic of': 'MOZ', 'Moldova, Republic of': 'MDA',
        'Kosovo, Republic of': 'XKX', 'Tajikistan, Republic of': 'TJK',
        'Kazakhstan, Republic of': 'KAZ', 'Armenia, Republic of': 'ARM',
        'Azerbaijan, Republic of': 'AZE', 'Serbia, Republic of': 'SRB',
        'Netherlands, The': 'NLD', 'Poland, Republic of': 'POL',
        'Afghanistan, Islamic Republic of': 'AFG', 'Egypt, Arab Republic of': 'EGY',
        'Slovak Republic': 'SVK', 'Kyrgyz Republic': 'KGZ',
        "Lao People's Democratic Republic": 'LAO', 'Syrian Arab Republic': 'SYR',
        'Cabo Verde': 'CPV', "Cote d'Ivoire": 'CIV',
        'Gambia, The': 'GMB', 'Bahrain, Kingdom of': 'BHR',
        'Eswatini, Kingdom of': 'SWZ', 'North Macedonia, Republic of': 'MKD',
        'West Bank and Gaza': 'PSE', 'South Sudan, Republic of': 'SSD',
        'Brunei Darussalam': 'BRN', 'Lesotho, Kingdom of': 'LSO',
        'Vietnam': 'VNM', 'Congo, Republic of': 'COG',
        'Central African Republic': 'CAF',
    }
    if name in overrides:
        return overrides[name]
    try:
        return pycountry.countries.search_fuzzy(name)[0].alpha_3
    except:
        return None

st.markdown("<h1 style='text-align: center;'>Unemployment</h1>", unsafe_allow_html=True)

# ── Key Statistics ────────────────────────────────────────────
st.markdown("### Key Findings")

unemp_all = df[
    (df["INDICATOR"] == "Unemployment Rate , Rate") &
    (df["AGE_GROUP"] == "Not Applicable") &
    (df["GS_MS"] == "Total") &
    (df["GENDER"].isin(["Female", "Male"]))
].copy()

global_female_unemp = unemp_all[unemp_all["GENDER"] == "Female"]["VALUE"].mean()
global_male_unemp = unemp_all[unemp_all["GENDER"] == "Male"]["VALUE"].mean()
global_gap_unemp = global_female_unemp - global_male_unemp
latest_female = unemp_all[(unemp_all["GENDER"] == "Female") & (unemp_all["YEAR"] == 2022)]["VALUE"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Female Unemployment", f"{global_female_unemp:.1f}%")
col2.metric("Avg Male Unemployment", f"{global_male_unemp:.1f}%")
col3.metric("Avg Gender Gap", f"{global_gap_unemp:.1f} pts")
col4.metric("Latest Female Rate (2022)", f"{latest_female:.1f}%")

st.divider()

# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Gender Trends", "Diverging Bar & Sparklines"])

# ══════════════════════════════════════════════════════════════
# TAB 1 — Gender Trends
# ══════════════════════════════════════════════════════════════
with tab1:
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            regions = ["Global Average"] + sorted(df["REGION"].dropna().unique().tolist())
            selected_region = st.selectbox("Select Region", regions)
        with col2:
            year_range = st.slider("Year Range", 1990, 2023, (1990, 2023))

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

    unemp_wide = unemp_avg.pivot(
        index="YEAR", columns="GENDER", values="VALUE"
    ).reset_index()
    unemp_wide.columns.name = None

    st.subheader(f"Female vs Male Unemployment Rate — {selected_region}")

    st.area_chart(
        unemp_wide,
        x="YEAR",
        y=["Female", "Male"],
        color=["#ffd4e4", "#3daeff"],
        y_label="Unemployment Rate (%)",
        x_label="Year"
    )

# ══════════════════════════════════════════════════════════════
# TAB 2 — Animated Map & Diverging Bar
# ══════════════════════════════════════════════════════════════
with tab2:
    unemp_viz = df[
        (df["INDICATOR"] == "Unemployment Rate , Rate") &
        (df["AGE_GROUP"] == "Not Applicable") &
        (df["GS_MS"] == "Total") &
        (df["GENDER"].isin(["Female", "Male"]))
    ].copy()

    with st.container(border=True):
        div_year = st.selectbox("Select Year", sorted(unemp_viz["YEAR"].unique(), reverse=True), key="div_year")

    st.subheader("Gender Unemployment Gap by Country")
    st.markdown("Bars going **right** = women have higher unemployment. Bars going **left** = men have higher unemployment.")

    # ── Sparklines by Region ──────────────────────────────────
    st.markdown("#### Gender Gap Trend by Region")
    st.markdown("How the female−male unemployment gap changed over time in each region.")

    region_gap_time = unemp_viz.groupby(["YEAR", "REGION", "GENDER"])["VALUE"].mean().unstack().reset_index()
    region_gap_time.columns.name = None
    region_gap_time["gap"] = region_gap_time["Female"] - region_gap_time["Male"]
    region_gap_time = region_gap_time.dropna(subset=["gap"])

    all_regions = sorted(region_gap_time["REGION"].dropna().unique())

    for i in range(0, len(all_regions), 3):
        cols = st.columns(3)
        for j, region in enumerate(all_regions[i:i+3]):
            with cols[j]:
                rdata = region_gap_time[region_gap_time["REGION"] == region].sort_values("YEAR")

                fig_spark = go.Figure()
                fig_spark.add_trace(go.Scatter(
                    x=rdata["YEAR"],
                    y=rdata["gap"],
                    mode="lines",
                    line=dict(color="#74c878", width=2),
                    fill="tozeroy",
                    fillcolor="rgba(61, 174, 255, 0.1)",
                    hovertemplate="Year: %{x}<br>Gap: %{y:.1f} pts<extra></extra>"
                ))

                selected_row = rdata[rdata["YEAR"] == div_year]
                if not selected_row.empty:
                    fig_spark.add_trace(go.Scatter(
                        x=selected_row["YEAR"],
                        y=selected_row["gap"],
                        mode="markers",
                        marker=dict(size=8, color="#ff7dc7"),
                        hovertemplate=f"Selected: {div_year}<br>Gap: %{{y:.1f}} pts<extra></extra>"
                    ))

                fig_spark.add_hline(y=0, line_dash="dash", line_color="grey", line_width=1)

                fig_spark.update_layout(
                    height=150,
                    title=dict(text=region, font=dict(size=11), x=0.5),
                    plot_bgcolor="white", paper_bgcolor="white",
                    margin=dict(t=30, b=20, l=30, r=10),
                    xaxis=dict(showgrid=False, showticklabels=True,
                               tickmode="linear", dtick=5, tickfont=dict(size=8)),
                    yaxis=dict(showgrid=False, showticklabels=True,
                               tickfont=dict(size=8)),
                    showlegend=False
                )
                st.plotly_chart(fig_spark, use_container_width=True)

    st.divider()

    # ── Diverging Bar ─────────────────────────────────────────
    div_data = unemp_viz[unemp_viz["YEAR"] == div_year].copy()
    div_pivot = div_data.pivot_table(
        index="COUNTRY", columns="GENDER", values="VALUE"
    ).reset_index()
    div_pivot.columns.name = None
    div_pivot = div_pivot.dropna(subset=["Female", "Male"])
    div_pivot["gap"] = div_pivot["Female"] - div_pivot["Male"]
    div_pivot = div_pivot.sort_values("gap")

    div_pivot["color"] = div_pivot["gap"].apply(
        lambda x: "#ffb4d3" if x > 0 else "#57ca5c"
    )

    fig_div = go.Figure()
    fig_div.add_trace(go.Bar(
        x=div_pivot["gap"],
        y=div_pivot["COUNTRY"],
        orientation="h",
        marker_color=div_pivot["color"],
        hovertemplate="<b>%{y}</b><br>Gap: %{x:.1f} pts<extra></extra>"
    ))

    fig_div.add_vline(x=0, line_width=1.5, line_color="black")

    fig_div.update_layout(
        height=max(600, len(div_pivot) * 18),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Arial", size=11),
        xaxis=dict(
            title="Female − Male Unemployment Gap (percentage points)",
            gridcolor="lightgrey", zeroline=False
        ),
        yaxis=dict(showgrid=False),
        margin=dict(l=150, r=40, t=30, b=40)
    )

    st.plotly_chart(fig_div, use_container_width=True)
    st.caption(f"Positive = women have higher unemployment | Negative = men have higher unemployment | {div_year}")