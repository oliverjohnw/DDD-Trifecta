import streamlit as st
import os
import pandas as pd

# local imports
from src.utils import calculate_week

def remaining_picks_page(app_config: dict):
    """
    Displays remaining picks for each player.
    """
    # page centering
    left, mid, right = st.columns([0.35, 0.85, 0.35])

    # determine which week
    current_week = calculate_week()

    # read weekly scores files
    scores_folder = app_config["output"]["weekly_scores_folder"]

    if os.path.isdir(scores_folder):
        csv_files = [f for f in os.listdir(scores_folder) if f.endswith(".csv")]
        score_data = pd.DataFrame()
        for file in csv_files:
            week_score_data = pd.read_csv(f"{scores_folder}/{file}")
            score_data = pd.concat([score_data, week_score_data], axis = 0)

        with mid:
            st.title("Remaining Picks")

            # clean up & gather player list
            if "Player" not in score_data or "Survivor Pick" not in score_data:
                st.error("Expected columns 'Player' and 'Survivor Pick' not found.")
                return

            players = sorted(
                score_data["Player"].dropna().unique().tolist(),
                key=str.lower
            )
            selected_player = st.selectbox("Select player. (You can type in usernames).", players, index=0)

            # all picks for that player (skip None/blank), keep first occurrence order
            picks_series = (
                score_data.loc[score_data["Player"] == selected_player, "Survivor Pick"]
                .astype(str)
                .str.strip()
            )

        # unique while preserving order
        picks_unique = sorted(picks_series.drop_duplicates().tolist())

        with mid:
            st.subheader(f"{selected_player}'s Used Survivor Teams")
            if picks_unique:
                for pick in picks_unique:
                    st.write(f" - {pick}")
                #    st.write(", ".join(picks_unique))
            else:
                st.info("No Survivor picks recorded yet for this player.")
    else:
        st.info("Survivor picks will update after week 1.")
