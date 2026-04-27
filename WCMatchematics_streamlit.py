import streamlit as st
import pandas as pd
import numpy as np
import math
import base64
import os
import streamlit.components.v1 as components
from collections import defaultdict
import feedparser
import re
from html import unescape

os.chdir(os.path.dirname(os.path.abspath(__file__)))
st.cache_data.clear()

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="World Cup Simulator",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');

/* ── MOBILE OVERRIDES ── */
@media (max-width: 768px) {
    .groups-grid {
        display: grid !important;
        grid-template-columns: 1fr !important;
        gap: 10px;
    }
    .groups-grid > div {
        order: 0;
    }
    .groups-grid > div:nth-child(1) .group-card:nth-child(1)  { order: 1; }
    .third-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 10px;
    }
    .bracket-slot {
        font-size: 0.55rem !important;
        min-width: 55px !important;
        max-width: 75px !important;
        padding: 2px 3px !important;
    }
    .bracket-wrap {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        transform: scale(0.72);
        transform-origin: top left;
        width: 139%;
    }
}
@media (min-width: 769px) {
    .groups-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 12px;
    }
    .third-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
    }
    .bracket-wrap {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
}

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0a0a0f; color: #e8e4dc; }
[data-testid="stSidebar"] { background: #0f0f18 !important; border-right: 1px solid #1e1e2e; }
[data-testid="stSidebar"] * { color: #e8e4dc !important; }

.main-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 4rem; letter-spacing: 0.08em;
    color: #f0e040; line-height: 1; margin-bottom: 0.1rem;
}
.main-subtitle {
    font-size: 0.9rem; color: #666;
    letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 2rem;
}
.section-header {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem; letter-spacing: 0.1em; color: #f0e040;
    border-bottom: 1px solid #1e1e2e;
    padding-bottom: 0.4rem; margin: 1.5rem 0 1rem 0;
}
.rank-row {
    display: flex; align-items: center;
    padding: 6px 12px; border-radius: 4px; margin-bottom: 2px; font-size: 0.88rem;
}
.rank-row:hover { background: #1a1a2e; }
.rank-num { width: 36px; color: #555; font-size: 0.75rem; }
.rank-name { flex: 1; }
.rank-rating { font-family: monospace; color: #f0e040; font-size: 0.9rem; }
.rank-top { background: #12120a; border-left: 3px solid #f0e040; }

.match-card {
    background: #0f0f18; border: 1px solid #1e1e2e;
    border-radius: 6px; padding: 10px 14px; margin-bottom: 6px;
    font-size: 0.85rem; display: flex; justify-content: space-between; align-items: center;
}
.match-vs { color: #333; font-size: 0.75rem; margin: 0 8px; }

.metric-box {
    background: #0f0f18; border: 1px solid #1e1e2e;
    border-radius: 6px; padding: 16px; text-align: center;
}
.metric-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.2rem; color: #f0e040; letter-spacing: 0.05em;
}
.metric-label {
    font-size: 0.72rem; color: #555;
    text-transform: uppercase; letter-spacing: 0.15em; margin-top: 2px;
}
.winner-banner {
    background: linear-gradient(135deg, #1a1a0a 0%, #12120a 100%);
    border: 2px solid #f0e040; border-radius: 8px;
    padding: 20px 24px; text-align: center; margin: 1rem 0;
}
.winner-label { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 0.2em; }
.winner-name { font-family: 'Bebas Neue', sans-serif; font-size: 3rem; color: #f0e040; letter-spacing: 0.1em; }
.round-label {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.1rem; color: #555; letter-spacing: 0.1em; margin: 1rem 0 0.5rem;
}

.stButton > button {
    background: #f0e040 !important; 
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.1rem !important; 
    letter-spacing: 0.1em !important;
    border: none !important; 
    border-radius: 4px !important;
    padding: 0.5rem 2rem !important; 
    width: 100%;
}
.stButton > button:hover { 
    background: #fff176 !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}
.stButton > button p {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}  border: 1px solid #1e1e2e !important; border-radius: 6px !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# STATIC DATA
# -------------------------------------------------
CONFEDERATION_MAP = {
    "Spain": "UEFA", "England": "UEFA", "France": "UEFA", "Germany": "UEFA",
    "Portugal": "UEFA", "Netherlands": "UEFA", "Italy": "UEFA", "Belgium": "UEFA",
    "Croatia": "UEFA", "Denmark": "UEFA", "Switzerland": "UEFA", "Austria": "UEFA",
    "Sweden": "UEFA", "Norway": "UEFA", "Scotland": "UEFA", "Turkey": "UEFA",
    "Czech Republic": "UEFA", "Bosnia and Herzegovina": "UEFA", "Serbia": "UEFA",
    "Poland": "UEFA", "Ukraine": "UEFA", "Hungary": "UEFA", "Slovakia": "UEFA",
    "Romania": "UEFA", "Greece": "UEFA", "Albania": "UEFA", "Slovenia": "UEFA",
    "Georgia": "UEFA", "Iceland": "UEFA", "Finland": "UEFA", "Wales": "UEFA",
    "Northern Ireland": "UEFA", "Republic of Ireland": "UEFA", "Kosovo": "UEFA",
    "Montenegro": "UEFA", "North Macedonia": "UEFA", "Bulgaria": "UEFA",
    "Luxembourg": "UEFA", "Armenia": "UEFA", "Azerbaijan": "UEFA",
    "Russia": "UEFA", "Estonia": "UEFA", "Latvia": "UEFA", "Lithuania": "UEFA",
    "Moldova": "UEFA", "Belarus": "UEFA", "Malta": "UEFA", "Cyprus": "UEFA",
    "Faroe Islands": "UEFA", "Gibraltar": "UEFA", "Liechtenstein": "UEFA",
    "Andorra": "UEFA", "San Marino": "UEFA", "Israel": "UEFA", "Kazakhstan": "UEFA",
    "Monaco": "UEFA", "Guernsey": "UEFA", "Ellan Vannin": "UEFA", "Jersey": "UEFA",
    "Alderney": "UEFA", "Corsica": "UEFA", "Catalonia": "UEFA", "Basque Country": "UEFA",
    "Galicia": "UEFA", "Occitania": "UEFA", "Brittany": "UEFA", "Padania": "UEFA",
    "Raetia": "UEFA", "Székely Land": "UEFA", "Felvidék": "UEFA", "Délvidék": "UEFA",
    "Kárpátalja": "UEFA", "County of Nice": "UEFA", "Ticino": "UEFA",
    "Western Isles": "UEFA", "Shetland": "UEFA", "Orkney": "UEFA", "Ynys Môn": "UEFA",
    "Isle of Wight": "UEFA", "Isle of Man": "UEFA", "Menorca": "UEFA",
    "Åland Islands": "UEFA", "Gotland": "UEFA", "Frøya": "UEFA", "Hitra": "UEFA",
    "Gozo": "UEFA", "Elba Island": "UEFA", "Franconia": "UEFA", "Surrey": "UEFA",
    "Yorkshire": "UEFA", "Kernow": "UEFA", "Saare County": "UEFA",
    "Luhansk PR": "UEFA", "Donetsk PR": "UEFA", "South Ossetia": "UEFA",
    "Northern Cyprus": "UEFA", "Artsakh": "UEFA", "Western Armenia": "UEFA",
    "Chameria": "UEFA", "Romani people": "UEFA", "Sápmi": "UEFA",
    "Greenland": "UEFA", "Two Sicilies": "UEFA", "Vatican City": "UEFA",
    "Parishes of Jersey": "UEFA", "Abkhazia": "UEFA",
    "Argentina": "CONMEBOL", "Brazil": "CONMEBOL", "Uruguay": "CONMEBOL",
    "Colombia": "CONMEBOL", "Chile": "CONMEBOL", "Ecuador": "CONMEBOL",
    "Peru": "CONMEBOL", "Venezuela": "CONMEBOL", "Bolivia": "CONMEBOL",
    "Paraguay": "CONMEBOL", "Guyana": "CONMEBOL", "Suriname": "CONMEBOL",
    "French Guiana": "CONMEBOL", "Falkland Islands": "CONMEBOL",
    "Mapuche": "CONMEBOL", "Aymara": "CONMEBOL", "Maule Sur": "CONMEBOL",
    "Senegal": "CAF", "Morocco": "CAF", "Nigeria": "CAF", "Algeria": "CAF",
    "Egypt": "CAF", "Ivory Coast": "CAF", "Ghana": "CAF", "Cameroon": "CAF",
    "Mali": "CAF", "Burkina Faso": "CAF", "Tunisia": "CAF", "DR Congo": "CAF",
    "South Africa": "CAF", "Cape Verde": "CAF", "Guinea": "CAF",
    "Mozambique": "CAF", "Zambia": "CAF", "Uganda": "CAF", "Tanzania": "CAF",
    "Zimbabwe": "CAF", "Benin": "CAF", "Gabon": "CAF", "Angola": "CAF",
    "Ethiopia": "CAF", "Kenya": "CAF", "Namibia": "CAF", "Sudan": "CAF",
    "Equatorial Guinea": "CAF", "Mauritania": "CAF", "Congo": "CAF",
    "Rwanda": "CAF", "Niger": "CAF", "Togo": "CAF", "Lesotho": "CAF",
    "Madagascar": "CAF", "Malawi": "CAF", "Guinea-Bissau": "CAF",
    "Liberia": "CAF", "Burundi": "CAF", "Libya": "CAF", "Sierra Leone": "CAF",
    "Central African Republic": "CAF", "Somalia": "CAF", "Chad": "CAF",
    "Eritrea": "CAF", "Zanzibar": "CAF", "São Tomé and Príncipe": "CAF",
    "South Sudan": "CAF", "Djibouti": "CAF", "Botswana": "CAF",
    "Eswatini": "CAF", "Mauritius": "CAF", "Seychelles": "CAF",
    "Gambia": "CAF", "Comoros": "CAF", "Réunion": "CAF", "Mayotte": "CAF",
    "Somaliland": "CAF", "Matabeleland": "CAF", "Kabylia": "CAF",
    "Biafra": "CAF", "Yoruba Nation": "CAF", "Barawa": "CAF", "Saint Helena": "CAF",
    "Japan": "AFC", "South Korea": "AFC", "Iran": "AFC", "Australia": "AFC",
    "Saudi Arabia": "AFC", "Qatar": "AFC", "Iraq": "AFC", "Jordan": "AFC",
    "Uzbekistan": "AFC", "UAE": "AFC", "United Arab Emirates": "AFC",
    "Oman": "AFC", "Bahrain": "AFC", "Kuwait": "AFC", "China": "AFC",
    "China PR": "AFC", "Thailand": "AFC", "Vietnam": "AFC", "Indonesia": "AFC",
    "India": "AFC", "Syria": "AFC", "Palestine": "AFC", "Tajikistan": "AFC",
    "Kyrgyzstan": "AFC", "North Korea": "AFC", "Lebanon": "AFC", "Laos": "AFC",
    "Afghanistan": "AFC", "Guam": "AFC", "Turkmenistan": "AFC", "Myanmar": "AFC",
    "Yemen": "AFC", "Bangladesh": "AFC", "Pakistan": "AFC", "Cambodia": "AFC",
    "Timor-Leste": "AFC", "Sri Lanka": "AFC", "Taiwan": "AFC", "Nepal": "AFC",
    "Mongolia": "AFC", "Macau": "AFC", "Brunei": "AFC", "Bhutan": "AFC",
    "Maldives": "AFC", "Hong Kong": "AFC", "Singapore": "AFC",
    "Malaysia": "AFC", "Philippines": "AFC", "Northern Mariana Islands": "AFC",
    "Panjab": "AFC", "Iraqi Kurdistan": "AFC", "United Koreans in Japan": "AFC",
    "Chagos Islands": "AFC", "West Papua": "AFC", "Tibet": "AFC",
    "Hmong": "AFC", "Tamil Eelam": "AFC", "Ryūkyū": "AFC",
    "Mexico": "CONCACAF", "United States": "CONCACAF", "Canada": "CONCACAF",
    "Panama": "CONCACAF", "Costa Rica": "CONCACAF", "Honduras": "CONCACAF",
    "Jamaica": "CONCACAF", "El Salvador": "CONCACAF", "Haiti": "CONCACAF",
    "Trinidad and Tobago": "CONCACAF", "Guatemala": "CONCACAF",
    "Curaçao": "CONCACAF", "Nicaragua": "CONCACAF", "Cuba": "CONCACAF",
    "Martinique": "CONCACAF", "Guadeloupe": "CONCACAF", "Bermuda": "CONCACAF",
    "Barbados": "CONCACAF", "Saint Kitts and Nevis": "CONCACAF",
    "Bahamas": "CONCACAF", "Dominican Republic": "CONCACAF",
    "United States Virgin Islands": "CONCACAF", "Dominica": "CONCACAF",
    "Turks and Caicos Islands": "CONCACAF", "Saint Lucia": "CONCACAF",
    "Grenada": "CONCACAF", "Aruba": "CONCACAF", "Puerto Rico": "CONCACAF",
    "Belize": "CONCACAF", "Montserrat": "CONCACAF", "Antigua and Barbuda": "CONCACAF",
    "Saint Vincent and the Grenadines": "CONCACAF",
    "Sint Maarten": "CONCACAF", "British Virgin Islands": "CONCACAF",
    "Anguilla": "CONCACAF", "Cayman Islands": "CONCACAF",
    "Saint Barthélemy": "CONCACAF", "Saint Martin": "CONCACAF",
    "Bonaire": "CONCACAF", "Cascadia": "CONCACAF",
    "New Zealand": "OFC", "Fiji": "OFC", "Papua New Guinea": "OFC",
    "Solomon Islands": "OFC", "Vanuatu": "OFC", "Samoa": "OFC",
    "Tonga": "OFC", "Cook Islands": "OFC", "American Samoa": "OFC",
    "New Caledonia": "OFC", "Tahiti": "OFC", "Tuvalu": "OFC",
    "Marshall Islands": "OFC",
}

CONFEDERATION_MEAN = {
    "UEFA": 1620, "CONMEBOL": 1620, "CAF": 1440,
    "AFC": 1400,  "CONCACAF": 1430, "OFC": 1390,
}

GROUPS = {
    "Group A": ["Mexico", "South Africa", "South Korea", "Czech Republic"],
    "Group B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "Group C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "Group D": ["United States", "Paraguay", "Australia", "Turkey"],
    "Group E": ["Germany", "Curaçao", "Ivory Coast", "Ecuador"],
    "Group F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "Group G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "Group H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "Group I": ["France", "Senegal", "Iraq", "Norway"],
    "Group J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "Group K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "Group L": ["England", "Croatia", "Ghana", "Panama"],
}

WC_TEAMS = set(team for teams in GROUPS.values() for team in teams)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.markdown('<div class="main-title">World Cup</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">2026 Simulator</div>', unsafe_allow_html=True)

    rating_system = st.selectbox(
        "Rating System",
        ["Elo", "Massey", "Colley"],
        key="rating_system"
    )

    st.markdown("### 📅 Date Range")
    c1, c2 = st.columns(2)
    with c1:
        start_date = st.date_input("Start", value=pd.to_datetime("2022-01-01"),
                                   min_value=pd.to_datetime("1990-01-01"))
    with c2:
        end_date = st.date_input("End", value=pd.to_datetime("2025-12-31"),
                                 min_value=pd.to_datetime("1990-01-01"))

    burnin_years = st.slider("Burn-in period (years)", 0, 10, 4)

    # --- ELO SETTINGS ---
    if rating_system == "Elo":
        st.markdown("### ⚙️ Elo Settings")
        home_adv   = st.slider("Home advantage",    0,    150, 70)
        decay_rate = st.slider("Time decay rate",   0.00, 0.20, 0.03, step=0.01)
        regression = st.slider("Regression factor", 0.0,  0.5,  0.1,  step=0.05)

        st.markdown("### 🎯 K-Factors")
        with st.expander("Tournament weights", expanded=False):
            k_wc       = st.number_input("FIFA World Cup",       value=75,  min_value=1, max_value=200)
            k_euro     = st.number_input("UEFA Euro",            value=60,  min_value=1, max_value=200)
            k_copa     = st.number_input("Copa America",         value=60,  min_value=1, max_value=200)
            k_afcon    = st.number_input("AFCON",                value=35,  min_value=1, max_value=200)
            k_gold     = st.number_input("Gold Cup",             value=30,  min_value=1, max_value=200)
            k_asian    = st.number_input("Asian Cup",            value=30,  min_value=1, max_value=200)
            k_wcq      = st.number_input("World Cup Qual.",      value=35,  min_value=1, max_value=200)
            k_nl       = st.number_input("Nations League",       value=25,  min_value=1, max_value=200)
            k_euroq    = st.number_input("Euro Qual.",           value=25,  min_value=1, max_value=200)
            k_afconq   = st.number_input("AFCON Qual.",          value=20,  min_value=1, max_value=200)
            k_asianq   = st.number_input("Asian Cup Qual.",      value=20,  min_value=1, max_value=200)
            k_friendly = st.number_input("Friendly",             value=10,  min_value=1, max_value=200)
            k_other    = st.number_input("Other",                value=5,   min_value=1, max_value=200)

        # Dummy values so the cache function signature stays consistent
        massey_home_adv = 0
        massey_regression = 0.0
        colley_home_adv = 0

    elif rating_system == "Massey":
        st.markdown("### Massey Settings")

        massey_weighting = st.selectbox("Age weighting", ["Uniform", "Linear", "Log"], key="m_weight")
        massey_years_back = st.slider("Years back", 1, 10, 4, key="m_yback")

        if massey_weighting == "Log":
            massey_years95 = st.slider("Years for 95% weight", 0.1, 3.0, 0.5, step=0.1, key="m_y95")
            massey_years50 = st.slider("Years for 50% weight", 0.5, 5.0, 3.5, step=0.1, key="m_y50")
        else:
            massey_years95 = 0.5
            massey_years50 = 3.5

        if massey_weighting == "Linear":
            massey_linear_first = st.slider("Weight of oldest game", 0.0, 1.0, 0.2, step=0.05, key="m_lf")
            massey_linear_last  = st.slider("Weight of newest game", 0.0, 1.0, 0.7, step=0.05, key="m_ll")
        else:
            massey_linear_first = 0.2
            massey_linear_last  = 0.7

        massey_max_score = st.slider("Max score difference cap", 1, 20, 10, key="m_maxsc")

        st.markdown("##### Tournament weights")
        with st.expander("Adjust weights", expanded=False):
            m_wt_friendly    = st.number_input("Friendly",             value=1.0, step=0.5, key="m_wf")
            m_wt_cont_qual   = st.number_input("Continental Qual.",    value=2.5, step=0.5, key="m_wcq2")
            m_wt_wcq         = st.number_input("World Cup Qual.",      value=2.5, step=0.5, key="m_wcq")
            m_wt_conf_cup    = st.number_input("Nations League",   value=2.5, step=0.5, key="m_cc") 
            m_wt_cont_final  = st.number_input("Continental Final",    value=3.0, step=0.5, key="m_cf")
            m_wt_wc_final    = st.number_input("World Cup",            value=4.0, step=0.5, key="m_wcf")

    #Colley Settings
    elif rating_system == "Colley":
        st.markdown("### Colley Settings")

        colley_weighting = st.selectbox("Age weighting", ["Uniform", "Linear", "Log"], key="c_weight")
        colley_years_back = st.slider("Years back", 1, 10, 4, key="c_yback")

        if colley_weighting == "Log":
            colley_years95 = st.slider("Years for 95% weight", 0.1, 3.0, 0.5, step=0.1, key="c_y95")
            colley_years50 = st.slider("Years for 50% weight", 0.5, 5.0, 3.5, step=0.1, key="c_y50")
        else:
            colley_years95 = 0.5
            colley_years50 = 3.5

        if colley_weighting == "Linear":
            colley_linear_first = st.slider("Weight of oldest game", 0.0, 1.0, 0.2, step=0.05, key="c_lf")
            colley_linear_last  = st.slider("Weight of newest game", 0.0, 1.0, 1.0, step=0.05, key="c_ll")
        else:
            colley_linear_first = 0.2
            colley_linear_last  = 1.0

        colley_pso = st.slider("Penalty shootout weight", 0.0, 0.5, 0.3, step=0.05, key="c_pso",
                                help="0 = draws treated equally, 0.5 = PSO counts as full win/loss")

        st.markdown("##### Tournament weights")
        with st.expander("Adjust weights", expanded=False):
            c_wt_friendly    = st.number_input("Friendly",             value=1.0, step=0.5, key="c_wf")
            c_wt_cont_qual   = st.number_input("Continental Qual.",    value=2.5, step=0.5, key="c_cq")
            c_wt_wcq         = st.number_input("World Cup Qual.",      value=2.5, step=0.5, key="c_wcq")
            c_wt_conf_cup    = st.number_input("Nations League",   value=2.5, step=0.5, key="c_cc") 
            c_wt_cont_final  = st.number_input("Continental Final",    value=3.0, step=0.5, key="c_cf")
            c_wt_wc_final    = st.number_input("World Cup",            value=4.0, step=0.5, key="c_wcf")

    conf_filter = st.multiselect(
        "Confederation",
        ["UEFA", "CONMEBOL", "CAF", "AFC", "CONCACAF", "OFC"],
        default=["UEFA", "CONMEBOL", "CAF", "AFC", "CONCACAF", "OFC"],
        key="conf_filter",
    )

    run_btn = st.button("▶  RUN SIMULATION")


def get_logo_html(height="60px"):
    logo_path = "IMG_3453.png"  ####### change this filename #########
    if not os.path.exists(logo_path):
        return ""
    with open(logo_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    ext  = logo_path.split(".")[-1].lower()
    mime = "image/svg+xml" if ext == "svg" else f"image/{ext}"
    return (
        '<img src="data:' + mime + ';base64,' + data + '" '
        'style="height:' + height + ';object-fit:contain;margin-bottom:8px;display:block;">'
    )

# -------------------------------------------------
# SPLASH SCREEN
# -------------------------------------------------
if not run_btn and "sim_results" not in st.session_state:
    st.markdown(get_logo_html("80px"), unsafe_allow_html=True)
    st.markdown('<div class="main-title">WORLD CUP MATCH-MATICS</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">World Cup Rating Simulator — configure settings and press Run</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="footer"> <div style="text-align:center"> <small>Created By: Garrett Walker</small></div>', unsafe_allow_html=True)
    st.stop()

# -------------------------------------------------
# CACHED SIMULATION FUNCTION
# -------------------------------------------------
@st.cache_data(show_spinner=False)
def run_simulation(start_date, end_date, burnin_years, home_adv, decay_rate, regression,
                   k_wc, k_euro, k_copa, k_afcon, k_gold, k_asian,
                   k_wcq, k_nl, k_euroq, k_afconq, k_asianq, k_friendly, k_other):

    try:
        all_games = pd.read_csv("all_international_soccer_results.csv", parse_dates=["date"])
    except FileNotFoundError:
        return None

    all_games["home_team"]  = all_games["home_team"].astype(str).str.strip()
    all_games["away_team"]  = all_games["away_team"].astype(str).str.strip()
    all_games["tournament"] = all_games["tournament"].astype(str).str.lower().str.strip()
    all_games["neutral"]    = all_games["neutral"].astype(str).str.lower().isin(["true", "1"])
    all_games["home_score"] = pd.to_numeric(all_games["home_score"], errors="coerce")
    all_games["away_score"] = pd.to_numeric(all_games["away_score"], errors="coerce")
    all_games = all_games.dropna(subset=["home_score", "away_score", "date"])

    start_dt     = pd.to_datetime(start_date)
    end_dt       = pd.to_datetime(end_date)
    burnin_start = start_dt - pd.DateOffset(years=burnin_years)

    burnin_games  = (all_games[(all_games["date"] >= burnin_start) & (all_games["date"] < start_dt)]
                     .sort_values("date").reset_index(drop=True))
    display_games = (all_games[(all_games["date"] >= start_dt) & (all_games["date"] <= end_dt)]
                     .sort_values("date").reset_index(drop=True))

    if display_games.empty:
        return None

    combined    = pd.concat([burnin_games, display_games])
    all_teams   = list(pd.concat([combined["home_team"], combined["away_team"]]).unique())
    team_to_idx = {team: i for i, team in enumerate(all_teams)}
    elo         = np.full(len(all_teams), 1500.0)

    def get_conf_mean(team):
        conf = CONFEDERATION_MAP.get(team)
        return CONFEDERATION_MEAN.get(conf, float(np.mean(elo))) if conf else float(np.mean(elo))

    def exp_score(r1, r2, ha):
        return 1.0 / (10 ** (-((r1 + ha) - r2) / 400) + 1)

    def get_k(t):
        if "friendly" in t:                                              return k_friendly
        if "fifa world cup" in t and "qualification" not in t:           return k_wc
        if "copa america" in t:                                          return k_copa
        if "uefa euro" in t and "qualification" not in t:                return k_euro
        if "african cup of nations" in t and "qualification" not in t:   return k_afcon
        if "gold cup" in t:                                              return k_gold
        if "asian cup" in t and "qualification" not in t:                return k_asian
        if "world cup qualification" in t:                               return k_wcq
        if "nations league" in t:                                        return k_nl
        if "uefa euro qualification" in t:                               return k_euroq
        if "african cup of nations qualification" in t:                  return k_afconq
        if "asian cup qualification" in t:                               return k_asianq
        return k_other

    def gdm(diff):
        if diff <= 1: return 1.0
        if diff == 2: return 1.3
        if diff == 3: return 1.5
        return 1.5 + (diff - 3) / 12.0

    def tdecay(match_date, current_date):
        return math.exp(-decay_rate * (current_date - match_date).days / 365.25)

    team_history = defaultdict(list)

    def run_loop(games_df, track):
        correct, brier, last_yr = 0, 0.0, None
        cur = games_df["date"].max()
        for row in games_df.itertuples():
            yr = row.date.year
            if last_yr is not None and yr != last_yr:
                for team, idx in team_to_idx.items():
                    elo[idx] += regression * (get_conf_mean(team) - elo[idx])
            last_yr = yr
            t1 = team_to_idx[row.home_team]
            t2 = team_to_idx[row.away_team]
            r1, r2 = elo[t1], elo[t2]
            s1, s2 = int(row.home_score), int(row.away_score)
            ha = 0 if row.neutral else home_adv
            We = exp_score(r1, r2, ha)
            W  = 1.0 if s1 > s2 else (0.0 if s1 < s2 else 0.5)
            if track:
                if (We > 0.5 and s1 > s2) or (We < 0.5 and s2 > s1):
                    correct += 1
                brier += (We - W) ** 2
            K  = get_k(row.tournament) * tdecay(row.date, cur) * gdm(abs(s1 - s2))
            ch = K * (W - We)
            elo[t1] += ch
            elo[t2] -= ch
            if track:
                date_str = str(row.date)[:10]
                res_h = "W" if s1 > s2 else ("D" if s1 == s2 else "L")
                res_a = "W" if s2 > s1 else ("D" if s1 == s2 else "L")
                team_history[row.home_team].append((date_str, row.away_team, s1, s2, res_h, ch))
                team_history[row.away_team].append((date_str, row.home_team, s2, s1, res_a, -ch))
        return correct, len(games_df), brier

    run_loop(burnin_games, False)
    team_history = defaultdict(list)
    for row in display_games.sort_values("date").itertuples():
        t1_name = row.home_team
        t2_name = row.away_team
        s1, s2 = int(row.home_score), int(row.away_score)
        result_h = "W" if s1 > s2 else ("D" if s1 == s2 else "L")
        result_a = "W" if s2 > s1 else ("D" if s1 == s2 else "L")
        date_str = str(row.date)[:10]
        team_history[t1_name].append((date_str, t2_name, s1, s2, result_h, 0.0))
        team_history[t2_name].append((date_str, t1_name, s2, s1, result_a, 0.0))
    
    correct_preds, total_games, brier_total = run_loop(display_games, True)

    ratings = {team: float(elo[team_to_idx[team]]) for team in all_teams}

    # Group stage
    group_results    = {}
    third_place_list = []
    for group_name, team_list in GROUPS.items():
        letter = group_name.split()[-1]
        ranked = sorted([(t, ratings.get(t, 1500.0)) for t in team_list], key=lambda x: -x[1])
        group_results[letter] = ranked
        third_place_list.append((letter, ranked[2][0], ranked[2][1]))

    third_place_list.sort(key=lambda x: -x[2])
    best_third   = third_place_list[:8]
    third_lookup = {grp: team for grp, team, _ in best_third}

    try:
        df = pd.read_csv("third_place_combinations.csv", header=None)
        df = df.drop(index=[0, 1]).reset_index(drop=True)
        scm = {"1A": 12, "1B": 13, "1D": 14, "1E": 15, "1G": 16, "1I": 17, "1K": 18, "1L": 19}
        ftable = {}
        for _, row in df.iterrows():
            key = frozenset(str(row[i]).strip() for i in range(12)
                            if pd.notna(row[i]) and str(row[i]).strip() not in ("", "nan"))
            if len(key) == 8:
                ftable[key] = {s: str(row[c]).strip() for s, c in scm.items()}
        bkg = frozenset(g for g, _, _ in best_third)
        if bkg in ftable:
            tpm = ftable[bkg]
    except Exception:
        pass

    def resolve(label):
        if label.startswith("1"): return group_results[label[1]][0][0]
        if label.startswith("2"): return group_results[label[1]][1][0]
        return third_lookup.get(label[1], "TBD")

    def sim(t1, t2):
        return t1 if ratings.get(t1, 1500) >= ratings.get(t2, 1500) else t2

    r32s = [
        (73,"2A","2B"),(74,"1E",tpm.get("1E","3D")),(75,"1F","2C"),(76,"1C","2F"),
        (77,"1I",tpm.get("1I","3F")),(78,"2E","2I"),(79,"1A",tpm.get("1A","3E")),
        (80,"1L",tpm.get("1L","3K")),(81,"1D",tpm.get("1D","3I")),(82,"1G",tpm.get("1G","3J")),
        (83,"2K","2L"),(84,"1H","2J"),(85,"1B",tpm.get("1B","3G")),
        (86,"1J","2H"),(87,"1K",tpm.get("1K","3L")),(88,"2D","2G"),
    ]
    r32_w = {}
    r32_matches = []
    for mn, l1, l2 in r32s:
        t1, t2 = resolve(l1), resolve(l2)
        w = sim(t1, t2)
        r32_w[mn] = w
        r32_matches.append((mn, t1, t2, w))

    r16s = [(89,74,77),(90,73,75),(91,76,78),(92,79,80),(93,83,84),(94,81,82),(95,86,88),(96,85,87)]
    r16_w = {}
    r16_matches = []
    for mn, m1, m2 in r16s:
        t1, t2 = r32_w[m1], r32_w[m2]
        w = sim(t1, t2)
        r16_w[mn] = w
        r16_matches.append((mn, t1, t2, w))

    qfs = [(97,89,90),(98,93,94),(99,91,92),(100,95,96)]
    qf_w = {}
    qf_matches = []
    for mn, m1, m2 in qfs:
        t1, t2 = r16_w[m1], r16_w[m2]
        w = sim(t1, t2)
        qf_w[mn] = w
        qf_matches.append((mn, t1, t2, w))

    sfs = [(101,97,98),(102,99,100)]
    sf_w, sf_l = {}, {}
    sf_matches = []
    for mn, m1, m2 in sfs:
        t1, t2 = qf_w[m1], qf_w[m2]
        w = sim(t1, t2)
        sf_w[mn] = w
        sf_l[mn] = t2 if w == t1 else t1
        sf_matches.append((mn, t1, t2, w))

    b1, b2   = sf_l[101], sf_l[102]
    f1, f2   = sf_w[101], sf_w[102]
    bronze_w = sim(b1, b2)
    final_w  = sim(f1, f2)

    return {
        "ratings":       ratings,
        "all_teams":     all_teams,
        "group_results": group_results,
        "best_third":    best_third,
        "r32_matches":   r32_matches,
        "r16_matches":   r16_matches,
        "qf_matches":    qf_matches,
        "sf_matches":    sf_matches,
        "bronze":        (b1, b2, bronze_w),
        "final":         (f1, f2, final_w),
        "total_games":   total_games,
        "burnin_count":  len(burnin_games),
    }

def _build_bracket_result(ratings, all_teams, display_games):
    """Shared bracket builder used by Massey and Colley."""
    group_results    = {}
    third_place_list = []
    for group_name, team_list in GROUPS.items():
        letter = group_name.split()[-1]
        ranked = sorted([(t, ratings.get(t, 1500.0)) for t in team_list], key=lambda x: -x[1])
        group_results[letter] = ranked
        third_place_list.append((letter, ranked[2][0], ranked[2][1]))

    third_place_list.sort(key=lambda x: -x[2])
    best_third   = third_place_list[:8]
    third_lookup = {grp: team for grp, team, _ in best_third}

    tpm = {"1A": "3E", "1B": "3G", "1D": "3I", "1E": "3D",
           "1G": "3J", "1I": "3F", "1K": "3L", "1L": "3K"}
    try:
        df = pd.read_csv("third_place_combinations.csv", header=None)
        df = df.drop(index=[0, 1]).reset_index(drop=True)
        scm = {"1A": 12, "1B": 13, "1D": 14, "1E": 15,
               "1G": 16, "1I": 17, "1K": 18, "1L": 19}
        ftable = {}
        for _, row in df.iterrows():
            key = frozenset(str(row[i]).strip() for i in range(12)
                            if pd.notna(row[i]) and str(row[i]).strip() not in ("", "nan"))
            if len(key) == 8:
                ftable[key] = {s: str(row[c]).strip() for s, c in scm.items()}
        bkg = frozenset(g for g, _, _ in best_third)
        if bkg in ftable:
            tpm = ftable[bkg]
    except Exception:
        pass

    def resolve(label):
        if label.startswith("1"): return group_results[label[1]][0][0]
        if label.startswith("2"): return group_results[label[1]][1][0]
        return third_lookup.get(label[1], "TBD")

    def sim(t1, t2):
        return t1 if ratings.get(t1, 1500) >= ratings.get(t2, 1500) else t2

    r32s = [
        (73,"2A","2B"),(74,"1E",tpm.get("1E","3D")),(75,"1F","2C"),(76,"1C","2F"),
        (77,"1I",tpm.get("1I","3F")),(78,"2E","2I"),(79,"1A",tpm.get("1A","3E")),
        (80,"1L",tpm.get("1L","3K")),(81,"1D",tpm.get("1D","3I")),(82,"1G",tpm.get("1G","3J")),
        (83,"2K","2L"),(84,"1H","2J"),(85,"1B",tpm.get("1B","3G")),
        (86,"1J","2H"),(87,"1K",tpm.get("1K","3L")),(88,"2D","2G"),
    ]
    r32_w, r32_matches = {}, []
    for mn, l1, l2 in r32s:
        t1, t2 = resolve(l1), resolve(l2)
        w = sim(t1, t2)
        r32_w[mn] = w
        r32_matches.append((mn, t1, t2, w))

    r16s = [(89,74,77),(90,73,75),(91,76,78),(92,79,80),(93,83,84),(94,81,82),(95,86,88),(96,85,87)]
    r16_w, r16_matches = {}, []
    for mn, m1, m2 in r16s:
        t1, t2 = r32_w[m1], r32_w[m2]
        w = sim(t1, t2)
        r16_w[mn] = w
        r16_matches.append((mn, t1, t2, w))

    qfs = [(97,89,90),(98,93,94),(99,91,92),(100,95,96)]
    qf_w, qf_matches = {}, []
    for mn, m1, m2 in qfs:
        t1, t2 = r16_w[m1], r16_w[m2]
        w = sim(t1, t2)
        qf_w[mn] = w
        qf_matches.append((mn, t1, t2, w))

    sfs = [(101,97,98),(102,99,100)]
    sf_w, sf_l, sf_matches = {}, {}, []
    for mn, m1, m2 in sfs:
        t1, t2 = qf_w[m1], qf_w[m2]
        w = sim(t1, t2)
        sf_w[mn] = w
        sf_l[mn] = t2 if w == t1 else t1
        sf_matches.append((mn, t1, t2, w))

    b1, b2   = sf_l[101], sf_l[102]
    f1, f2   = sf_w[101], sf_w[102]
    bronze_w = sim(b1, b2)
    final_w  = sim(f1, f2)

    return {
        "ratings":       ratings,
        "all_teams":     all_teams,
        "group_results": group_results,
        "best_third":    best_third,
        "r32_matches":   r32_matches,
        "r16_matches":   r16_matches,
        "qf_matches":    qf_matches,
        "sf_matches":    sf_matches,
        "bronze":        (b1, b2, bronze_w),
        "final":         (f1, f2, final_w),
        "total_games":   len(display_games),
        "burnin_count":  0,
    }

@st.cache_data(show_spinner=False)
def run_massey(start_date, end_date, burnin_years,
               weighting, years_back, years95, years50,
               wt_friendly, wt_cont_qual, wt_wcq, wt_conf_cup,
               wt_cont_final, wt_wc_final,
               max_score_diff, pso_val,
               linear_first, linear_last):

    try:
        all_games = pd.read_csv("all_international_soccer_results.csv", parse_dates=["date"])
    except FileNotFoundError:
        return None

    all_games["home_team"]  = all_games["home_team"].astype(str).str.strip()
    all_games["away_team"]  = all_games["away_team"].astype(str).str.strip()
    all_games["tournament"] = all_games["tournament"].astype(str).str.lower().str.strip()
    all_games["neutral"]    = all_games["neutral"].astype(str).str.lower().isin(["true", "1"])
    all_games["home_score"] = pd.to_numeric(all_games["home_score"], errors="coerce")
    all_games["away_score"] = pd.to_numeric(all_games["away_score"], errors="coerce")
    all_games = all_games.dropna(subset=["home_score", "away_score", "date"])

    start_dt     = pd.to_datetime(start_date)
    end_dt       = pd.to_datetime(end_date)
    burnin_start = start_dt - pd.DateOffset(years=burnin_years)

    display_games = (all_games[(all_games["date"] >= burnin_start) & (all_games["date"] <= end_dt)]
                     .sort_values("date").reset_index(drop=True))
    show_games    = (all_games[(all_games["date"] >= start_dt) & (all_games["date"] <= end_dt)]
                     .sort_values("date").reset_index(drop=True))

    if show_games.empty:
        return None

    all_teams   = sorted(set(display_games["home_team"]) | set(display_games["away_team"]))
    team_to_idx = {t: i for i, t in enumerate(all_teams)}
    n           = len(all_teams)

    last_date  = display_games["date"].max()
    start_date_dt = display_games["date"].min()
    date_gap   = max((last_date - start_date_dt).days, 1)

    # --- Age weighting function ---
    if weighting == "Log":
        A_log = (-years_back) / (years50 - years95) * math.log(0.95 / 0.05)
        B_log = (years_back - years50) / (years50 - years95) * math.log(0.95 / 0.05)
        def age_weight(x):
            return 1.0 / (1.0 + math.exp(A_log * x + B_log))
    elif weighting == "Linear":
        def age_weight(x):
            return linear_first + x * (linear_last - linear_first)
    else:
        def age_weight(x):
            return 1.0

    # --- Tournament type → weight ---
    def get_tournament_weight(tournament):
        t = tournament
        if "friendly" in t:                                              return wt_friendly
        if "fifa world cup" in t and "qualification" not in t:           return wt_wc_final
        if "copa america" in t or "uefa euro" in t or "african cup" in t \
           or "gold cup" in t or "asian cup" in t:
            if "qualification" not in t:                                 return wt_cont_final
        if "world cup qualification" in t:                               return wt_wcq
        if "qualification" in t:                                         return wt_cont_qual
        if "confederations cup" in t or "nations league" in t:           return wt_conf_cup #confed cup doesn't exist anymore
        return wt_friendly

    # --- Build Massey matrix ---
    M = np.zeros((n, n))
    b = np.zeros(n)

    for row in display_games.itertuples():
        t1 = team_to_idx.get(row.home_team, -1)
        t2 = team_to_idx.get(row.away_team, -1)
        if t1 < 0 or t2 < 0:
            continue

        days_from_start = max((row.date - start_date_dt).days, 0)
        x  = days_from_start / date_gap
        wm = age_weight(x)
        tw = get_tournament_weight(row.tournament)
        w  = wm * tw

        s1 = int(row.home_score)
        s2 = int(row.away_score)

        M[t1][t2] -= w
        M[t2][t1] -= w
        M[t1][t1] += w
        M[t2][t2] += w

        if s1 > s2:
            delta = min(s1 - s2, max_score_diff)
        elif s1 < s2:
            delta = max(s1 - s2, -max_score_diff)
        else:
            delta = 0.0

        b[t1] += w * delta
        b[t2] -= w * delta

    # Replace last row with sum = 0 constraint
    M[-1] = np.ones(n)
    b[-1] = 0.0

    try:
        r = np.linalg.solve(M, b)
    except np.linalg.LinAlgError:
        r = np.zeros(n)

    try:
        r = np.linalg.solve(M, b)
    except np.linalg.LinAlgError:
        try:
            r = np.linalg.lstsq(M, b, rcond=None)[0]
        except Exception:
            r = np.zeros(n)
   
    ratings = {team: float(r[team_to_idx[team]])
               for team in all_teams}

    result = _build_bracket_result(ratings, all_teams, show_games)
    result["burnin_count"] = len(display_games) - len(show_games)
    return result


@st.cache_data(show_spinner=False)
def run_colley(start_date, end_date, burnin_years,
               weighting, years_back, years95, years50,
               wt_friendly, wt_cont_qual, wt_wcq, wt_conf_cup,
               wt_cont_final, wt_wc_final,
               pso_weight,
               linear_first, linear_last):

    try:
        all_games = pd.read_csv("all_international_soccer_results.csv", parse_dates=["date"])
    except FileNotFoundError:
        return None

    all_games["home_team"]  = all_games["home_team"].astype(str).str.strip()
    all_games["away_team"]  = all_games["away_team"].astype(str).str.strip()
    all_games["tournament"] = all_games["tournament"].astype(str).str.lower().str.strip()
    all_games["neutral"]    = all_games["neutral"].astype(str).str.lower().isin(["true", "1"])
    all_games["home_score"] = pd.to_numeric(all_games["home_score"], errors="coerce")
    all_games["away_score"] = pd.to_numeric(all_games["away_score"], errors="coerce")
    all_games = all_games.dropna(subset=["home_score", "away_score", "date"])

    start_dt     = pd.to_datetime(start_date)
    end_dt       = pd.to_datetime(end_date)
    burnin_start = start_dt - pd.DateOffset(years=burnin_years)

    display_games = (all_games[(all_games["date"] >= burnin_start) & (all_games["date"] <= end_dt)]
                     .sort_values("date").reset_index(drop=True))
    show_games    = (all_games[(all_games["date"] >= start_dt) & (all_games["date"] <= end_dt)]
                     .sort_values("date").reset_index(drop=True))

    if show_games.empty:
        return None

    all_teams   = sorted(set(display_games["home_team"]) | set(display_games["away_team"]))
    team_to_idx = {t: i for i, t in enumerate(all_teams)}
    n           = len(all_teams)

    last_date     = display_games["date"].max()
    start_date_dt = display_games["date"].min()
    date_gap      = max((last_date - start_date_dt).days, 1)
    pso_deflate   = 1.0 - 2.0 * pso_weight

    if weighting == "Log":
        A_log = (-years_back) / (years50 - years95) * math.log(0.95 / 0.05)
        B_log = (years_back - years50) / (years50 - years95) * math.log(0.95 / 0.05)
        def age_weight(x):
            return 1.0 / (1.0 + math.exp(A_log * x + B_log))
    elif weighting == "Linear":
        def age_weight(x):
            return linear_first + x * (linear_last - linear_first)
    else:
        def age_weight(x):
            return 1.0

    def get_tournament_weight(tournament):
        t = tournament
        if "friendly" in t:                                              return wt_friendly
        if "fifa world cup" in t and "qualification" not in t:           return wt_wc_final
        if "copa america" in t or "uefa euro" in t or "african cup" in t \
           or "gold cup" in t or "asian cup" in t:
            if "qualification" not in t:                                 return wt_cont_final
        if "world cup qualification" in t:                               return wt_wcq
        if "qualification" in t:                                         return wt_cont_qual
        if "confederations cup" in t or "nations league" in t:           return wt_conf_cup #confed cup doesn't exist anymore
        return wt_friendly

    # --- Build Colley matrix ---
    C = np.zeros((n, n))
    for i in range(n):
        C[i][i] = 2.0
    b = np.ones(n)

    for row in display_games.itertuples():
        t1 = team_to_idx.get(row.home_team, -1)
        t2 = team_to_idx.get(row.away_team, -1)
        if t1 < 0 or t2 < 0:
            continue

        days_from_start = max((row.date - start_date_dt).days, 0)
        x  = days_from_start / date_gap
        wm = age_weight(x)
        tw = get_tournament_weight(row.tournament)
        w  = wm * tw

        s1 = int(row.home_score)
        s2 = int(row.away_score)

        C[t1][t2] -= w
        C[t2][t1] -= w
        C[t1][t1] += w
        C[t2][t2] += w

        if s1 > s2:
            b[t1] += w / 2.0
            b[t2] -= w / 2.0
        elif s1 < s2:
            b[t2] += w / 2.0
            b[t1] -= w / 2.0
        # draws: no change (treat as 0.5 win each, cancels out)

    try:
        r = np.linalg.solve(C, b)
    except np.linalg.LinAlgError:
        r = np.full(n, 0.5)

    ratings = {team: float(r[team_to_idx[team]])
               for team in all_teams}

    result = _build_bracket_result(ratings, all_teams, show_games)
    result["burnin_count"] = len(display_games) - len(show_games)
    return result

# -------------------------------------------------
# TRIGGER SIMULATION
# -------------------------------------------------
if run_btn:
    with st.spinner("Running simulation..."):
        if rating_system == "Elo":
            result = run_simulation(
                str(start_date), str(end_date), burnin_years, home_adv, decay_rate, regression,
                k_wc, k_euro, k_copa, k_afcon, k_gold, k_asian,
                k_wcq, k_nl, k_euroq, k_afconq, k_asianq, k_friendly, k_other
            )
        elif rating_system == "Massey":
            result = run_massey(
                str(start_date), str(end_date), burnin_years,
                massey_weighting, massey_years_back, massey_years95, massey_years50,
                m_wt_friendly, m_wt_cont_qual, m_wt_wcq, m_wt_conf_cup,
                m_wt_cont_final, m_wt_wc_final,
                massey_max_score, 0.3,
                massey_linear_first, massey_linear_last
            )
        elif rating_system == "Colley":
            result = run_colley(
                str(start_date), str(end_date), burnin_years,
                colley_weighting, colley_years_back, colley_years95, colley_years50,
                c_wt_friendly, c_wt_cont_qual, c_wt_wcq, c_wt_conf_cup,
                c_wt_cont_final, c_wt_wc_final,
                colley_pso,
                colley_linear_first, colley_linear_last
            )

    if result is None:
        st.error("Could not load data or no games in selected range.")
        st.stop()
    st.session_state["sim_results"] = result
    st.session_state["rating_system_used"] = rating_system

result = st.session_state.get("sim_results")
if result is None:
    st.stop()

ratings       = result["ratings"]
all_teams     = result["all_teams"]
group_results = result["group_results"]
best_third    = result["best_third"]
f1, f2, fw    = result["final"]

# -------------------------------------------------
# PAGE HEADER
# -------------------------------------------------
st.markdown(get_logo_html("60px"), unsafe_allow_html=True)
st.markdown('<div class="main-title">WORLD CUP MATCH-MATICS</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="main-subtitle">{start_date} → {end_date}'
    f' &nbsp;·&nbsp; {result["total_games"]:,} games'
    f' &nbsp;·&nbsp; {result["burnin_count"]:,} burn-in</div>',
    unsafe_allow_html=True
)

mc1, mc2 = st.columns(2)
mc1.markdown(
    f'<div class="metric-box"><div class="metric-value">{burnin_years}yr</div>'
    f'<div class="metric-label">Burn-in Period</div></div>',
    unsafe_allow_html=True
)
mc2.markdown(
    f'<div class="metric-box"><div class="metric-value">{result["burnin_count"]:,}</div>'
    f'<div class="metric-label">Burn-in Games</div></div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="winner-banner">'
    f'<div class="winner-label">🏆 Predicted Tournament Winner</div>'
    f'<div class="winner-name">{fw}</div>'
    f'</div>',
    unsafe_allow_html=True
)

# -------------------------------------------------
# TABS
# -------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Rankings", "Groups", "Bracket", "Help"])

# ── RANKINGS TAB ─────────────────────────────────
with tab1:
    rankings_col, news_col = st.columns([2, 1])

    with rankings_col:
        st.markdown('<div class="section-header">RANKINGS</div>', unsafe_allow_html=True)

        sorted_teams = sorted(all_teams, key=lambda t: -ratings.get(t, 1500))
        rating_system_used = st.session_state.get("rating_system_used", "Elo")
        fmt = ".4f" if rating_system_used in ("Massey", "Colley") else ".0f"


        rows = []
        displayed = 0
        for team in sorted_teams:
            conf = CONFEDERATION_MAP.get(team, "")
            if conf not in conf_filter:
                continue
            displayed += 1
            rating  = ratings.get(team, 1500)
            is_top  = displayed <= 10
            is_wc   = team in WC_TEAMS

            row_style = (
                "display:flex;align-items:center;padding:6px 12px;border-radius:4px;"
                "margin-bottom:2px;font-size:0.88rem;width:fit-content;"
                + ("background:#12120a;border-left:3px solid #f0e040;" if is_top else "")
            )
            name_style = "display:inline-block;min-width:200px;" + ("color:#4caf50;font-weight:500;" if is_wc else "")

            rows.append(
                f'<div style="{row_style}">'
                f'<span style="width:36px;color:#888;font-size:0.75rem;">{displayed}</span>'
                f'<span style="{name_style}">{team}</span>'
                f'<span style="font-family:monospace;color:#f0e040;font-size:0.9rem;">' + format(rating, fmt) + '</span>'
                f'</div>'
            )

        st.markdown("".join(rows), unsafe_allow_html=True)
        st.markdown('<div class="footer"><div style="text-align:center"><small>Created By: Garrett Walker</small></div>', unsafe_allow_html=True)



    def clean_html(text):
        text = re.sub('<.*?>', '', text)
        return unescape(text)

    with news_col:
        st.markdown('<div class="section-header">RECENT NEWS</div>', unsafe_allow_html=True)

        # Try multiple feeds in case one is blocked by the host
        news_items = []
        feeds_to_try = [
            "https://feeds.bbci.co.uk/sport/football/rss.xml",
            "https://www.theguardian.com/football/rss",
            "https://www.espn.com/espn/rss/soccer/news",
        ]
        for feed_url in feeds_to_try:
            try:
                feed = feedparser.parse(feed_url)
                if feed.entries:
                    news_items = feed.entries[:8]
                    break
            except Exception:
                continue

        if not news_items:
            st.markdown(
                '<div style="color:#555;font-size:0.82rem;padding:8px 0;">News unavailable — RSS feed could not be reached from this server.</div>',
                unsafe_allow_html=True
            )
        else:
            # Build the whole block as one HTML string so open/close divs stay together
            links_html = ""
            for entry in news_items:
                title = unescape(re.sub('<.*?>', '', entry.get("title", "")))
                link  = entry.get("link", "#")
                links_html += (
                    f'<a href="{link}" target="_blank" rel="noopener noreferrer" '
                    f'style="display:block;margin-bottom:14px;color:#e6e6e6;'
                    f'font-size:0.83rem;text-decoration:none;line-height:1.4;'
                    f'border-bottom:1px solid #1a1a2e;padding-bottom:10px;">'
                    f'{title}'
                    f'</a>'
                )
            st.markdown(
                f'<div style="background:#0a0a0f;padding:12px;border-radius:6px;">{links_html}</div>',
                unsafe_allow_html=True
            )

# ── GROUPS TAB ───────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">GROUP STAGE RANKINGS</div>', unsafe_allow_html=True)

    best_third_set = {(g, t) for g, t, _ in best_third}

    col_html = ["", "", ""]
    all_group_cards = []

    for gi, (group_name, team_list) in enumerate(GROUPS.items()):
        letter = group_name.split()[-1]
        ranked = group_results[letter]

        rows_html = ""
        for pos, (team, rating) in enumerate(ranked, 1):
            if pos <= 2:
                badge = '<span style="color:#f0e040;font-size:0.65rem;margin-left:5px;font-weight:600;">Q</span>'
            elif (letter, team) in best_third_set:
                badge = '<span style="color:#4caf50;font-size:0.65rem;margin-left:5px;font-weight:600;">3rd</span>'
            else:
                badge = ""

            name_color = "#aaa" if pos <= 2 else "#666"
            row_bg     = "background:#13130a;" if pos <= 2 else ""

            rating_system_used = st.session_state.get("rating_system_used", "Elo")
            fmt_rating = round(rating, 4) if rating_system_used in ("Massey", "Colley") else int(rating)

            rows_html += (
                '<div style="display:flex;justify-content:space-between;align-items:center;'
                'padding:5px 8px;border-bottom:1px solid #1a1a2e;' + row_bg + '">'
                '<span style="color:#888;font-size:0.72rem;width:14px;">' + str(pos) + '</span>'
                '<span style="flex:1;font-size:0.83rem;color:' + name_color + ';">' + team + badge + '</span>'
                '<span style="font-family:monospace;font-size:0.8rem;color:#888;">' + str(fmt_rating) + '</span>'
                '</div>'
            )

        card_html = (
            '<div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;'
            'padding:12px;margin-bottom:10px;">'
            '<div style="font-family:Bebas Neue,sans-serif;font-size:1rem;'
            'letter-spacing:0.1em;color:#f0e040;margin-bottom:8px;">GROUP ' + letter + '</div>'
            + rows_html +
            '</div>'
        )

        col_html[gi % 3] += card_html
        all_group_cards.append(card_html)

    # Desktop: 3 columns. Mobile: single column in alphabetical order via flat list
    flat_html = "".join(all_group_cards)

    st.markdown(
        '<style>'
        '.groups-desktop { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }'
        '.groups-mobile  { display: none; }'
        '@media (max-width: 768px) {'
        '  .groups-desktop { display: none !important; }'
        '  .groups-mobile  { display: block !important; }'
        '}'
        '</style>'
        '<div class="groups-desktop">'
        '<div>' + col_html[0] + '</div>'
        '<div>' + col_html[1] + '</div>'
        '<div>' + col_html[2] + '</div>'
        '</div>'
        '<div class="groups-mobile">' + flat_html + '</div>',
        unsafe_allow_html=True
    )


    st.markdown('<div class="section-header">BEST 3RD PLACE TEAMS</div>', unsafe_allow_html=True)
    third_cards = ""
    for grp, team, rating in best_third:
        rating_system_used = st.session_state.get("rating_system_used", "Elo")
        fmt_rating = round(rating, 4) if rating_system_used in ("Massey", "Colley") else int(rating)

        third_cards += (
            '<div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;'
            'padding:16px;text-align:center;">'
            '<div style="font-family:Bebas Neue,sans-serif;font-size:1.3rem;color:#f0e040;letter-spacing:0.05em;">' + team + '</div>'
            '<div style="font-size:0.72rem;color:#555;text-transform:uppercase;letter-spacing:0.15em;margin-top:2px;">Group ' + grp + ' &middot; ' + str(fmt_rating) + '</div>'
            '</div>'
        )
    st.markdown(
        '<div class="third-grid">' + third_cards + '</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="footer"> <div style="text-align:center"> <small>Created By: Garrett Walker</small></div>', unsafe_allow_html=True)

# ── BRACKET TAB ──────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">TOURNAMENT BRACKET</div>', unsafe_allow_html=True)

    def team_slot(team, winner=False, align="left"):
        bg     = "#1a1a0a" if winner else "#0f0f18"
        color  = "#f0e040" if winner else "#888"
        border = "1px solid #f0e040" if winner else "1px solid #1e1e2e"
        ta     = "right" if align == "right" else "left"
        return (
            '<div class="bracket-slot" style="background:' + bg + ';border:' + border + ';'
            'border-radius:3px;padding:3px 6px;font-size:0.72rem;color:' + color + ';'
            'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'
            'max-width:130px;min-width:100px;text-align:' + ta + ';">' + team + '</div>'
        )

    def match_pair(t1, t2, winner, align="left"):
        gap = "2px"
        return (
            '<div style="display:flex;flex-direction:column;gap:' + gap + ';margin:4px 0;">'
            + team_slot(t1, t1 == winner, align)
            + team_slot(t2, t2 == winner, align)
            + '</div>'
        )

    r32 = result["r32_matches"]
    r16 = result["r16_matches"]
    qf  = result["qf_matches"]
    sf  = result["sf_matches"]
    b1, b2, bw = result["bronze"]
    f1, f2, fw = result["final"]

    def col_matches(matches, align="left"):
        html = '<div style="display:flex;flex-direction:column;justify-content:space-around;flex:1;">'
        for mn, t1, t2, w in matches:
            html += match_pair(t1, t2, w, align)
        html += '</div>'
        return html

    def connector_col(n, direction="right"):
        lines = ""
        for i in range(n):
            lines += (
                '<div style="display:flex;flex-direction:column;justify-content:center;flex:1;">'
                '<div style="border-top:1px solid #333;border-' + direction + ':1px solid #333;'
                'border-bottom:1px solid #333;height:calc(50% + 6px);margin-bottom:-1px;"></div>'
                '</div>'
            )
        return '<div style="display:flex;flex-direction:column;width:12px;flex-shrink:0;">' + lines + '</div>'

    r32_by_num = {mn: (mn, t1, t2, w) for mn, t1, t2, w in r32}
    r16_by_num = {mn: (mn, t1, t2, w) for mn, t1, t2, w in r16}
    qf_by_num  = {mn: (mn, t1, t2, w) for mn, t1, t2, w in qf}
    sf_by_num  = {mn: (mn, t1, t2, w) for mn, t1, t2, w in sf}

    # Left side top to bottom — pairs that meet in R16 grouped together
    left_r32  = col_matches([r32_by_num[74], r32_by_num[77],
                          r32_by_num[73], r32_by_num[75],
                          r32_by_num[76], r32_by_num[78],
                          r32_by_num[79], r32_by_num[80]])

    left_r16  = col_matches([r16_by_num[89], r16_by_num[90],
                          r16_by_num[91], r16_by_num[92]])

    left_qf   = col_matches([qf_by_num[97], qf_by_num[99]])
    left_sf   = col_matches([sf_by_num[101]])

    # Right side top to bottom
    right_r32 = col_matches([r32_by_num[83], r32_by_num[84],
                          r32_by_num[81], r32_by_num[82],
                          r32_by_num[86], r32_by_num[88],
                          r32_by_num[85], r32_by_num[87]], "right")

    right_r16 = col_matches([r16_by_num[93], r16_by_num[94],
                          r16_by_num[95], r16_by_num[96]], "right")

    right_qf  = col_matches([qf_by_num[98], qf_by_num[100]], "right")
    right_sf  = col_matches([sf_by_num[102]], "right")

    final_html = (
        '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;padding:0 8px;">'
        '<div style="font-family:Bebas Neue,sans-serif;font-size:0.8rem;color:#888;letter-spacing:0.1em;margin-bottom:4px;">FINAL</div>'
        + team_slot(f1, f1 == fw, "left")
        + team_slot(f2, f2 == fw, "left")
        + '<div style="font-family:Bebas Neue,sans-serif;font-size:1.4rem;color:#f0e040;margin-top:6px;letter-spacing:0.08em;">CHAMPION</div>'
        '<div style="font-family:Bebas Neue,sans-serif;font-size:1.35rem;color:#f0e040;letter-spacing:0.05em;">' + fw + '</div>'
        + '<div style="margin-top:12px;border-top:1px solid #1e1e2e;padding-top:8px;width:100%;text-align:center;">'
        + '<div style="font-family:Bebas Neue,sans-serif;font-size:0.9rem;color:#888;letter-spacing:0.1em;">3RD PLACE</div>'
        + team_slot(b1, b1 == bw, "left")
        + team_slot(b2, b2 == bw, "left")
        + '</div>'
        + '</div>'
    )

    bracket_html = (
        '<div style="display:flex;align-items:stretch;gap:0;overflow-x:auto;padding:12px 0;">'

        '<div style="display:flex;flex-direction:column;gap:0;">'
        '<div style="font-family:Bebas Neue,sans-serif;font-size:0.7rem;color:#888;letter-spacing:0.1em;margin-bottom:4px;">R32</div>'
        + left_r32 + '</div>'

        '<div style="display:flex;flex-direction:column;gap:0;">'
        '<div style="font-family:Bebas Neue,sans-serif;font-size:0.7rem;color:#888;letter-spacing:0.1em;margin-bottom:4px;">R16</div>'
        + left_r16 + '</div>'

        '<div style="display:flex;flex-direction:column;gap:0;">'
        '<div style="font-family:Bebas Neue,sans-serif;font-size:0.7rem;color:#888;letter-spacing:0.1em;margin-bottom:4px;">QF</div>'
        + left_qf + '</div>'

        '<div style="display:flex;flex-direction:column;gap:0;">'
        '<div style="font-family:Bebas Neue,sans-serif;font-size:0.7rem;color:#888;letter-spacing:0.1em;margin-bottom:4px;">SF</div>'
        + left_sf + '</div>'

        + final_html +

        '<div style="display:flex;flex-direction:column;gap:0;">'
        '<div style="font-family:Bebas Neue,sans-serif;font-size:0.7rem;color:#888;letter-spacing:0.1em;margin-bottom:4px;">SF</div>'
        + right_sf + '</div>'

        '<div style="display:flex;flex-direction:column;gap:0;">'
        '<div style="font-family:Bebas Neue,sans-serif;font-size:0.7rem;color:#888;letter-spacing:0.1em;margin-bottom:4px;">QF</div>'
        + right_qf + '</div>'

        '<div style="display:flex;flex-direction:column;gap:0;">'
        '<div style="font-family:Bebas Neue,sans-serif;font-size:0.7rem;color:#888;letter-spacing:0.1em;margin-bottom:4px;">R16</div>'
        + right_r16 + '</div>'

        '<div style="display:flex;flex-direction:column;gap:0;">'
        '<div style="font-family:Bebas Neue,sans-serif;font-size:0.7rem;color:#888;letter-spacing:0.1em;margin-bottom:4px;">R32</div>'
        + right_r32 + '</div>'

        '</div>'
    )

    st.markdown(
        '<div class="bracket-wrap">' + bracket_html + '</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="footer"> <div style="text-align:center"> <small>Created By: Garrett Walker</small></div>', unsafe_allow_html=True)

with tab4:
    st.markdown("""
    <div style="max-width:800px;padding:8px 0;">

    <div style="font-family:Bebas Neue,sans-serif;font-size:1.6rem;letter-spacing:0.1em;
    color:#f0e040;border-bottom:1px solid #1e1e2e;padding-bottom:0.4rem;margin-bottom:1.2rem;">
    HOW TO USE THIS APP</div>

    <p style="color:#aaa;font-size:0.9rem;line-height:1.7;">
    This app calculates Elo ratings for every international soccer team based on historical
    match results, then uses those ratings to simulate the 2026 World Cup bracket.
    Configure the settings in the sidebar and press <strong style="color:#f0e040;">Run Simulation</strong> to generate results.
    </p>

    <div style="font-family:Bebas Neue,sans-serif;font-size:1.1rem;letter-spacing:0.1em;
    color:#f0e040;margin:1.4rem 0 0.6rem;">DATE RANGE</div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:14px 16px;margin-bottom:8px;">
    <div style="color:#e8e4dc;font-size:0.85rem;font-weight:500;margin-bottom:4px;">Start / End Date</div>
    <div style="color:#888;font-size:0.82rem;line-height:1.6;">
    The window of matches used to build the final ratings. Only games played between these
    two dates affect the rankings you see. A wider window gives more data but may include
    results that are less relevant to current team strength. A narrower window is more
    reactive to recent form. A typical choice is 2–4 years ending near the present.
    </div></div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:14px 16px;margin-bottom:8px;">
    <div style="color:#e8e4dc;font-size:0.85rem;font-weight:500;margin-bottom:4px;">Burn-in Period</div>
    <div style="color:#888;font-size:0.82rem;line-height:1.6;">
    Every team starts at 1500 Elo before any games are processed. If ratings start cold
    at your chosen start date, early results are noisy — a weak team that wins its first
    few games looks stronger than it is. The burn-in silently processes N years of matches
    before your start date to give teams realistic starting ratings. 4–6 years is recommended.
    Longer burn-ins are more accurate but slower to run.
    </div></div>

    <div style="font-family:Bebas Neue,sans-serif;font-size:1.1rem;letter-spacing:0.1em;
    color:#f0e040;margin:1.4rem 0 0.6rem;">ELO SETTINGS</div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:14px 16px;margin-bottom:8px;">
    <div style="color:#e8e4dc;font-size:0.85rem;font-weight:500;margin-bottom:4px;">Home Advantage</div>
    <div style="color:#888;font-size:0.82rem;line-height:1.6;">
    The number of Elo points added to the home team's rating when calculating expected
    win probability. A value of 70 means the home team is treated as if they are 70 Elo
    points stronger than they actually are. This is only applied to non-neutral venue games.
    World Cup matches and most major tournaments are played at neutral venues so this has
    no effect on those. Typical values range from 50–100.
    </div></div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:14px 16px;margin-bottom:8px;">
    <div style="color:#e8e4dc;font-size:0.85rem;font-weight:500;margin-bottom:4px;">Time Decay Rate</div>
    <div style="color:#888;font-size:0.82rem;line-height:1.6;">
    Applies exponential decay to the K-factor of older matches, so recent results have
    more impact on ratings than old ones. A rate of 0.03 means a match from 2 years ago
    has roughly 94% of the weight of a match played today. Higher values make the model
    more reactive to recent form and less influenced by older results. Set to 0 to treat
    all matches equally regardless of age.
    </div></div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:14px 16px;margin-bottom:8px;">
    <div style="color:#e8e4dc;font-size:0.85rem;font-weight:500;margin-bottom:4px;">Regression Factor</div>
    <div style="color:#888;font-size:0.82rem;line-height:1.6;">
    Once per calendar year, every team's rating is pulled partway toward their
    confederation's average rating. A factor of 0.1 moves each team 10% of the way
    toward that target. This prevents strong teams from inflating indefinitely and
    weak teams from bottoming out. It also corrects for confederation strength — AFC
    and CAF teams that accumulate Elo by beating weak regional opponents get pulled
    back toward a more realistic baseline. Values between 0.05 and 0.2 are typical.
    </div></div>

    <div style="font-family:Bebas Neue,sans-serif;font-size:1.1rem;letter-spacing:0.1em;
    color:#f0e040;margin:1.4rem 0 0.6rem;">K-FACTORS</div>

    <p style="color:#aaa;font-size:0.82rem;line-height:1.7;margin-bottom:10px;">
    The K-factor controls how much a result can change a team's Elo rating. A higher K
    means a single result has a bigger impact. K is multiplied by goal difference and
    time decay before being applied, so the actual rating change also depends on the
    margin of victory and how recent the match was.
    </p>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:12px 14px;">
    <div style="color:#e8e4dc;font-size:0.83rem;font-weight:500;margin-bottom:3px;">FIFA World Cup <span style="color:#f0e040;font-size:0.75rem;margin-left:4px;">default 75</span></div>
    <div style="color:#888;font-size:0.78rem;line-height:1.5;">The highest-stakes tournament. Results here should move ratings the most.</div>
    </div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:12px 14px;">
    <div style="color:#e8e4dc;font-size:0.83rem;font-weight:500;margin-bottom:3px;">UEFA Euro / Copa America <span style="color:#f0e040;font-size:0.75rem;margin-left:4px;">default 60</span></div>
    <div style="color:#888;font-size:0.78rem;line-height:1.5;">Top continental tournaments. Slightly below the World Cup in weight.</div>
    </div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:12px 14px;">
    <div style="color:#e8e4dc;font-size:0.83rem;font-weight:500;margin-bottom:3px;">AFCON / Asian Cup / Gold Cup <span style="color:#f0e040;font-size:0.75rem;margin-left:4px;">default 30–35</span></div>
    <div style="color:#888;font-size:0.78rem;line-height:1.5;">Continental tournaments outside UEFA/CONMEBOL. Lower weight reflects weaker average competition.</div>
    </div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:12px 14px;">
    <div style="color:#e8e4dc;font-size:0.83rem;font-weight:500;margin-bottom:3px;">World Cup Qualification <span style="color:#f0e040;font-size:0.75rem;margin-left:4px;">default 35</span></div>
    <div style="color:#888;font-size:0.78rem;line-height:1.5;">Competitive matches with real stakes. Worth more than friendlies but less than the tournament itself.</div>
    </div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:12px 14px;">
    <div style="color:#e8e4dc;font-size:0.83rem;font-weight:500;margin-bottom:3px;">Nations League / Euro Qual. <span style="color:#f0e040;font-size:0.75rem;margin-left:4px;">default 25</span></div>
    <div style="color:#888;font-size:0.78rem;line-height:1.5;">Competitive but lower-stakes regional competition.</div>
    </div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:12px 14px;">
    <div style="color:#e8e4dc;font-size:0.83rem;font-weight:500;margin-bottom:3px;">Friendlies <span style="color:#f0e040;font-size:0.75rem;margin-left:4px;">default 10</span></div>
    <div style="color:#888;font-size:0.78rem;line-height:1.5;">Low stakes. Teams often rotate squads. Should have minimal impact on ratings.</div>
    </div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:12px 14px;">
    <div style="color:#e8e4dc;font-size:0.83rem;font-weight:500;margin-bottom:3px;">Other <span style="color:#f0e040;font-size:0.75rem;margin-left:4px;">default 5</span></div>
    <div style="color:#888;font-size:0.78rem;line-height:1.5;">Any tournament not matched by the above categories. Keep low to avoid unrecognised competitions distorting ratings.</div>
    </div>

    </div>
                
    <div style="font-family:Bebas Neue,sans-serif;font-size:1.1rem;letter-spacing:0.1em;
    color:#f0e040;margin:1.4rem 0 0.6rem;">MASSEY & COLLEY RATING SYSTEMS</div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:14px 16px;margin-bottom:8px;">
    <div style="color:#e8e4dc;font-size:0.85rem;font-weight:500;margin-bottom:4px;">Colley</div>
    <div style="color:#666;font-size:0.82rem;line-height:1.6;">
    A linear system that only uses wins and losses. Each team's rating is determined by
    solving a system of equations that accounts for who they beat and lost to, and how
    strong those opponents were. Score margins are completely ignored.
    </div></div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:14px 16px;margin-bottom:8px;">
    <div style="color:#e8e4dc;font-size:0.85rem;font-weight:500;margin-bottom:4px;">Massey</div>
    <div style="color:#666;font-size:0.82rem;line-height:1.6;">
    A linear system that incorporates the scores of games. A 3-0 win contributes more
    to a team's rating than a 1-0 win. Like Colley, the system solves a matrix equation
    that accounts for strength of schedule, so beating strong opponents by large margins
    is rewarded more than beating weak ones.
    </div></div>

    <div style="font-family:Bebas Neue,sans-serif;font-size:1.1rem;letter-spacing:0.1em;
    color:#f0e040;margin:1.4rem 0 0.6rem;">TIME WEIGHTING OPTIONS</div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:14px 16px;margin-bottom:8px;">
    <div style="color:#e8e4dc;font-size:0.85rem;font-weight:500;margin-bottom:4px;">Uniform Weighting</div>
    <div style="color:#666;font-size:0.82rem;line-height:1.6;">
    Each game is weighted equally regardless of the day it was played. A match from
    4 years ago counts the same as one played last week.
    </div></div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:14px 16px;margin-bottom:8px;">
    <div style="color:#e8e4dc;font-size:0.85rem;font-weight:500;margin-bottom:4px;">Linear Weighted Time</div>
    <div style="color:#666;font-size:0.82rem;line-height:1.6;">
    Games are weighted based on the day they were played. The value of games on each
    day are given by a straight line through two values you choose — the weight for
    the first day in the time period, and the weight for the most recent day. Games
    in between are interpolated along that line.
    </div>
    <div style="color:#555;font-size:0.78rem;margin-top:6px;line-height:1.5;">
    Parameters: <span style="color:#888;">Weight of oldest game</span> — value assigned to a game played on the first day
    of the time period. <span style="color:#888;">Weight of newest game</span> — value assigned to a game played today
    or on the cutoff date.
    </div></div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:14px 16px;margin-bottom:8px;">
    <div style="color:#e8e4dc;font-size:0.85rem;font-weight:500;margin-bottom:4px;">Log Weighted Time</div>
    <div style="color:#666;font-size:0.82rem;line-height:1.6;">
    Games are weighted based on the day they were played using a logarithmic curve.
    Games played today are weighted at 100%. You define the curve by specifying two
    points: how many years ago a game should be worth 95% of a game played today,
    and how many years ago a game should be worth 50%. Both values can be fractions
    of a year. The curve is steeper when these two values are close together.
    </div>
    <div style="color:#555;font-size:0.78rem;margin-top:6px;line-height:1.5;">
    Parameters: <span style="color:#888;">Years for 95% weight</span> — a game this many years old retains 95% of its
    value. <span style="color:#888;">Years for 50% weight</span> — a game this many years old retains 50% of its value.
    Must satisfy: years back &gt; years for 50% &gt; years for 95%.
    </div></div>

    <div style="font-family:Bebas Neue,sans-serif;font-size:1.1rem;letter-spacing:0.1em;
    color:#f0e040;margin:1.4rem 0 0.6rem;">TOURNAMENT TYPE WEIGHTING</div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:14px 16px;margin-bottom:8px;">
    <div style="color:#e8e4dc;font-size:0.85rem;font-weight:500;margin-bottom:4px;">Weighting by Type of Game</div>
    <div style="color:#666;font-size:0.82rem;line-height:1.6;">
    Nations play different types of international games. Each type has a different
    purpose and may be approached differently by teams — for example, Friendlies have
    no bearing on World Cup qualification so teams may not take them as seriously.
    These weights control how much impact each type of game has on the ratings.
    They are multiplied by the time weight to give each game its final weight.
    In the Colley method, for games decided by Penalty Shootout, the weight is
    additionally multiplied by the penalty shootout parameter.
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:10px;">
    <div style="background:#0a0a0f;border:1px solid #1a1a2e;border-radius:4px;padding:8px 10px;">
    <div style="color:#888;font-size:0.78rem;font-weight:500;">Friendly</div>
    <div style="color:#555;font-size:0.75rem;margin-top:2px;">Lowest stakes. Teams often rotate squads.</div>
    </div>
    <div style="background:#0a0a0f;border:1px solid #1a1a2e;border-radius:4px;padding:8px 10px;">
    <div style="color:#888;font-size:0.78rem;font-weight:500;">Continental Qualifier</div>
    <div style="color:#555;font-size:0.75rem;margin-top:2px;">Regional qualification matches.</div>
    </div>
    <div style="background:#0a0a0f;border:1px solid #1a1a2e;border-radius:4px;padding:8px 10px;">
    <div style="color:#888;font-size:0.78rem;font-weight:500;">World Cup Qualifier</div>
    <div style="color:#555;font-size:0.75rem;margin-top:2px;">High stakes — direct path to the World Cup.</div>
    </div>
    <div style="background:#0a0a0f;border:1px solid #1a1a2e;border-radius:4px;padding:8px 10px;">
    <div style="color:#888;font-size:0.78rem;font-weight:500;">Continental Final</div>
    <div style="color:#555;font-size:0.75rem;margin-top:2px;">Euro, Copa America, AFCON, Asian Cup etc.</div>
    </div>
    <div style="background:#0a0a0f;border:1px solid #1a1a2e;border-radius:4px;padding:8px 10px;">
    <div style="color:#888;font-size:0.78rem;font-weight:500;">World Cup</div>
    <div style="color:#555;font-size:0.75rem;margin-top:2px;">Highest weight. The pinnacle of international football.</div>
    </div>
    </div></div>

    <div style="font-family:Bebas Neue,sans-serif;font-size:1.1rem;letter-spacing:0.1em;
    color:#f0e040;margin:1.4rem 0 0.6rem;">READING THE RESULTS</div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:14px 16px;margin-bottom:8px;">
    <div style="color:#e8e4dc;font-size:0.85rem;font-weight:500;margin-bottom:4px;">Rankings tab</div>
    <div style="color:#888;font-size:0.82rem;line-height:1.6;">
    All teams sorted by final Elo rating. Teams appearing in the 2026 World Cup groups are
    highlighted in <span style="color:#4caf50;">green</span>. The top 10 are highlighted with a gold left border.
    Use the confederation filter in the sidebar to narrow the list.
    </div></div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:14px 16px;margin-bottom:8px;">
    <div style="color:#e8e4dc;font-size:0.85rem;font-weight:500;margin-bottom:4px;">Groups tab</div>
    <div style="color:#888;font-size:0.82rem;line-height:1.6;">
    Each group ranked by Elo. <span style="color:#f0e040;">Q</span> marks the top 2 who
    automatically advance. <span style="color:#4caf50;">3rd</span> marks a third-place team
    that qualifies as one of the best 8 third-place teams across all groups.
    </div></div>

    <div style="background:#0f0f18;border:1px solid #1e1e2e;border-radius:6px;padding:14px 16px;margin-bottom:8px;">
    <div style="color:#e8e4dc;font-size:0.85rem;font-weight:500;margin-bottom:4px;">Bracket tab</div>
    <div style="color:#888;font-size:0.82rem;line-height:1.6;">
    The full knockout bracket from Round of 32 to the Final. In every match the higher-rated
    team wins — there is no probability involved. The predicted champion is shown at the
    centre of the bracket and at the top of the page.
    </div></div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="footer"> <div style="text-align:center"> <small>Created By: Garrett Walker</small></div>', unsafe_allow_html=True)

