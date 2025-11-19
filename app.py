import streamlit as st
import pandas as pd

# local imports
from src.utils import load_yaml, calculate_week, fetch_csv
from src.utils import determine_game_winners, calculate_weekly_scores
from src.pages import matchups_and_spreads_page, standings_page, picks_page, remaining_picks_page
from src.pages import prizes_page, rules_page, breakdown_page

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
pages = ["Matchups and Spreads", "Standings", "Picks and Scores", "Breakdown", "Remaining Picks", "Prizes", "Rules"]
choice = st.sidebar.selectbox("Select Page", pages)

# CACLULATE WEEKLY SCORES
# -----------------------
week = calculate_week()
overall_scores = pd.DataFrame()
for i in range(1, week + 1):

    # load picks
    sheet_id = app_config["data"]["picks"]["sheet_id"]
    gid = app_config["data"]["picks"]["gid"][f"week{i}"]
    weekly_picks = fetch_csv(sheet_id, gid)

    # load scores
    sheet_id = app_config["data"]["games"]["sheet_id"]
    gid = app_config["data"]["games"]["gid"] 
    outcome_data = fetch_csv(sheet_id, gid)
    weekly_outcomes = outcome_data.loc[outcome_data["Week"] == int(i), :]

    # calculate game + spread winners in games
    weekly_outcomes = determine_game_winners(weekly_outcomes)

    # calculate score for week
    weekly_scores = calculate_weekly_scores(weekly_picks, weekly_outcomes, i)

    # combine
    overall_scores = pd.concat([overall_scores, weekly_scores], axis = 0)

# PAGES
# -----
if choice == "Matchups and Spreads":
    matchups_and_spreads_page(app_config)
elif choice == "Standings":
    standings_page(app_config, overall_scores)
elif choice == "Picks and Scores":
    picks_page(app_config, overall_scores)
elif choice == "Breakdown":
    breakdown_page(app_config, overall_scores)
elif choice == "Remaining Picks":
    remaining_picks_page(app_config, overall_scores)
elif choice == "Prizes":
    prizes_page(app_config)
elif choice == "Rules":
    rules_page()

st.sidebar.divider()