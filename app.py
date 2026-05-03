# ============================================================
# IMPORTS
# ============================================================

from dash import html, dcc, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pycountry
import dash
import pandas as pd
import dash_bootstrap_components as dbc


# ============================================================
# APP SETUP
# ============================================================

app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;900&display=swap"
])
server = app.server

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv("gender_clean.csv")
df_raw = pd.read_csv("gender.csv")


# ============================================================
# GLOBAL STYLE VARIABLES
# ============================================================

BG = "#ffffff"
CARD_BG = "#fbf4e6"
PRIMARY = "#000000"
TEXT = "#a08070"
ACCENT = "#8faf8f"

COLOR_FEMALE = "#fbe6ef"   
COLOR_MALE = "#ceecce"     
GRID = "#f9f8fd"


# ============================================================
# SHARED COMPONENT STYLES
# ============================================================

nav_bar = {
    "textAlign": "center",
    "marginTop": "30px",
    "marginBottom": "40px"
}

nav_link = {
    "display": "inline-block",
    "margin": "8px",
    "padding": "8px 16px",
    "border": f"1px solid {PRIMARY}",
    "borderRadius": "20px",
    "color": PRIMARY,
    "textDecoration": "none",
    "fontWeight": "700"
}

section_style = {
    "padding": "80px 0",
    "borderTop": f"1px solid {PRIMARY}33"
}

section_title = {
    "textAlign": "center",
    "color": PRIMARY,
    "fontWeight": "700",
    "marginBottom": "20px"
}

# ============================================================
# HELPER FUNCTION: COUNTRY NAME TO ISO3 CODE
# ============================================================

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


# ============================================================
# DATA PREP: LABOR FORCE PARTICIPATION
# ============================================================

def prepare_lfp(df_raw, df):
    year_cols = [str(y) for y in range(1990, 2024)]

    id_cols = [
        "COUNTRY", "GENDER", "INDICATOR", "GS_MS", "AGE_GROUP",
        "UNIT", "GS_LI_DS", "GS_LI_EA", "GS_LI_ED", "GS_LI_OCC"
    ]

    df_long = df_raw.melt(
        id_vars=id_cols,
        value_vars=year_cols,
        var_name="YEAR",
        value_name="VALUE"
    )

    df_long["YEAR"] = df_long["YEAR"].astype(int)
    df_long = df_long.dropna(subset=["VALUE"])

    region_map = df[["COUNTRY", "REGION"]].drop_duplicates()
    df_long = df_long.merge(region_map, on="COUNTRY", how="left")

    return df_long


df_long = prepare_lfp(df_raw, df)

lfp_ext = df_long[
    (df_long["INDICATOR"] == "Labor Force Participation, Modeled ILO Estimate, Rate") &
    (df_long["AGE_GROUP"] == "15+ yrs") &
    (df_long["GS_MS"] == "Not Applicable") &
    (df_long["GENDER"].isin(["Female", "Male"]))
]

regions = ["Global Average"] + sorted(lfp_ext["REGION"].dropna().unique().tolist())

# ============================================================
# DATA PREP: CROSS INDICATOR COMBINED
# ============================================================

_lfp = df[
    (df["INDICATOR"] == "Labor Force Participation, Modeled ILO Estimate, Rate") &
    (df["AGE_GROUP"] == "15+ yrs") &
    (df["GS_MS"] == "Not Applicable") &
    (df["GENDER"] == "Female")
].groupby("COUNTRY")["VALUE"].mean().rename("LFP")

_unemp = df[
    (df["INDICATOR"] == "Unemployment Rate , Rate") &
    (df["AGE_GROUP"] == "Not Applicable") &
    (df["GS_MS"] == "Total") &
    (df["GENDER"] == "Female")
].groupby("COUNTRY")["VALUE"].mean().rename("Unemployment")

_wage = df[
    (df["INDICATOR"] == "Gender Wage Gap by Occupation, Rate") &
    (df["GS_LI_OCC"] == "Total (By ICSO 08 Classification)")
].groupby("COUNTRY")["VALUE"].mean().rename("Wage Gap")

_parttime = df[
    (df["INDICATOR"] == "Part-Time Employment, Percent of total employment") &
    (df["GENDER"] == "Female")
].groupby("COUNTRY")["VALUE"].mean().rename("Part-Time")

_informal = df[
    (df["INDICATOR"] == "Informal Employment by Economic Activity") &
    (df["GS_LI_EA"] == "Total Agriculture and Non-agriculture") &
    (df["GENDER"] == "Female")
].groupby("COUNTRY")["VALUE"].mean().rename("Informal")

_region = df[["COUNTRY", "REGION"]].drop_duplicates()
combined_data = pd.concat([_lfp, _unemp, _wage, _parttime, _informal], axis=1).reset_index()
combined_data = combined_data.merge(_region, on="COUNTRY", how="left")

# ============================================================
# MAIN APP LAYOUT
# ============================================================

app.layout = html.Div(
    style={
        "backgroundColor": BG,
        "minHeight": "100vh",
        "padding": "60px 80px",
        "fontFamily": "Playfair Display, serif",
        "color": TEXT
    },
    children=[

        # ======================================================
        # HERO SECTION
        # ======================================================
        html.H1(
            "GENDER TRENDS IN THE GLOBAL WORKFORCE",
            style={
                "textAlign": "center",
                "color": PRIMARY,
                "fontWeight": "900",
                "fontSize": "3.4em",
                "maxWidth": "1400px",
                "width": "100%",
                "margin": "0 auto",
                "lineHeight": "1.1",
                "letterSpacing": "-1px"
            }
        ),
        html.Hr(style={"borderColor": PRIMARY, "opacity": "0.3"}),


        # ======================================================
        # INTRODUCTION SECTION
        # ======================================================

        html.Div([
            html.P(
                """What does gender patterns in the global workforce look like? 
                This project presents  visualizations to make these disparities easier to understand.""",
                style={
                    "maxWidth": "750px",
                    "lineHeight": "1.8",
                    "fontSize": "1.1em",
                    "textAlign": "center",
                    "margin": "0 auto"
                }
            ),
        ], style={"padding": "40px 0"}),

        html.Hr(style={"borderColor": PRIMARY, "opacity": "0.3"}),


        # ======================================================
        # DATASET OVERVIEW SECTION
        # ======================================================

        html.Div(id="overview", children=[
            html.H2(
                "Dataset Overview",
                style={
                    "textAlign": "center",
                    "color": PRIMARY,
                    "fontWeight": "700",
                    "marginBottom": "30px"}
            ), 

            html.Div(
                html.A(
                    "📎 Access IMF Dataset",
                    href="https://data.imf.org/en/Data-Explorer?datasetUrn=IMF.STA:GS_LI(1.0.0)",
                    target="_blank",
                    style={
                        "color": PRIMARY,
                        "fontWeight": "700",
                        "textDecoration": "none",
                        "fontSize": "1em"
                    }
                ),
                style={"textAlign": "center", "marginBottom": "30px"}),

            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H3("51,200", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Rows")
                ]), style={
                    "backgroundColor": CARD_BG,
                    "textAlign": "center",
                    "border": f"1px solid {PRIMARY}33"
                })),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H3("227", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Countries")
                ]), style={
                    "backgroundColor": CARD_BG,
                    "textAlign": "center",
                    "border": f"1px solid {PRIMARY}33"
                })),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H3("1950–2026", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Years")
                ]), style={
                    "backgroundColor": CARD_BG,
                    "textAlign": "center",
                    "border": f"1px solid {PRIMARY}33"
                })),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H3("16+", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Indicators")
                ]), style={
                    "backgroundColor": CARD_BG,
                    "textAlign": "center",
                    "border": f"1px solid {PRIMARY}33"
                })),
            ], style={"marginBottom": "40px"}),


            # ==================================================
            # EXPLORE NAVIGATION MENU
            # ==================================================

            html.P(
                "Explore",
                style={
                    "textAlign": "center",
                    "color": PRIMARY,
                    "fontWeight": "700",
                    "letterSpacing": "2px",
                    "textTransform": "uppercase",
                    "fontSize": "0.9em",
                    "marginTop": "30px",
                    "marginBottom": "10px",
                    "opacity": "0.7"
                }
            ),

            html.Div([
                html.A("Overview", href="#overview", style=nav_link),
                html.A("Labor Force", href="#labor", style=nav_link),
                html.A("Wages", href="#wages", style=nav_link),
                html.A("Unemployment", href="#unemployment", style=nav_link),
                html.A("Part-Time Work & Informal Work", href="#part-time", style=nav_link),
                html.A("Cross-Indicator", href="#cross", style=nav_link),
            ], style=nav_bar),
        ]),


        # ======================================================
        # LABOR FORCE PARTICIPATION SECTION
        # ======================================================

        html.Div(id="labor", style=section_style, children=[
            html.H2("Labor Force Participation", style=section_title),

        # --------------------------------------------------
        # LFP KEY METRIC CARDS
        # --------------------------------------------------

            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(id="female-lfp", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Global Female LFP Rate")
                ]), style={
                    "backgroundColor": CARD_BG,
                    "textAlign": "center",
                    "border": f"1px solid {PRIMARY}33",
                    "height": "120px"
                })),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(id="male-lfp", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Global Male LFP Rate")
                ]), style={
                    "backgroundColor": CARD_BG,
                    "textAlign": "center",
                    "border": f"1px solid {PRIMARY}33",
                    "height": "120px"
                })),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(id="gap-lfp", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Global Gender Gap")
                ]), style={
                    "backgroundColor": CARD_BG,
                    "textAlign": "center",
                    "border": f"1px solid {PRIMARY}33",
                    "height": "120px"
                })),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(id="region-lfp", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Largest Gap Region")
                ]), style={
                    "backgroundColor": CARD_BG,
                    "textAlign": "center",
                    "border": f"1px solid {PRIMARY}33",
                    "height": "120px"
                })),
            ], className="my-4"),


            # --------------------------------------------------
            # LFP CONTROLS
            # --------------------------------------------------

            dbc.Row([
                dbc.Col([
                    html.Label("Select Region", style={"color": PRIMARY, "fontWeight": "700"}),
                    dcc.Dropdown(
                        id="lfp-region",
                        options=[{"label": r, "value": r} for r in regions],
                        value="Global Average",
                        clearable=False
                    ),
                ], width=3),

                dbc.Col([
                    html.Label("Year Range", style={"color": PRIMARY, "fontWeight": "700"}),
                    dcc.RangeSlider(
                        id="lfp-year",
                        min=1990,
                        max=2023,
                        value=[1990, 2023],
                        marks={y: str(y) for y in range(1990, 2024, 5)},
                        tooltip={"placement": "bottom"}
                    ),
                ], width=6),

                dbc.Col([
                    html.Label("Chart Type", style={"color": PRIMARY, "fontWeight": "700"}),
                    dcc.RadioItems(
                        id="lfp-chart-type",
                        options=["Grouped Bar", "Line", "Stacked Bar"],
                        value="Grouped Bar",
                        inputStyle={"marginRight": "6px"},
                        labelStyle={"marginRight": "14px"}
                    ),
                ], width=3),
            ], className="my-4"),


            # --------------------------------------------------
            # LFP TREND CHART
            # --------------------------------------------------
            dcc.Graph(id="lfp-trend-chart", style={"width": "100%"}),

            html.Div([
                html.P("💡 What does this chart tell us?",
                       style={"color": PRIMARY, "fontWeight": "700", "marginBottom": "8px", "fontSize": "0.95em"}),
                html.Ul([
                    html.Li("Male labor force participation (70%-75%) has consistently been about 20 to 25 percentage points higher than female (48%-52%) across the 1990-2023 period."),
                    html.Li("Male participation is slowly declining, while female participation is slowly rising."),
                ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8"}),
            ], style={"backgroundColor": CARD_BG, "padding": "16px 24px", "borderRadius": "8px", "marginTop": "16px", "marginBottom": "24px"}),

            html.Hr(style={"borderColor": PRIMARY, "opacity": "0.2"}),


            # --------------------------------------------------
            # LFP ANIMATED MAP
            # --------------------------------------------------
            html.H3(
                "Global Labor Force Participation Map",
                style={
                    "textAlign": "center",
                    "color": PRIMARY,
                    "marginTop": "40px",
                    "fontSize": "20px",
                    "fontFamily": "Playfair Display, serif"
                }
            ),

            dcc.RadioItems(
                id="lfp-anim-gender",
                options=["Female", "Male"],
                value="Female",
                inputStyle={"marginRight": "6px"},
                labelStyle={"marginRight": "16px"},
                style={"textAlign": "center", "marginBottom": "20px"}
            ),

            dcc.Graph(id="lfp-anim-map", style={"width": "100%"}),

            html.P(
                "Grey = no data | Source: IMF Gender Statistics | Age group: 15+",
                style={
                    "textAlign": "center",
                    "fontSize": "0.85em",
                    "opacity": "0.6"
                }
            ),
        ]),


        # ======================================================
        # WAGES SECTION
        # ======================================================

        html.Div(id="wages", style=section_style, children=[
            html.H2("Wages", style=section_title),

            # Key Metric Cards
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(id="wage-gap-avg", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Avg Gender Wage Gap")
                ]), style={"backgroundColor": CARD_BG, "textAlign": "center", "border": f"1px solid {PRIMARY}33", "height": "120px"})),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(id="wage-gap-latest", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Latest Gap (2022)")
                ]), style={"backgroundColor": CARD_BG, "textAlign": "center", "border": f"1px solid {PRIMARY}33", "height": "120px"})),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(id="wage-private", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Private Sector Ratio")
                ]), style={"backgroundColor": CARD_BG, "textAlign": "center", "border": f"1px solid {PRIMARY}33", "height": "120px"})),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(id="wage-public", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Public Sector Ratio")
                ]), style={"backgroundColor": CARD_BG, "textAlign": "center", "border": f"1px solid {PRIMARY}33", "height": "120px"})),
            ], className="my-4"),

            # Small multiples - one chart per region
            html.H3("Gender Wage Gap by Region Over Time", style={"textAlign": "center", "color": PRIMARY, "fontSize": "20px"}),
            html.P("X axis = Year   |   Y axis = Gender Wage Gap in percentage points",
                style={"textAlign": "center", "opacity": "0.6", "fontSize": "0.85em"}),
            html.P("Central Asia has limited data available.",
                style={"textAlign": "center", "opacity": "0.6", "fontSize": "0.9em", "fontStyle": "italic"}),
            html.Div(id="wage-region-small-multiples"),
            html.Div([
                html.P("💡 What does this chart tell us?",
                       style={"color": PRIMARY, "fontWeight": "700", "marginBottom": "8px", "fontSize": "0.95em"}),
                html.Ul([
                    html.Li("The average gender wage gap is 6.7%, with the latest figure in 2022 at 6.4%."),
                    html.Li("The Middle East & North Africa has had the largest gender wage gap, with gaps reaching 40% to 60%."),
                ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8"}),
            ], style={"backgroundColor": CARD_BG, "padding": "16px 24px", "borderRadius": "8px", "marginTop": "16px", "marginBottom": "24px"}),

            # Private vs Public
            html.H3("Private vs Public Sector Wage Ratio", style={"textAlign": "center", "color": PRIMARY, "fontSize": "20px", "marginTop": "40px"}),
            html.P("A ratio of 1.0 means perfect equality. Below 1.0 means women earn less than men.",
                   style={"textAlign": "center", "opacity": "0.7"}),

            dbc.Row([
                dbc.Col([
                    html.Label("Select Region", style={"color": PRIMARY, "fontWeight": "700"}),
                    dcc.Dropdown(
                        id="wage-sector-region",
                        options=[{"label": r, "value": r} for r in ["Global Average"] + sorted(df["REGION"].dropna().unique().tolist())],
                        value="Global Average",
                        clearable=False
                    ),
                ], width=4),
                dbc.Col([
                    html.Label("Chart Type", style={"color": PRIMARY, "fontWeight": "700"}),
                    dcc.RadioItems(
                        id="wage-sector-type",
                        options=["Line", "Bar"],
                        value="Line",
                        inputStyle={"marginRight": "6px"},
                        labelStyle={"marginRight": "14px"}
                    ),
                ], width=4),
            ], className="my-4"),

            dcc.Graph(id="wage-sector-chart"),

            html.Div([
                html.P("💡 What does this chart tell us?",
                       style={"color": PRIMARY, "fontWeight": "700", "marginBottom": "8px", "fontSize": "0.95em"}),
                html.Ul([
                    html.Li("The difference between public (~0.82–0.92) and private (~0.74–0.80) is approximately 5–10 percentage points in most years."),
                    html.Li("Progress is slow: the private sector moves from ~0.75 to ~0.79, and the public sector from ~0.85 to ~0.90. Progress exists, but neither sector is close to 1.0."),
                ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8"}),
            ], style={"backgroundColor": CARD_BG, "padding": "16px 24px", "borderRadius": "8px", "marginTop": "16px", "marginBottom": "24px"}),
        ]),

        # ======================================================
        # UNEMPLOYMENT SECTION
        # ======================================================

        html.Div(id="unemployment", style=section_style, children=[
            html.H2("Unemployment", style=section_title),

            # Key Metric Cards
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(id="unemp-female", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Avg Female Unemployment")
                ]), style={"backgroundColor": CARD_BG, "textAlign": "center", "border": f"1px solid {PRIMARY}33", "height": "120px"})),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(id="unemp-male", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Avg Male Unemployment")
                ]), style={"backgroundColor": CARD_BG, "textAlign": "center", "border": f"1px solid {PRIMARY}33", "height": "120px"})),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(id="unemp-gap", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Avg Gender Gap")
                ]), style={"backgroundColor": CARD_BG, "textAlign": "center", "border": f"1px solid {PRIMARY}33", "height": "120px"})),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(id="unemp-latest", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Latest Female Rate (2022)")
                ]), style={"backgroundColor": CARD_BG, "textAlign": "center", "border": f"1px solid {PRIMARY}33", "height": "120px"})),
            ], className="my-4"),

            # Gender Trends
            html.H3("Female vs Male Unemployment Rate Over Time", style={"textAlign": "center", "color": PRIMARY, "fontSize": "20px"}),
            dbc.Row([
                dbc.Col([
                    html.Label("Select Region", style={"color": PRIMARY, "fontWeight": "700"}),
                    dcc.Dropdown(
                        id="unemp-region",
                        options=[{"label": r, "value": r} for r in ["Global Average"] + sorted(df["REGION"].dropna().unique().tolist())],
                        value="Global Average",
                        clearable=False
                    ),
                ], width=4),
                dbc.Col([
                    html.Label("Year Range", style={"color": PRIMARY, "fontWeight": "700"}),
                    dcc.RangeSlider(
                        id="unemp-year",
                        min=1990, max=2023, value=[1990, 2023],
                        marks={y: str(y) for y in range(1990, 2024, 5)},
                        tooltip={"placement": "bottom"}
                    ),
                ], width=6),
            ], className="my-4"),
            dcc.Graph(id="unemp-trend-chart"),

            html.Hr(style={"borderColor": PRIMARY, "opacity": "0.2"}),

            # Sparklines
            html.H3("Gender Unemployment Gap by Region", style={"textAlign": "center", "color": PRIMARY, "fontSize": "20px", "marginTop": "40px"}),
            html.P("X axis = Year   |   Y axis = Female − Male unemployment gap (percentage points)",
                   style={"textAlign": "center", "opacity": "0.6", "fontSize": "0.85em"}),
            dbc.Row([
                dbc.Col([
                    html.Label("Select Year to Highlight", style={"color": PRIMARY, "fontWeight": "700"}),
                    dcc.Dropdown(
                        id="unemp-div-year",
                        options=[],
                        value=None,
                        clearable=False
                    ),
                ], width=3),
            ], className="my-3"),
            html.Div(id="unemp-sparklines"),

            html.Div([
                html.P("💡 What does this chart tell us?",
                       style={"color": PRIMARY, "fontWeight": "700", "marginBottom": "8px", "fontSize": "0.95em"}),
                html.Ul([
                    html.Li("Largest gaps: Middle East & North Africa has the largest positive gap, at approximately +7 to +8. Other regions with relatively large gaps include Latin America & Caribbean, South Asia, and Sub-Saharan Africa."),
                    html.Li("Smallest gaps: East & Southeast Asia, Russia & Caucasus, and Oceania have the smallest gaps, with values close to 0."),
                ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8"}),
            ], style={"backgroundColor": CARD_BG, "padding": "16px 24px", "borderRadius": "8px", "marginTop": "16px", "marginBottom": "24px"}),

            html.Hr(style={"borderColor": PRIMARY, "opacity": "0.2"}),

            # Diverging Bar
            html.H3("Gender Unemployment Gap by Country", style={"textAlign": "center", "color": PRIMARY, "fontSize": "20px", "marginTop": "40px"}),
            html.P("Pink = women have higher unemployment | Green = men have higher unemployment",
                   style={"textAlign": "center", "opacity": "0.7"}),
            dcc.Graph(id="unemp-diverging"),
        ]),


        # ======================================================
        # PART-TIME AND INFORMAL WORK SECTION
        # ======================================================
        html.Div(id="part-time", style=section_style, children=[
            html.H2("Part-Time & Informal Work", style=section_title),

            # Key Metric Cards
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(id="pt-female", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Avg Female Part-Time")
                ]), style={"backgroundColor": CARD_BG, "textAlign": "center", "border": f"1px solid {PRIMARY}33", "height": "120px"})),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(id="pt-male", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Avg Male Part-Time")
                ]), style={"backgroundColor": CARD_BG, "textAlign": "center", "border": f"1px solid {PRIMARY}33", "height": "120px"})),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(id="inf-female", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Avg Female Informal")
                ]), style={"backgroundColor": CARD_BG, "textAlign": "center", "border": f"1px solid {PRIMARY}33", "height": "120px"})),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(id="inf-male", style={"color": PRIMARY, "fontWeight": "900"}),
                    html.P("Avg Male Informal")
                ]), style={"backgroundColor": CARD_BG, "textAlign": "center", "border": f"1px solid {PRIMARY}33", "height": "120px"})),
            ], className="my-4"),

            html.Hr(style={"borderColor": PRIMARY, "opacity": "0.2"}),

            # Dumbbell Chart
            html.H3("Female vs Male Part-Time Employment by Country", style={"textAlign": "center", "color": PRIMARY, "fontSize": "20px"}),
            html.P("Each dot pair shows female (pink) and male (green) part-time rates. Top 30 countries by gap.",
                   style={"textAlign": "center", "opacity": "0.6", "fontSize": "0.85em"}),
            dbc.Row([
                dbc.Col([
                    html.Label("Select Year", style={"color": PRIMARY, "fontWeight": "700"}),
                    dcc.Slider(
                        id="pt-year",
                        min=2000, max=2022, value=2022, step=1,
                        marks={y: str(y) for y in range(2000, 2023, 5)},
                        tooltip={"placement": "bottom"}
                    ),
                ], width=6),
                dbc.Col([
                    html.Label("Select Region", style={"color": PRIMARY, "fontWeight": "700"}),
                    dcc.Dropdown(
                        id="pt-region",
                        options=[{"label": r, "value": r} for r in ["All Regions"] + sorted(df["REGION"].dropna().unique().tolist())],
                        value="All Regions",
                        clearable=False
                    ),
                ], width=4),
            ], className="my-4"),
            dcc.Graph(id="pt-dumbbell"),

            html.Div([
                html.P("💡 What does this chart tell us?",
                       style={"color": PRIMARY, "fontWeight": "700", "marginBottom": "8px", "fontSize": "0.95em"}),
                html.Ul([
                    html.Li("The largest gaps appear in countries such as the Netherlands, Iceland, Austria, Mozambique, and Norway."),
                    html.Li("The Netherlands stands out the most, with women's part-time employment reaching around 70% to 75%."),
                ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8"}),
            ], style={"backgroundColor": CARD_BG, "padding": "16px 24px", "borderRadius": "8px", "marginTop": "16px", "marginBottom": "24px"}),

            html.Hr(style={"borderColor": PRIMARY, "opacity": "0.2"}),

            # Small Multiples
            html.H3("Part-Time Employment Trend by Region", style={"textAlign": "center", "color": PRIMARY, "fontSize": "20px", "marginTop": "40px"}),
            html.P("How female and male part-time employment changed over time in each region.",
                   style={"textAlign": "center", "opacity": "0.6", "fontSize": "0.85em"}),
            html.Div([
                html.Span("● Male", style={"color": COLOR_MALE, "fontWeight": "600", "marginRight": "24px", "fontSize": "0.9em"}),
                html.Span("● Female", style={"color": COLOR_FEMALE, "fontWeight": "600", "fontSize": "0.9em"}),
            ], style={"textAlign": "center", "marginBottom": "12px"}),
            html.Div(id="pt-small-multiples"),

            html.Div([
                html.P("💡 What does this chart tell us?",
                       style={"color": PRIMARY, "fontWeight": "700", "marginBottom": "8px", "fontSize": "0.95em"}),
                html.Ul([
                    html.Li("Middle East & North Africa: Female 30–50%, male 10–20%. This region has one of the largest gender gaps."),
                    html.Li("Oceania: Female 45–60%, male 25–40%. This region has some of the highest part-time employment rates overall."),
                    html.Li("South Asia: Female 35–50%, male 15–25%. The gender gap is large, and the trends fluctuate over time."),
                    html.Li("Europe: Female 35–40%, male 20–25%. The gap is smaller than in some regions but remains stable over time."),
                    html.Li("Latin America & Caribbean / North America: Both regions show a noticeable spike around 2020, especially compared with their usual trends."),
                ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8"}),
            ], style={"backgroundColor": CARD_BG, "padding": "16px 24px", "borderRadius": "8px", "marginTop": "16px", "marginBottom": "24px"}),

            html.Hr(style={"borderColor": PRIMARY, "opacity": "0.2"}),

            # Lollipop Chart
            html.H3("Female vs Male Informal Employment by Country", style={"textAlign": "center", "color": PRIMARY, "fontSize": "20px", "marginTop": "40px"}),
            html.P("Top 25 countries by female−male informal employment gap.",
                   style={"textAlign": "center", "opacity": "0.6", "fontSize": "0.85em"}),
            dbc.Row([
                dbc.Col([
                    html.Label("Select Year", style={"color": PRIMARY, "fontWeight": "700"}),
                    dcc.Slider(
                        id="inf-year",
                        min=2000, max=2022, value=2022, step=1,
                        marks={y: str(y) for y in range(2000, 2023, 5)},
                        tooltip={"placement": "bottom"}
                    ),
                ], width=6),
                dbc.Col([
                    html.Label("Activity Type", style={"color": PRIMARY, "fontWeight": "700"}),
                    dcc.Dropdown(
                        id="inf-activity",
                        options=[
                            {"label": "Total Agriculture and Non-agriculture", "value": "Total Agriculture and Non-agriculture"},
                            {"label": "Agriculture", "value": "Agriculture"},
                            {"label": "Non-agriculture", "value": "Non-agriculture"},
                        ],
                        value="Total Agriculture and Non-agriculture",
                        clearable=False
                    ),
                ], width=4),
            ], className="my-4"),
            dcc.Graph(id="inf-lollipop"),

            html.Div([
                html.P("💡 What does this chart tell us?",
                       style={"color": PRIMARY, "fontWeight": "700", "marginBottom": "8px", "fontSize": "0.95em"}),
                html.Ul([
                    html.Li("Benin, Burkina Faso, Mali, and Senegal have the highest overall rates, meaning informal employment is very high for both genders."),
                ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8"}),
            ], style={"backgroundColor": CARD_BG, "padding": "16px 24px", "borderRadius": "8px", "marginTop": "16px", "marginBottom": "24px"}),

            html.Hr(style={"borderColor": PRIMARY, "opacity": "0.2"}),

            # Scatter Plot
            html.H3("Informal vs Part-Time Employment by Country", style={"textAlign": "center", "color": PRIMARY, "fontSize": "20px", "marginTop": "40px"}),
            html.P("Does high informal employment correlate with high part-time work?",
                   style={"textAlign": "center", "opacity": "0.6", "fontSize": "0.85em"}),
            dbc.Row([
                dbc.Col([
                    html.Label("Gender", style={"color": PRIMARY, "fontWeight": "700"}),
                    dcc.RadioItems(
                        id="scatter-gender",
                        options=["Female", "Male"],
                        value="Female",
                        inputStyle={"marginRight": "6px"},
                        labelStyle={"marginRight": "14px"}
                    ),
                ], width=4),
            ], className="my-3"),
            dcc.Graph(id="inf-scatter"),

            html.Div([
                html.P("💡 What does this chart tell us? (Female)",
                       style={"color": PRIMARY, "fontWeight": "700", "marginBottom": "8px", "fontSize": "0.95em"}),
                html.Ul([
                    html.Li("Sub-Saharan Africa and East & Southeast Asia show the strongest positive relationship: higher female part-time employment is linked with higher female informal employment."),
                    html.Li("Europe also shows that higher female part-time employment is linked with higher female informal employment, but both rates are much lower overall."),
                    html.Li("Latin America & Caribbean shows a weaker relationship because countries are more spread out."),
                    html.Li("Middle East & North Africa shows no clear relationship because countries with similar part-time rates have very different informal employment rates."),
                    html.Li("Russia & Caucasus and South Asia have too few data points to make a reliable conclusion."),
                ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8"}),
            ], style={"backgroundColor": CARD_BG, "padding": "16px 24px", "borderRadius": "8px", "marginTop": "16px", "marginBottom": "24px"}),

            html.P("Source: IMF Gender Statistics",
                   style={"textAlign": "center", "fontSize": "0.85em", "opacity": "0.6"}),
        ]),

        html.Div(id="informal", style={"display": "none"}),

        # ======================================================
        # CROSS-INDICATOR SECTION
        # ======================================================

        html.Div(id="cross", style=section_style, children=[
            html.H2("Cross-Indicator Analysis", style=section_title),

            # Heatmap
            html.H3("Correlation Heatmap", style={"textAlign": "center", "color": PRIMARY, "fontSize": "20px"}),
            html.P("Shows how major workforce indicators relate to one another.",
                   style={"textAlign": "center", "opacity": "0.6", "fontSize": "0.85em"}),
            html.Div([
                html.P("Values range from −1 to +1", style={"margin": "0"}),
                html.P("+1 = perfect positive relationship | −1 = perfect negative | 0 = no relationship",
                       style={"margin": "0"}),
            ], style={"textAlign": "center", "opacity": "0.6", "fontSize": "0.8em", "marginBottom": "20px"}),
            dcc.Graph(id="cross-heatmap"),

            html.Div([
                html.P("💡 What does this chart tell us?",
                       style={"color": PRIMARY, "fontWeight": "700", "marginBottom": "8px", "fontSize": "0.95em"}),
                html.Ul([
                    html.Li([html.B("Labor Force Participation & Unemployment: −0.52. "), "This is the strongest relationship. Where more women participate in the labor force, female unemployment tends to be lower."]),
                    html.Li([html.B("Part-Time & Informal: 0.45. "), "This is the strongest positive relationship. Countries with higher female part-time employment also tend to have higher female informal employment, suggesting these two forms of non-standard work often appear together."]),
                    html.Li([html.B("Unemployment & Informal: −0.42. "), "Where female informal employment is higher, measured unemployment tends to be lower."]),
                    html.Li([html.B("LFP & Informal: 0.31. "), "Higher female labor force participation is moderately linked with higher informal employment."]),
                    html.Li([html.B("LFP & Wage Gap: 0.23. "), "This is a weak positive relationship. More women working does not necessarily mean they earn closer to men."]),
                    html.Li([html.B("Wage Gap & Informal: 0.25. "), "Countries with larger wage gaps also tend to have slightly higher female informal employment."]),
                    html.Li([html.B("Part-Time & Wage Gap: 0.09; Part-Time & LFP: 0.14. "), "These are very weak relationships, meaning there is little to no clear connection between these pairs."]),
                ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8"}),
            ], style={"backgroundColor": CARD_BG, "padding": "16px 24px", "borderRadius": "8px", "marginTop": "16px", "marginBottom": "24px"}),

            html.Hr(style={"borderColor": PRIMARY, "opacity": "0.2"}),

            # Quadrant Scatter
            html.H3("Quadrant Scatter Plot", style={"textAlign": "center", "color": PRIMARY, "fontSize": "20px", "marginTop": "40px"}),
            html.P("All countries in 2022 — Female LFP vs Gender Wage Gap across four quadrants.",
                   style={"textAlign": "center", "opacity": "0.6", "fontSize": "0.85em"}),
            dcc.Graph(id="cross-quadrant"),

            html.Div([
                html.P("💡 What does this chart tell us?",
                       style={"color": PRIMARY, "fontWeight": "700", "marginBottom": "8px", "fontSize": "0.95em"}),
                html.Ul([
                    html.Li("Most countries fall into either the High LFP + High Wage Gap group or the Low LFP + Low Wage Gap group."),
                    html.Li("This suggests two common patterns: some countries have many women participating in the labor force but earning much less than men, while other countries have fewer women participating in the labor force but a smaller wage gap."),
                ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8"}),
            ], style={"backgroundColor": CARD_BG, "padding": "16px 24px", "borderRadius": "8px", "marginTop": "16px", "marginBottom": "24px"}),
        ]),
        # ======================================================
        # INTERACTIVE SCATTER PLOT
        # ======================================================

        html.Div(style={"padding": "80px 0", "borderTop": f"1px solid {PRIMARY}33"}, children=[
            html.H2("Explore Indicator Relationships", style=section_title),
            html.P("Select any two indicators to explore their relationship across countries.",
                   style={"textAlign": "center", "opacity": "0.6", "fontSize": "0.85em", "marginBottom": "30px"}),

            dbc.Row([
                dbc.Col([
                    html.Label("X Axis", style={"color": PRIMARY, "fontWeight": "700"}),
                    dcc.Dropdown(
                        id="scatter-x",
                        options=[
                            {"label": "Female LFP Rate", "value": "LFP"},
                            {"label": "Female Unemployment", "value": "Unemployment"},
                            {"label": "Gender Wage Gap", "value": "Wage Gap"},
                            {"label": "Female Part-Time Employment", "value": "Part-Time"},
                            {"label": "Female Informal Employment", "value": "Informal"},
                        ],
                        value="LFP",
                        clearable=False
                    ),
                ], width=4),
                dbc.Col([
                    html.Label("Y Axis", style={"color": PRIMARY, "fontWeight": "700"}),
                    dcc.Dropdown(
                        id="scatter-y",
                        options=[
                            {"label": "Female LFP Rate", "value": "LFP"},
                            {"label": "Female Unemployment", "value": "Unemployment"},
                            {"label": "Gender Wage Gap", "value": "Wage Gap"},
                            {"label": "Female Part-Time Employment", "value": "Part-Time"},
                            {"label": "Female Informal Employment", "value": "Informal"},
                        ],
                        value="Unemployment",
                        clearable=False
                    ),
                ], width=4),
                dbc.Col([
                    html.Label("Trend Line", style={"color": PRIMARY, "fontWeight": "700"}),
                    dcc.RadioItems(
                        id="scatter-trendline",
                        options=["Show", "Hide"],
                        value="Show",
                        inputStyle={"marginRight": "6px"},
                        labelStyle={"marginRight": "14px"}
                    ),
                ], width=4),
            ], className="my-4"),

            html.Div(id="scatter-corr", style={
                "textAlign": "center",
                "color": PRIMARY,
                "fontWeight": "700",
                "fontSize": "1em",
                "marginBottom": "10px"
            }),

            dcc.Graph(id="cross-scatter"),
        ]),

        # ======================================================
        # NOTES SECTION
        # ======================================================

        html.Div(style={"padding": "80px 0", "borderTop": f"1px solid {PRIMARY}33"}, children=[
            html.H2("Notes", style={"color": PRIMARY, "fontWeight": "700", "marginBottom": "40px"}),

            # 1. Labor Force Participation
            html.H4("1. Labor Force Participation", style={"color": PRIMARY, "fontWeight": "700", "marginBottom": "10px"}),

            html.P("1.1 Female vs Male Labor Force Participation", style={"color": PRIMARY, "fontWeight": "600", "marginBottom": "4px"}),
            html.Ul([
                html.Li("Indicator: Labor Force Participation, Modeled ILO Estimate, Rate."),
                html.Li("Filter: Age Group: 15+ years, Marital Status: Not Applicable (broadest adult population measure)."),
                html.Li("Calculation: Female and male values are averaged by year and region. Gender gap = Male − Female."),
            ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8", "marginBottom": "16px"}),

            html.P("1.2 Global Labor Force Participation Map", style={"color": PRIMARY, "fontWeight": "600", "marginBottom": "4px"}),
            html.Ul([
                html.Li("Indicator: Labor Force Participation, Modeled ILO Estimate, Rate."),
                html.Li("Filter: Age Group: 15+ years, Marital Status: Not Applicable."),
                html.Li("Calculation: Uses country-level female or male values directly from the dataset by year. Country names are mapped to ISO3 codes using the pycountry library and a custom override dictionary for countries with non-standard names."),
            ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8", "marginBottom": "30px"}),

            # 2. Wages
            html.H4("2. Wages", style={"color": PRIMARY, "fontWeight": "700", "marginBottom": "10px"}),

            html.P("2.1 Gender Wage Gap by Region Over Time", style={"color": PRIMARY, "fontWeight": "600", "marginBottom": "4px"}),
            html.Ul([
                html.Li("Indicator: Gender Wage Gap by Occupation, Rate."),
                html.Li("Filter: Occupation: Total (By ICSO 08 Classification) — covers all occupations combined, not a specific job category."),
                html.Li("Calculation: Uses the wage gap values already provided in the dataset. Regional and global values are averaged by year."),
            ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8", "marginBottom": "16px"}),

            html.P("2.2 Private vs Public Sector Wage Ratio", style={"color": PRIMARY, "fontWeight": "600", "marginBottom": "4px"}),
            html.Ul([
                html.Li("Indicators: Female To Male Wage Ratio, Private Sector, Mean; Female To Male Wage Ratio, Public Sector, Mean."),
                html.Li("Calculation: Uses dataset values directly, averaged by year and selected region."),
            ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8", "marginBottom": "30px"}),

            # 3. Unemployment
            html.H4("3. Unemployment", style={"color": PRIMARY, "fontWeight": "700", "marginBottom": "10px"}),

            html.P("3.1 Female vs Male Unemployment Rate Over Time", style={"color": PRIMARY, "fontWeight": "600", "marginBottom": "4px"}),
            html.Ul([
                html.Li("Indicator: Unemployment Rate."),
                html.Li("Filter: Age Group: Not Applicable, Marital Status: Total — covers all adults regardless of age or marital status."),
                html.Li("Calculation: Female and male values are averaged by year and region. Gender gap = Female − Male."),
            ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8", "marginBottom": "16px"}),

            html.P("3.2 Gender Unemployment Gap by Region", style={"color": PRIMARY, "fontWeight": "600", "marginBottom": "4px"}),
            html.Ul([
                html.Li("Indicator: Unemployment Rate."),
                html.Li("Filter: Age Group: Not Applicable, Marital Status: Total."),
                html.Li("Calculation: Gender unemployment gap = Female − Male, averaged by region and year."),
            ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8", "marginBottom": "16px"}),

            html.P("3.3 Gender Unemployment Gap by Country", style={"color": PRIMARY, "fontWeight": "600", "marginBottom": "4px"}),
            html.Ul([
                html.Li("Indicator: Unemployment Rate."),
                html.Li("Filter: Age Group: Not Applicable, Marital Status: Total."),
                html.Li("Calculation: Country-level gender unemployment gap = Female − Male for the selected year."),
            ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8", "marginBottom": "30px"}),

            # 4. Part-Time & Informal Work
            html.H4("4. Part-Time & Informal Work", style={"color": PRIMARY, "fontWeight": "700", "marginBottom": "10px"}),

            html.P("4.1 Female vs Male Part-Time Employment by Country", style={"color": PRIMARY, "fontWeight": "600", "marginBottom": "4px"}),
            html.Ul([
                html.Li("Indicator: Part-Time Employment, Percent of total employment."),
                html.Li("Calculation: Gender gap = Female − Male. Only the top 30 countries by gap size are shown, highlighting the most extreme cases rather than the global picture."),
            ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8", "marginBottom": "16px"}),

            html.P("4.2 Part-Time Employment Trend by Region", style={"color": PRIMARY, "fontWeight": "600", "marginBottom": "4px"}),
            html.Ul([
                html.Li("Indicator: Part-Time Employment, Percent of total employment."),
                html.Li("Calculation: Female and male values are averaged by region and year. The shaded area between the two lines shows the gender gap visually."),
            ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8", "marginBottom": "16px"}),

            html.P("4.3 Female vs Male Informal Employment by Country", style={"color": PRIMARY, "fontWeight": "600", "marginBottom": "4px"}),
            html.Ul([
                html.Li("Indicator: Informal Employment by Economic Activity."),
                html.Li("Calculation: Gender gap = Female − Male for the selected year and activity type. Only the top 25 countries by gap size are shown, highlighting the most extreme cases."),
            ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8", "marginBottom": "16px"}),

            html.P("4.4 Informal vs Part-Time Employment by Country", style={"color": PRIMARY, "fontWeight": "600", "marginBottom": "4px"}),
            html.Ul([
                html.Li("Indicators: Informal Employment by Economic Activity and Part-Time Employment, Percent of total employment."),
                html.Li("Calculation: Uses both indicators directly, merged at the country level for the selected year and gender. The trend line is an OLS (Ordinary Least Squares) regression line calculated automatically by Plotly Express."),
            ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8", "marginBottom": "30px"}),

            # 5. Cross-Indicator Analysis
            html.H4("5. Cross-Indicator Analysis", style={"color": PRIMARY, "fontWeight": "700", "marginBottom": "10px"}),

            html.P("5.1 Correlation Heatmap", style={"color": PRIMARY, "fontWeight": "600", "marginBottom": "4px"}),
            html.Ul([
                html.Li("Indicators: Female labor force participation, female unemployment, gender wage gap, female part-time employment, and female informal employment."),
                html.Li("Calculation: Country-level averages across all available years are computed for each indicator, then Pearson correlations between all indicator pairs are calculated using pandas .corr(). Values range from −1 to +1."),
            ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8", "marginBottom": "16px"}),

            html.P("5.2 Quadrant Scatter Plot", style={"color": PRIMARY, "fontWeight": "600", "marginBottom": "4px"}),
            html.Ul([
                html.Li("Indicators: Female labor force participation and gender wage gap, both for 2022."),
                html.Li("Calculation: The median is calculated separately for each axis from 2022 data only. Countries missing either LFP or wage gap data in 2022 are excluded. The median thresholds are used to classify each country into one of four quadrants: High LFP + Low Wage Gap, High LFP + High Wage Gap, Low LFP + Low Wage Gap, and Low LFP + High Wage Gap."),
            ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8", "marginBottom": "16px"}),

            html.P("5.3 Explore Indicator Relationships", style={"color": PRIMARY, "fontWeight": "600", "marginBottom": "4px"}),
            html.Ul([
                html.Li("Indicators: Users can select any two indicators: Female LFP Rate, Female Unemployment Rate, Gender Wage Gap, Female Part-Time Employment, and Female Informal Employment."),
                html.Li("Calculation: Country-level averages are calculated across all available years for each indicator, then merged by country. The Pearson correlation between the two selected indicators is shown above the chart. The trend line is an OLS regression line, calculated automatically by Plotly Express."),
            ], style={"color": TEXT, "fontSize": "0.9em", "lineHeight": "1.8", "marginBottom": "30px"}),

            html.P("Source: IMF Gender Statistics (GS_LI). Data accessed through the IMF Data Portal.",
                    style={"color": TEXT, "fontSize": "0.85em", "opacity": "0.6", "marginTop": "40px", "fontStyle": "italic"}),
        ]),
    ]
)

# ============================================================
# CALLBACK: UPDATE LFP METRICS AND TREND CHART
# ============================================================

@app.callback(
    Output("female-lfp", "children"),
    Output("male-lfp", "children"),
    Output("gap-lfp", "children"),
    Output("region-lfp", "children"),
    Output("lfp-trend-chart", "figure"),
    Input("lfp-region", "value"),
    Input("lfp-year", "value"),
    Input("lfp-chart-type", "value")
)
def update_lfp_section(selected_region, year_range, chart_type):
    filtered = lfp_ext[
        lfp_ext["YEAR"].between(year_range[0], year_range[1])
    ].copy()

    if selected_region != "Global Average":
        filtered = filtered[filtered["REGION"] == selected_region]

    global_female = filtered[filtered["GENDER"] == "Female"]["VALUE"].mean()
    global_male = filtered[filtered["GENDER"] == "Male"]["VALUE"].mean()
    global_gap = global_male - global_female

    region_gap = (
        filtered
        .groupby(["REGION", "GENDER"])["VALUE"]
        .mean()
        .unstack()
        .dropna()
    )

    region_gap["gap"] = region_gap["Male"] - region_gap["Female"]

    if len(region_gap) > 0:
        largest_gap_region = region_gap["gap"].idxmax()
    else:
        largest_gap_region = "N/A"

    lfp_avg = (
        filtered
        .groupby(["YEAR", "GENDER"])["VALUE"]
        .mean()
        .reset_index()
    )

    female_vals = lfp_avg[lfp_avg["GENDER"] == "Female"].sort_values("YEAR")
    male_vals = lfp_avg[lfp_avg["GENDER"] == "Male"].sort_values("YEAR")

    fig = go.Figure()

    if chart_type == "Line":
        fig.add_trace(go.Scatter(
            x=male_vals["YEAR"],
            y=male_vals["VALUE"],
            name="Male",
            mode="lines",
            line=dict(color=COLOR_MALE, width=3)
        ))

        fig.add_trace(go.Scatter(
            x=female_vals["YEAR"],
            y=female_vals["VALUE"],
            name="Female",
            mode="lines",
            line=dict(color=COLOR_FEMALE, width=3),
            fill="tonexty",
            fillcolor="rgba(206, 236, 206, 0.5)",
        ))

        barmode = None

    else:
        fig.add_trace(go.Bar(
            x=female_vals["YEAR"],
            y=female_vals["VALUE"],
            name="Female",
            marker_color=COLOR_FEMALE
        ))

        fig.add_trace(go.Bar(
            x=male_vals["YEAR"],
            y=male_vals["VALUE"],
            name="Male",
            marker_color=COLOR_MALE
        ))

        barmode = "stack" if chart_type == "Stacked Bar" else "group"

    fig.update_layout(
        title=dict(
            text=f"Female vs Male Labor Force Participation ({selected_region})",
            font=dict(family="Playfair Display, serif", size=20, color=PRIMARY),
            x=0.5,
            xanchor="center"
        ),
        barmode=barmode,
        height=520,
        plot_bgcolor=BG,
        paper_bgcolor=BG,
        font=dict(family="Playfair Display, serif", size=14),
        xaxis=dict(title="Year", gridcolor="#eeeeee", dtick=2),
        yaxis=dict(title="Labor Force Participation Rate (%)", gridcolor="#eeeeee"),
        legend=dict(title="Gender"),
        margin=dict(t=60, b=50, l=60, r=30)
    )

    return (
        f"{global_female:.1f}%",
        f"{global_male:.1f}%",
        f"{global_gap:.1f} pts",
        largest_gap_region,
        fig
    )

# ============================================================
# CALLBACK: UPDATE LFP ANIMATED MAP
# ============================================================

@app.callback(
    Output("lfp-anim-map", "figure"),
    Input("lfp-anim-gender", "value")
)
def update_anim_map(gender):
    data = df[
        (df["INDICATOR"] == "Labor Force Participation, Modeled ILO Estimate, Rate") &
        (df["AGE_GROUP"] == "15+ yrs") &
        (df["GS_MS"] == "Not Applicable") &
        (df["GENDER"] == gender)
    ].copy()

    data["code"] = data["COUNTRY"].apply(iso3)
    data = data.dropna(subset=["code", "VALUE"]).sort_values("YEAR")

    fig = px.choropleth(
        data,
        locations="code",
        color="VALUE",
        hover_name="COUNTRY",
        animation_frame="YEAR",
        color_continuous_scale=[
            [0.0, "#F8FFFC"],
            [0.4, "#c9f4e0"],
            [0.7, "#577c6c"],
            [1.0, "#11241c"]
        ],
        range_color=[0, 100],
        hover_data={"code": False, "VALUE": ":.1f"}
    )
    fig.update_layout(height=800, paper_bgcolor=BG,
        geo=dict(showframe=False, showcoastlines=False, showland=True,
            landcolor="#d9d9d9", showocean=True, oceancolor="#ddeeff",
            projection_type="equirectangular", showcountries=True, countrycolor="white"),
        margin=dict(t=20, b=120, l=0, r=110),
        coloraxis_colorbar=dict(
            title="",
            orientation="v",
            x=1.02, xanchor="left",
            y=0.5, yanchor="middle",
            len=0.5, thickness=20,
            tickvals=[0, 40, 70, 100],
            ticktext=["0%", "40%", "70%", "100%"],
        )
    )
    
    try:
        fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 800
        fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 400
    except IndexError:
        pass

    return fig

# ============================================================
# CALLBACKS: WAGES
# ============================================================
@app.callback(
    Output("wage-gap-avg", "children"),
    Output("wage-gap-latest", "children"),
    Output("wage-private", "children"),
    Output("wage-public", "children"),
    Input("wage-sector-chart", "id")
)
def update_wage_metrics(_):
    global_gap = df[
        (df["INDICATOR"] == "Gender Wage Gap by Occupation, Rate") &
        (df["GS_LI_OCC"] == "Total (By ICSO 08 Classification)")
    ]["VALUE"].mean()
    latest_gap = df[
        (df["INDICATOR"] == "Gender Wage Gap by Occupation, Rate") &
        (df["GS_LI_OCC"] == "Total (By ICSO 08 Classification)") &
        (df["YEAR"] == 2022)
    ]["VALUE"].mean()
    private_ratio = df[df["INDICATOR"] == "Female To Male Wage Ratio, Private Sector, Mean"]["VALUE"].mean()
    public_ratio = df[df["INDICATOR"] == "Female To Male Wage Ratio, Public Sector, Mean"]["VALUE"].mean()
    return f"{global_gap:.1f}%", f"{latest_gap:.1f}%", f"{private_ratio:.2f}", f"{public_ratio:.2f}"

@app.callback(
    Output("wage-sector-chart", "figure"),
    Input("wage-sector-region", "value"),
    Input("wage-sector-type", "value")
)
def update_wage_sector(selected_region, chart_type):
    if selected_region != "Global Average":
        private_vals = df[
            (df["INDICATOR"] == "Female To Male Wage Ratio, Private Sector, Mean") &
            (df["REGION"] == selected_region)
        ].groupby("YEAR")["VALUE"].mean().reset_index()
        public_vals = df[
            (df["INDICATOR"] == "Female To Male Wage Ratio, Public Sector, Mean") &
            (df["REGION"] == selected_region)
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

    fig = go.Figure()
    if chart_type == "Line":
        fig.add_trace(go.Scatter(
            x=private_vals["YEAR"], y=private_vals["VALUE"],
            name="Private Sector",
            line=dict(color=COLOR_FEMALE, width=2.5), mode="lines",
            hovertemplate="<b>Private</b><br>Year: %{x}<br>Ratio: %{y:.3f}<extra></extra>"
        ))
        fig.add_trace(go.Scatter(
            x=public_vals["YEAR"], y=public_vals["VALUE"],
            name="Public Sector",
            line=dict(color=COLOR_MALE, width=2.5), mode="lines",
            fill="tonexty", fillcolor="rgba(206,236,206,0.5)",
            hovertemplate="<b>Public</b><br>Year: %{x}<br>Ratio: %{y:.3f}<extra></extra>"
        ))
    else:
        fig.add_trace(go.Bar(
            x=private_vals["YEAR"], y=private_vals["VALUE"],
            name="Private Sector", marker_color=COLOR_FEMALE,
            hovertemplate="<b>Private</b><br>Year: %{x}<br>Ratio: %{y:.3f}<extra></extra>"
        ))
        fig.add_trace(go.Bar(
            x=public_vals["YEAR"], y=public_vals["VALUE"],
            name="Public Sector", marker_color=COLOR_MALE,
            hovertemplate="<b>Public</b><br>Year: %{x}<br>Ratio: %{y:.3f}<extra></extra>"
        ))

    fig.update_layout(
        height=520,
        plot_bgcolor=BG, paper_bgcolor=BG,
        font=dict(family="Playfair Display, serif", size=13, color=TEXT),
        barmode="group",
        xaxis=dict(title="Year", tickmode="linear", dtick=2, tickangle=45, gridcolor="#eeeeee"),
        yaxis=dict(title="Female-to-Male Wage Ratio", gridcolor="#eeeeee",
                   autorange=True),
        legend=dict(title="Sector"),
        hovermode="x unified", margin=dict(t=30)
    )
    return fig

@app.callback(
    Output("wage-region-small-multiples", "children"),
    Input("wage-sector-chart", "id")
)
def update_wage_charts(_):
    all_data = df[
        (df["INDICATOR"] == "Gender Wage Gap by Occupation, Rate") &
        (df["GS_LI_OCC"] == "Total (By ICSO 08 Classification)")
    ].copy().dropna(subset=["VALUE", "REGION"])

    region_trend = all_data.groupby(["YEAR", "REGION"])["VALUE"].mean().reset_index()
    all_regions = ["Global Average"] + sorted(region_trend["REGION"].dropna().unique())

    rows = []
    for i in range(0, len(all_regions), 3):
        row_regions = all_regions[i:i+3]
        cols = []
        for region in row_regions:
            rdata = region_trend[region_trend["REGION"] == region].sort_values("YEAR")
            fig_small = go.Figure()
            if region == "Global Average":
                global_rdata = all_data.groupby("YEAR")["VALUE"].mean().reset_index().sort_values("YEAR")
                fig_small.add_trace(go.Scatter(
                    x=global_rdata["YEAR"], y=global_rdata["VALUE"],
                    mode="lines",
                    line=dict(color="#8faf8f", width=2.5),
                    fill="tozeroy",
                    fillcolor="rgba(251,230,239,0.5)",
                    hovertemplate="Year: %{x}<br>Gap: %{y:.1f}%<extra></extra>"
                ))
            elif region == "Central Asia" or len(rdata) < 5:
                fig_small.add_annotation(
                    text="Limited data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=12, color=TEXT, family="Playfair Display, serif")
                )
            else:
                fig_small.add_trace(go.Scatter(
                    x=rdata["YEAR"], y=rdata["VALUE"],
                    mode="lines",
                    line=dict(color="#8faf8f", width=2),
                    fill="tozeroy",
                    fillcolor="rgba(251,230,239,0.5)",
                    hovertemplate="Year: %{x}<br>Gap: %{y:.1f}%<extra></extra>"
                ))
            fig_small.update_layout(
                height=250,
                title=dict(text=region, font=dict(size=12, family="Playfair Display, serif", color="#8faf8f"), x=0.5),
                plot_bgcolor=BG, paper_bgcolor=BG,
                margin=dict(t=40, b=30, l=40, r=20),
                xaxis=dict(showgrid=False, tickmode="linear", dtick=2, tickfont=dict(size=9)),
                yaxis=dict(showgrid=False, tickfont=dict(size=8), title=dict(text="Gap (%)", font=dict(size=9))),
                showlegend=False
            )
            cols.append(dbc.Col(dcc.Graph(figure=fig_small), width=4))
        rows.append(dbc.Row(cols, className="mb-3"))

    return rows


# ============================================================
# CALLBACKS: UNEMPLOYMENT
# ============================================================

@app.callback(
    Output("unemp-female", "children"),
    Output("unemp-male", "children"),
    Output("unemp-gap", "children"),
    Output("unemp-latest", "children"),
    Output("unemp-div-year", "options"),
    Output("unemp-div-year", "value"),
    Input("unemp-region", "id")
)
def init_unemp(_):
    unemp_all = df[
        (df["INDICATOR"] == "Unemployment Rate , Rate") &
        (df["AGE_GROUP"] == "Not Applicable") &
        (df["GS_MS"] == "Total") &
        (df["GENDER"].isin(["Female", "Male"]))
    ].copy()
    female = unemp_all[unemp_all["GENDER"] == "Female"]["VALUE"].mean()
    male = unemp_all[unemp_all["GENDER"] == "Male"]["VALUE"].mean()
    gap = female - male
    latest = unemp_all[(unemp_all["GENDER"] == "Female") & (unemp_all["YEAR"] == 2022)]["VALUE"].mean()
    years = sorted(unemp_all["YEAR"].unique(), reverse=True)
    year_options = [{"label": str(y), "value": y} for y in years]
    return f"{female:.1f}%", f"{male:.1f}%", f"{gap:.1f} pts", f"{latest:.1f}%", year_options, years[0]

@app.callback(
    Output("unemp-trend-chart", "figure"),
    Input("unemp-region", "value"),
    Input("unemp-year", "value")
)
def update_unemp_trend(selected_region, year_range):
    unemp = df[
        (df["INDICATOR"] == "Unemployment Rate , Rate") &
        (df["AGE_GROUP"] == "Not Applicable") &
        (df["GS_MS"] == "Total") &
        (df["GENDER"].isin(["Female", "Male"]))
    ].copy()
    unemp = unemp[unemp["YEAR"].between(year_range[0], year_range[1])]
    if selected_region != "Global Average":
        unemp = unemp[unemp["REGION"] == selected_region]
    avg = unemp.groupby(["YEAR", "GENDER"])["VALUE"].mean().reset_index()
    female_vals = avg[avg["GENDER"] == "Female"].sort_values("YEAR")
    male_vals = avg[avg["GENDER"] == "Male"].sort_values("YEAR")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=male_vals["YEAR"], y=male_vals["VALUE"],
        name="Male", mode="lines",
        line=dict(color=COLOR_MALE, width=2.5),
        fill="tozeroy", fillcolor="rgba(206,236,206,0.4)",
        hovertemplate="<b>Male</b><br>Year: %{x}<br>Rate: %{y:.1f}%<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=female_vals["YEAR"], y=female_vals["VALUE"],
        name="Female", mode="lines",
        line=dict(color=COLOR_FEMALE, width=2.5),
        fill="tozeroy", fillcolor="rgba(251,230,239,0.4)",
        hovertemplate="<b>Female</b><br>Year: %{x}<br>Rate: %{y:.1f}%<extra></extra>"
    ))
    fig.update_layout(
        height=450, plot_bgcolor=BG, paper_bgcolor=BG,
        font=dict(family="Playfair Display, serif", size=13, color=TEXT),
        xaxis=dict(title="Year", tickmode="linear", dtick=2, tickangle=45, gridcolor="#eeeeee"),
        yaxis=dict(title="Unemployment Rate (%)", gridcolor="#eeeeee"),
        legend=dict(title="Gender"),
        hovermode="x unified", margin=dict(t=30)
    )
    return fig

@app.callback(
    Output("unemp-sparklines", "children"),
    Output("unemp-diverging", "figure"),
    Input("unemp-div-year", "value")
)
def update_unemp_charts(div_year):
    unemp_viz = df[
        (df["INDICATOR"] == "Unemployment Rate , Rate") &
        (df["AGE_GROUP"] == "Not Applicable") &
        (df["GS_MS"] == "Total") &
        (df["GENDER"].isin(["Female", "Male"]))
    ].copy()

    # Sparklines
    region_gap_time = unemp_viz.groupby(["YEAR", "REGION", "GENDER"])["VALUE"].mean().unstack().reset_index()
    region_gap_time.columns.name = None
    region_gap_time["gap"] = region_gap_time["Female"] - region_gap_time["Male"]
    region_gap_time = region_gap_time.dropna(subset=["gap"])
    all_regions = sorted(region_gap_time["REGION"].dropna().unique())

    rows = []
    for i in range(0, len(all_regions), 3):
        row_regions = all_regions[i:i+3]
        cols = []
        for region in row_regions:
            rdata = region_gap_time[region_gap_time["REGION"] == region].sort_values("YEAR")
            fig_spark = go.Figure()
            fig_spark.add_trace(go.Scatter(
                x=rdata["YEAR"], y=rdata["gap"],
                mode="lines",
                line=dict(color="#8faf8f", width=2),
                fill="tozeroy",
                fillcolor="rgba(143,175,143,0.15)",
                hovertemplate="Year: %{x}<br>Gap: %{y:.1f} pts<extra></extra>"
            ))
            if div_year:
                selected_row = rdata[rdata["YEAR"] == div_year]
                if not selected_row.empty:
                    fig_spark.add_trace(go.Scatter(
                        x=selected_row["YEAR"], y=selected_row["gap"],
                        mode="markers",
                        marker=dict(size=8, color=COLOR_FEMALE),
                        hovertemplate=f"Selected: {div_year}<br>Gap: %{{y:.1f}} pts<extra></extra>"
                    ))
            fig_spark.add_hline(y=0, line_dash="dash", line_color="grey", line_width=1)
            fig_spark.update_layout(
                height=180,
                title=dict(text=region, font=dict(size=11, family="Playfair Display, serif", color=PRIMARY), x=0.5),
                plot_bgcolor=BG, paper_bgcolor=BG,
                margin=dict(t=30, b=20, l=30, r=10),
                xaxis=dict(showgrid=False, tickmode="linear", dtick=5, tickfont=dict(size=8)),
                yaxis=dict(showgrid=False, tickfont=dict(size=8)),
                showlegend=False
            )
            cols.append(dbc.Col(dcc.Graph(figure=fig_spark), width=4))
        rows.append(dbc.Row(cols, className="mb-3"))

    # Diverging Bar
    if div_year:
        div_data = unemp_viz[unemp_viz["YEAR"] == div_year].copy()
        div_pivot = div_data.pivot_table(index="COUNTRY", columns="GENDER", values="VALUE").reset_index()
        div_pivot.columns.name = None
        div_pivot = div_pivot.dropna(subset=["Female", "Male"])
        div_pivot["gap"] = div_pivot["Female"] - div_pivot["Male"]
        div_pivot = div_pivot.sort_values("gap")
        div_pivot["color"] = div_pivot["gap"].apply(lambda x: COLOR_FEMALE if x > 0 else COLOR_MALE)

        fig_div = go.Figure()
        fig_div.add_trace(go.Bar(
            x=div_pivot["gap"], y=div_pivot["COUNTRY"],
            orientation="h",
            marker_color=div_pivot["color"],
            hovertemplate="<b>%{y}</b><br>Gap: %{x:.1f} pts<extra></extra>"
        ))
        fig_div.add_vline(x=0, line_width=1.5, line_color=PRIMARY)
        fig_div.update_layout(
            height=max(600, len(div_pivot) * 18),
            plot_bgcolor=BG, paper_bgcolor=BG,
            font=dict(family="Playfair Display, serif", size=11, color=TEXT),
            xaxis=dict(title="Female − Male Unemployment Gap (pts)", gridcolor="#eeeeee"),
            yaxis=dict(showgrid=False),
            margin=dict(l=150, r=40, t=30, b=40)
        )
    else:
        fig_div = go.Figure()

    return rows, fig_div

# ============================================================
# CALLBACKS: PART-TIME & INFORMAL
# ============================================================

@app.callback(
    Output("pt-female", "children"),
    Output("pt-male", "children"),
    Output("inf-female", "children"),
    Output("inf-male", "children"),
    Input("pt-dumbbell", "id")
)
def init_pt_metrics(_):
    pt_f = df[(df["INDICATOR"] == "Part-Time Employment, Percent of total employment") & (df["GENDER"] == "Female")]["VALUE"].mean()
    pt_m = df[(df["INDICATOR"] == "Part-Time Employment, Percent of total employment") & (df["GENDER"] == "Male")]["VALUE"].mean()
    inf_f = df[(df["INDICATOR"] == "Informal Employment by Economic Activity") & (df["GS_LI_EA"] == "Total Agriculture and Non-agriculture") & (df["GENDER"] == "Female")]["VALUE"].mean()
    inf_m = df[(df["INDICATOR"] == "Informal Employment by Economic Activity") & (df["GS_LI_EA"] == "Total Agriculture and Non-agriculture") & (df["GENDER"] == "Male")]["VALUE"].mean()
    return f"{pt_f:.1f}%", f"{pt_m:.1f}%", f"{inf_f:.1f}%", f"{inf_m:.1f}%"

@app.callback(
    Output("pt-dumbbell", "figure"),
    Input("pt-year", "value"),
    Input("pt-region", "value")
)
def update_pt_dumbbell(pt_year, pt_region):
    pt = df[
        (df["INDICATOR"] == "Part-Time Employment, Percent of total employment") &
        (df["AGE_GROUP"] == "Not Applicable") &
        (df["GS_MS"] == "Not Applicable") &
        (df["YEAR"] == pt_year)
    ].copy()
    if pt_region != "All Regions":
        pt = pt[pt["REGION"] == pt_region]
    pt_pivot = pt.pivot_table(index=["COUNTRY", "REGION"], columns="GENDER", values="VALUE").reset_index()
    pt_pivot.columns.name = None
    pt_pivot = pt_pivot.dropna(subset=["Female", "Male"])
    pt_pivot["gap"] = pt_pivot["Female"] - pt_pivot["Male"]
    pt_pivot = pt_pivot.sort_values("gap", ascending=False).head(30)

    fig = go.Figure()
    for _, row in pt_pivot.iterrows():
        fig.add_shape(type="line",
            x0=row["Male"], x1=row["Female"],
            y0=row["COUNTRY"], y1=row["COUNTRY"],
            line=dict(color="#dddddd", width=2))
    fig.add_trace(go.Scatter(
        x=pt_pivot["Male"], y=pt_pivot["COUNTRY"],
        mode="markers", name="Male",
        marker=dict(size=10, color=COLOR_MALE),
        hovertemplate="<b>%{y}</b><br>Male: %{x:.1f}%<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=pt_pivot["Female"], y=pt_pivot["COUNTRY"],
        mode="markers", name="Female",
        marker=dict(size=10, color=COLOR_FEMALE),
        hovertemplate="<b>%{y}</b><br>Female: %{x:.1f}%<extra></extra>"
    ))
    fig.update_layout(
        height=700, plot_bgcolor=BG, paper_bgcolor=BG,
        font=dict(family="Playfair Display, serif", size=12, color=TEXT),
        xaxis=dict(title="Part-Time Employment (%)", gridcolor="#eeeeee"),
        yaxis=dict(categoryorder="total ascending", showgrid=False),
        legend=dict(title="Gender"),
        margin=dict(l=150, r=40, t=30, b=40)
    )
    return fig

@app.callback(
    Output("pt-small-multiples", "children"),
    Input("pt-dumbbell", "id")
)
def update_pt_small_multiples(_):
    pt_trend = df[
        (df["INDICATOR"] == "Part-Time Employment, Percent of total employment") &
        (df["AGE_GROUP"] == "Not Applicable") &
        (df["GS_MS"] == "Not Applicable") &
        (df["GENDER"].isin(["Female", "Male"]))
    ].groupby(["YEAR", "REGION", "GENDER"])["VALUE"].mean().reset_index()

    all_regions = sorted(pt_trend["REGION"].dropna().unique())
    rows = []
    for i in range(0, len(all_regions), 3):
        row_regions = all_regions[i:i+3]
        cols = []
        for region in row_regions:
            rdata = pt_trend[pt_trend["REGION"] == region]
            f_data = rdata[rdata["GENDER"] == "Female"].sort_values("YEAR")
            m_data = rdata[rdata["GENDER"] == "Male"].sort_values("YEAR")
            fig_sm = go.Figure()
            fig_sm.add_trace(go.Scatter(
                x=m_data["YEAR"], y=m_data["VALUE"],
                mode="lines", name="Male",
                line=dict(color=COLOR_MALE, width=1.5)
            ))
            fig_sm.add_trace(go.Scatter(
                x=f_data["YEAR"], y=f_data["VALUE"],
                mode="lines", name="Female",
                line=dict(color=COLOR_FEMALE, width=1.5),
                fill="tonexty", fillcolor="rgba(251,230,239,0.2)"
            ))
            fig_sm.update_layout(
                height=180,
                title=dict(text=region, font=dict(size=11, family="Playfair Display, serif", color=PRIMARY), x=0.5),
                plot_bgcolor=BG, paper_bgcolor=BG,
                margin=dict(t=30, b=20, l=30, r=10),
                xaxis=dict(showgrid=False, tickmode="linear", dtick=5, tickfont=dict(size=8)),
                yaxis=dict(showgrid=False, tickfont=dict(size=8)),
                showlegend=False
            )
            cols.append(dbc.Col(dcc.Graph(figure=fig_sm), width=4))
        rows.append(dbc.Row(cols, className="mb-3"))
    return rows

@app.callback(
    Output("inf-lollipop", "figure"),
    Input("inf-year", "value"),
    Input("inf-activity", "value")
)
def update_inf_lollipop(inf_year, inf_activity):
    inf = df[
        (df["INDICATOR"] == "Informal Employment by Economic Activity") &
        (df["AGE_GROUP"] == "Not Applicable") &
        (df["GS_LI_EA"] == inf_activity) &
        (df["YEAR"] == inf_year)
    ].copy()
    inf_pivot = inf.pivot_table(index=["COUNTRY", "REGION"], columns="GENDER", values="VALUE").reset_index()
    inf_pivot.columns.name = None
    inf_pivot = inf_pivot.dropna(subset=["Female", "Male"])
    inf_pivot["gap"] = inf_pivot["Female"] - inf_pivot["Male"]
    inf_pivot = inf_pivot.sort_values("gap", ascending=False).head(25)

    fig = go.Figure()
    for _, row in inf_pivot.iterrows():
        fig.add_shape(type="line",
            x0=row["Male"], x1=row["Female"],
            y0=row["COUNTRY"], y1=row["COUNTRY"],
            line=dict(color="#dddddd", width=2))
    fig.add_trace(go.Scatter(
        x=inf_pivot["Male"], y=inf_pivot["COUNTRY"],
        mode="markers", name="Male",
        marker=dict(size=10, color=COLOR_MALE),
        hovertemplate="<b>%{y}</b><br>Male: %{x:.1f}%<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=inf_pivot["Female"], y=inf_pivot["COUNTRY"],
        mode="markers", name="Female",
        marker=dict(size=10, color=COLOR_FEMALE),
        hovertemplate="<b>%{y}</b><br>Female: %{x:.1f}%<extra></extra>"
    ))
    fig.update_layout(
        height=650, plot_bgcolor=BG, paper_bgcolor=BG,
        font=dict(family="Playfair Display, serif", size=12, color=TEXT),
        xaxis=dict(title="Informal Employment (%)", gridcolor="#eeeeee"),
        yaxis=dict(categoryorder="total ascending", showgrid=False),
        legend=dict(title="Gender"),
        margin=dict(l=150, r=40, t=30, b=40)
    )
    return fig

@app.callback(
    Output("inf-scatter", "figure"),
    Input("scatter-gender", "value"),
    Input("inf-year", "value")
)
def update_inf_scatter(scatter_gender, inf_year):
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
    REGION_COLORS = {
        r: c for r, c in zip(
            sorted(scatter_data["REGION"].dropna().unique()),
            ["#fbb4ae", "#b3cde3", "#ccebc5", "#decbe4",
             "#fed9a6", "#ffffcc", "#e5d8bd", "#fddaec", "#f2f2f2"]
        )
    }

    fig = px.scatter(
        scatter_data,
        x="Part-Time", y="Informal",
        color="REGION",
        hover_name="COUNTRY",
        trendline="ols",
        color_discrete_map=REGION_COLORS,
        labels={"Part-Time": "Part-Time Employment (%)", "Informal": "Informal Employment (%)"}
    )

    fig.update_traces(marker=dict(size=9, opacity=0.8))
    fig.update_layout(
        height=500,
        plot_bgcolor=BG, paper_bgcolor=BG,
        font=dict(family="Playfair Display, serif", size=13, color=TEXT),
        xaxis=dict(gridcolor="#eeeeee"),
        yaxis=dict(gridcolor="#eeeeee"),
        legend=dict(title="Region"),
        margin=dict(t=30)
    )
    return fig

# ============================================================
# CALLBACKS: CROSS-INDICATOR
# ============================================================

@app.callback(
    Output("cross-heatmap", "figure"),
    Output("cross-quadrant", "figure"),
    Input("cross-heatmap", "id")
)
def update_cross(_):
    corr = combined_data[["LFP", "Unemployment", "Wage Gap", "Part-Time", "Informal"]].corr()

    fig_heat = px.imshow(
        corr.round(2),
        text_auto=True,
        color_continuous_scale=[COLOR_FEMALE, "#ffffff", COLOR_MALE],
        zmin=-1, zmax=1,
        aspect="auto"
    )
    fig_heat.update_layout(
        height=450,
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(family="Playfair Display, serif", size=13, color=TEXT),
        margin=dict(t=30)
    )

    lfp_2022 = df[
        (df["INDICATOR"] == "Labor Force Participation, Modeled ILO Estimate, Rate") &
        (df["AGE_GROUP"] == "15+ yrs") &
        (df["GS_MS"] == "Not Applicable") &
        (df["GENDER"] == "Female") &
        (df["YEAR"] == 2022)
    ][["COUNTRY", "REGION", "VALUE"]].rename(columns={"VALUE": "LFP"})

    wage_2022 = df[
        (df["INDICATOR"] == "Gender Wage Gap by Occupation, Rate") &
        (df["GS_LI_OCC"] == "Total (By ICSO 08 Classification)") &
        (df["YEAR"] == 2022)
    ][["COUNTRY", "VALUE"]].rename(columns={"VALUE": "Wage Gap"})

    quad_data = lfp_2022.merge(wage_2022, on="COUNTRY").dropna()
    lfp_mid = quad_data["LFP"].median()
    wage_mid = quad_data["Wage Gap"].median()

    def quadrant(row):
        if row["LFP"] >= lfp_mid and row["Wage Gap"] <= wage_mid:
            return "High LFP + Low Wage Gap"
        elif row["LFP"] >= lfp_mid and row["Wage Gap"] > wage_mid:
            return "High LFP + High Wage Gap"
        elif row["LFP"] < lfp_mid and row["Wage Gap"] <= wage_mid:
            return "Low LFP + Low Wage Gap"
        else:
            return "Low LFP + High Wage Gap"

    quad_data["Quadrant"] = quad_data.apply(quadrant, axis=1)
    quad_colors = {
        "High LFP + Low Wage Gap": "#8faf8f",
        "High LFP + High Wage Gap": "#fed9a6",
        "Low LFP + Low Wage Gap": "#b3cde3",
        "Low LFP + High Wage Gap": COLOR_FEMALE,
    }

    fig_quad = px.scatter(
        quad_data, x="LFP", y="Wage Gap",
        color="Quadrant", hover_name="COUNTRY",
        color_discrete_map=quad_colors,
        labels={"LFP": "Female LFP Rate (%)", "Wage Gap": "Gender Wage Gap (%)"}
    )
    fig_quad.add_vline(x=lfp_mid, line_dash="dash", line_color=TEXT, opacity=0.4)
    fig_quad.add_hline(y=wage_mid, line_dash="dash", line_color=TEXT, opacity=0.4)
    fig_quad.add_annotation(x=quad_data["LFP"].max(), y=quad_data["Wage Gap"].max(), text="High LFP + High Wage Gap", showarrow=False, font=dict(size=10, color=TEXT), opacity=0.5)
    fig_quad.add_annotation(x=quad_data["LFP"].min(), y=quad_data["Wage Gap"].max(), text="Low LFP + High Wage Gap", showarrow=False, font=dict(size=10, color=TEXT), opacity=0.5)
    fig_quad.add_annotation(x=quad_data["LFP"].max(), y=quad_data["Wage Gap"].min(), text="High LFP + Low Wage Gap", showarrow=False, font=dict(size=10, color=TEXT), opacity=0.5)
    fig_quad.add_annotation(x=quad_data["LFP"].min(), y=quad_data["Wage Gap"].min(), text="Low LFP + Low Wage Gap", showarrow=False, font=dict(size=10, color=TEXT), opacity=0.5)
    fig_quad.update_traces(marker=dict(size=9, opacity=0.8))
    fig_quad.update_layout(
        height=550, plot_bgcolor=BG, paper_bgcolor=BG,
        font=dict(family="Playfair Display, serif", size=13, color=TEXT),
        xaxis=dict(title="Female LFP Rate (%)", gridcolor="#eeeeee"),
        yaxis=dict(title="Gender Wage Gap (%)", gridcolor="#eeeeee"),
        legend=dict(title="Quadrant"), margin=dict(t=30)
    )
    return fig_heat, fig_quad

# ============================================================
# CALLBACK: INTERACTIVE SCATTER PLOT
# ============================================================

@app.callback(
    Output("cross-scatter", "figure"),
    Output("scatter-corr", "children"),
    Input("scatter-x", "value"),
    Input("scatter-y", "value"),
    Input("scatter-trendline", "value")
)
def update_cross_scatter(x_axis, y_axis, trendline):
    scatter_data = combined_data.dropna(subset=[x_axis, y_axis])
    corr_val = scatter_data[x_axis].corr(scatter_data[y_axis])

    REGION_COLORS = {
        r: c for r, c in zip(
            sorted(scatter_data["REGION"].dropna().unique()),
            ["#fbb4ae", "#b3cde3", "#ccebc5", "#decbe4",
             "#fed9a6", "#ffffcc", "#e5d8bd", "#fddaec", "#f2f2f2"]
        )
    }

    fig = px.scatter(
        scatter_data, x=x_axis, y=y_axis,
        color="REGION", hover_name="COUNTRY",
        trendline="ols" if trendline == "Show" else None,
        color_discrete_map=REGION_COLORS,
        labels={x_axis: x_axis, y_axis: y_axis}
    )
    fig.update_traces(marker=dict(size=9, opacity=0.8))
    fig.update_layout(
        height=550, plot_bgcolor=BG, paper_bgcolor=BG,
        font=dict(family="Playfair Display, serif", size=13, color=TEXT),
        xaxis=dict(title=x_axis, gridcolor="#eeeeee"),
        yaxis=dict(title=y_axis, gridcolor="#eeeeee"),
        legend=dict(title="Region"), margin=dict(t=30)
    )
    corr_text = f"Pearson Correlation: {corr_val:.2f}"
    return fig, corr_text

# ============================================================
# RUN APP
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)