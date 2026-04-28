import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import pycountry

st.set_page_config(page_title="Labor Force Participation", layout="wide")

# ── Tab 1: change colors here ──────────────────
COLOR_FEMALE = "#a7afff"   
COLOR_MALE = "#ffd69c"

@st.cache_data
def load_data():
    df = pd.read_csv("gender_clean.csv")
    df_raw = pd.read_csv("gender.csv")
    return df, df_raw

df, df_raw = load_data()

@st.cache_data
def prepare_lfp(_df_raw, _df):
    year_cols = [str(y) for y in range(1990, 2024)]
    id_cols = ["COUNTRY", "GENDER", "INDICATOR", "GS_MS", "AGE_GROUP",
               "UNIT", "GS_LI_DS", "GS_LI_EA", "GS_LI_ED", "GS_LI_OCC"]
    df_long = _df_raw.melt(id_vars=id_cols, value_vars=year_cols,
        var_name="YEAR", value_name="VALUE")
    df_long["YEAR"] = df_long["YEAR"].astype(int)
    df_long = df_long.dropna(subset=["VALUE"])
    region_map = _df[["COUNTRY", "REGION"]].drop_duplicates()
    df_long = df_long.merge(region_map, on="COUNTRY", how="left")
    return df_long

df_long = prepare_lfp(df_raw, df)

lfp_ext = df_long[
    (df_long["INDICATOR"] == "Labor Force Participation, Modeled ILO Estimate, Rate") &
    (df_long["AGE_GROUP"] == "15+ yrs") &
    (df_long["GS_MS"] == "Not Applicable") &
    (df_long["GENDER"].isin(["Female", "Male"]))
]

# ── iso3 function ─────────────────────────────────────────────
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
        'Central African Republic': 'CAF', 'Fiji, Republic of': 'FJI',
        'Madagascar, Republic of': 'MDG', 'Slovenia, Republic of': 'SVN',
        'Croatia, Republic of': 'HRV', 'Lithuania, Republic of': 'LTU',
        'Latvia, Republic of': 'LVA', 'Estonia, Republic of': 'EST',
        'Uzbekistan, Republic of': 'UZB', 'Timor-Leste, Democratic Republic of': 'TLS',
        "Hong Kong Special Administrative Region, People's Republic of China": 'HKG',
        "Macao Special Administrative Region, People's Republic of China": 'MAC',
        'Mauritania, Islamic Republic of': 'MRT',
    }
    if name in overrides:
        return overrides[name]
    try:
        return pycountry.countries.search_fuzzy(name)[0].alpha_3
    except:
        return None

# ── Page title ────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align: center;'>Labor Force Participation</h1>",
    unsafe_allow_html=True
)
st.divider()

# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Gender Trends", "World Map"])

with tab1:
    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            regions = ["Global Average"] + sorted(df["REGION"].dropna().unique().tolist())
            selected_region = st.selectbox("Select Region", regions)
        with col2:
            year_range = st.slider("Year Range", 1990, 2023, (1990, 2023))
        with col3:
            chart_type = st.radio("Chart Type", ["Stacked Bar", "Grouped Bar", "Line"], horizontal=False)

    lfp_filtered = lfp_ext[lfp_ext["YEAR"].between(year_range[0], year_range[1])].copy()
    if selected_region != "Global Average":
        lfp_filtered = lfp_filtered[lfp_filtered["REGION"] == selected_region]

    lfp_avg = lfp_filtered.groupby(["YEAR", "GENDER"])["VALUE"].mean().reset_index()
    female_vals = lfp_avg[lfp_avg["GENDER"] == "Female"].sort_values("YEAR")
    male_vals = lfp_avg[lfp_avg["GENDER"] == "Male"].sort_values("YEAR")

    st.subheader(f"Female vs. Male Labor Force Participation — {selected_region}")

    fig = go.Figure()

    if chart_type == "Line":
        fig.add_trace(go.Scatter(
            x=male_vals["YEAR"], y=male_vals["VALUE"],
            name="Male", line=dict(color=COLOR_MALE, width=2.5), mode="lines",
            hovertemplate="<b>Male</b><br>Year: %{x}<br>Rate: %{y:.1f}%<extra></extra>"
        ))
        fig.add_trace(go.Scatter(
            x=female_vals["YEAR"], y=female_vals["VALUE"],
            name="Female", line=dict(color=COLOR_FEMALE, width=2.5),
            fill="tonexty", fillcolor="rgba(167, 175, 255, 0.2)", mode="lines",
            hovertemplate="<b>Female</b><br>Year: %{x}<br>Rate: %{y:.1f}%<extra></extra>"
        ))
        yaxis_settings = dict(
            title="Labor Force Participation Rate (%)",
            gridcolor="lightgrey", range=[20, 85],
            tickmode="linear", tick0=40, dtick=5
        )
    elif chart_type == "Grouped Bar":
        fig.add_trace(go.Bar(
            x=female_vals["YEAR"], y=female_vals["VALUE"],
            name="Female", marker_color=COLOR_FEMALE,
            hovertemplate="<b>Female</b><br>Year: %{x}<br>Rate: %{y:.1f}%<extra></extra>"
        ))
        fig.add_trace(go.Bar(
            x=male_vals["YEAR"], y=male_vals["VALUE"],
            name="Male", marker_color=COLOR_MALE,
            hovertemplate="<b>Male</b><br>Year: %{x}<br>Rate: %{y:.1f}%<extra></extra>"
        ))
        yaxis_settings = dict(
            title="Labor Force Participation Rate (%)",
            gridcolor="lightgrey", range=[0, 80],
            tickmode="linear", tick0=0, dtick=10
        )
    elif chart_type == "Stacked Bar":
        fig.add_trace(go.Bar(
            x=female_vals["YEAR"], y=female_vals["VALUE"],
            name="Female", marker_color=COLOR_FEMALE,
            hovertemplate="<b>Female</b><br>Year: %{x}<br>Rate: %{y:.1f}%<extra></extra>"
        ))
        fig.add_trace(go.Bar(
            x=male_vals["YEAR"], y=male_vals["VALUE"],
            name="Male", marker_color=COLOR_MALE,
            hovertemplate="<b>Male</b><br>Year: %{x}<br>Rate: %{y:.1f}%<extra></extra>"
        ))
        yaxis_settings = dict(
            title="Labor Force Participation Rate (%)",
            gridcolor="lightgrey", range=[0, 140],
            tickmode="linear", tick0=0, dtick=10
        )

    fig.update_layout(
        barmode="stack" if chart_type == "Stacked Bar" else "group",
        height=520, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Arial", size=13),
        xaxis=dict(title="Year", tickmode="linear", dtick=1,
                   tickangle=45, gridcolor="lightgrey"),
        yaxis=yaxis_settings,
        legend=dict(title="Gender", bgcolor="white",
                    bordercolor="lightgrey", borderwidth=1),
        hovermode="x unified", margin=dict(t=30)
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Gender Gap in Labor Force Participation by Country")

    # ── Step 1: Filter data ───────────────────────────────────
    lfp_map = df[
        (df["INDICATOR"] == "Labor Force Participation, Modeled ILO Estimate, Rate") &
        (df["AGE_GROUP"] == "15+ yrs") &
        (df["GS_MS"] == "Not Applicable") &
        (df["GENDER"].isin(["Female", "Male"]))
    ].groupby(["COUNTRY", "REGION", "GENDER"])["VALUE"].mean().unstack().reset_index()
    lfp_map.columns.name = None

    # ── Step 2: Calculate gap ─────────────────────────────────
    lfp_map["gap"] = (lfp_map["Female"] - lfp_map["Male"]).abs()
    lfp_map = lfp_map.dropna(subset=["gap"])

    # ── Step 3: Add ISO3 country codes ───────────────────────
    lfp_map["code"] = lfp_map["COUNTRY"].apply(iso3)
    lfp_map = lfp_map.dropna(subset=["code"])

    # ── Step 4: Bin the gap into discrete categories ──────────
    bins   = [0, 15, 30, 45, 60, 100]
    labels = ["0–15", "15–30", "30–45", "45–60", "60+"]
    lfp_map["gap_group"] = pd.cut(
        lfp_map["gap"], bins=bins, labels=labels, include_lowest=True
    )

    color_map = {
        "0–15":  "#ffe3e3",
        "15–30": "#ffb8b8",
        "30–45": "#ff5b5b",
        "45–60": "#ae1111",
        "60+":   "#3d0000",
    }

    # ── Step 5: Build the map ─────────────────────────────────
    fig_map = px.choropleth(
        lfp_map,
        locations="code",
        color="gap_group",
        hover_name="COUNTRY",
        color_discrete_map=color_map,
        category_orders={"gap_group": labels},
        labels={"gap_group": "Gender gap (percentage points)"},
        hover_data={"code": False, "gap": ":.1f"}
    )

    # ── Step 6: Style the map layout ─────────────────────────
    fig_map.update_layout(
        height=600,
        dragmode=False,
        geo=dict(
            showframe=False,
            showcoastlines=False,
            showland=True,
            landcolor="#d9d9d9",
            showocean=True,
            oceancolor="#ddeeff",
            showlakes=False,
            projection_type="equirectangular",
            showcountries=True,
            countrycolor="white",
            countrywidth=0.5,
        ),
        legend=dict(
            title="Gender gap (percentage points)",
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.05,
            yanchor="top",
            font=dict(size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="white",
        font=dict(family="Arial", size=13),
        margin=dict(t=10, b=100, l=0, r=0),
    )

    st.plotly_chart(fig_map, use_container_width=True)
    st.caption("Gap = |Female − Male| participation rate | Average 2000–2022 | Grey = no data")


