import streamlit as st

# local imports
from src.utils import load_yaml
from src.pages import matchups_and_spreads_page, standings_page, picks_and_scores_page, remaining_picks_page
from src.pages import prizes_page, rules_page

# load in script config
app_config_path = "config/app_config.yaml"
app_config = load_yaml(app_config_path)

# PAGE CONFIGS
# -------------
st.set_page_config(page_title="DDD Trifecta 2025", page_icon="🏈", layout="wide")

# SIDEBAR
# -------
st.sidebar.title("🏈 DDD Trifecta 2025")
st.sidebar.caption("Use the sidebar to navigate.")
pages = ["Matchups and Spreads", "Standings", "Picks and Scores", "Remaining Picks", "Prizes", "Rules"]
choice = st.sidebar.selectbox("Select Page", pages)
                                   
# PAGES
# -----
if choice == "Matchups and Spreads":
    matchups_and_spreads_page(app_config)
elif choice == "Standings":
    standings_page(app_config)
elif choice == "Picks and Scores":
    picks_and_scores_page(app_config)
elif choice == "Remaining Picks":
    remaining_picks_page(app_config)
elif choice == "Prizes":
    prizes_page(app_config)
elif choice == "Rules":
    rules_page()

st.sidebar.divider()