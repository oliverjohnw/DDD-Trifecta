import streamlit as st

# local imports
from src.utils import load_yaml
from src.pages import weekly_view_page, standings_page, prizes_page, rules_page
from src.ui import inject_css

# load in script config
app_config_path = "config/app_config.yaml"
app_config = load_yaml(app_config_path)

# PAGE CONFIGS
# -------------
st.set_page_config(page_title="DDD Trifecta 2025", page_icon="🏈", layout="wide")
inject_css()

# SIDEBAR
# -------
st.sidebar.title("🏈 DDD Trifecta 2025")
st.sidebar.caption("Use the sidebar to navigate.")
pages = ["Matchups and Spreads", "Standings", "Prizes", "Rules"]
choice = st.sidebar.selectbox("Select Page", pages)
                                   
# PAGES
# -----
if choice == "Matchups and Spreads":
    weekly_view_page(app_config)
elif choice == "Standings":
    standings_page()
elif choice == "Prizes":
    prizes_page()
elif choice == "Rules":
    rules_page()

st.sidebar.divider()