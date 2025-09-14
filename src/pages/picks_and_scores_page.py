import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# local imports
from src.utils import calculate_week

def picks_and_scores_page(app_config: dict):
    """
    Displays players picks for the selected week and their scores.
    """
    _inject_css()

    # page centering
    left, mid, right = st.columns([0.35, 0.85, 0.35])

    # determine which week
    current_week = calculate_week()
    weeks = [f"Week {i}" for i in range(1, 19)]
    with mid:
        st.title(f"Matchups and Spreads")
        week_choice = st.selectbox("Select Week", weeks, index=current_week-1)
        week = int(week_choice[-1])

    # check dates
    ET = ZoneInfo("America/New_York")
    first_sunday = datetime(2025, 9, 7, 13, 0, 0, tzinfo=ET)  # CHANGE THIS
    picks_release_date = first_sunday + timedelta(weeks=week-1)
    current_time = datetime.now(ET)

    # load picks if after kickoff
    if current_time > picks_release_date:

        # load in picks data
        sheet_id = app_config["data"]["picks"]["sheet_id"]
        gid = app_config["data"]["picks"]["gid"][f"week{week}"]
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        weekly_picks = pd.read_csv(url)

        # format
        picks_cols = ["Survivor Pick", "2 Point Spread", "1 Point Spread (1)",
                    "1 Point Spread (2)", "1 Point Spread (3)", "1 Point Spread (4)"]
        weekly_picks = (
            weekly_picks.copy()
            .sort_values(
                by="Player",
                key=lambda col: col.str.strip().str.lower()  # normalize for sorting
            )
            .set_index("Player")
            .loc[:, picks_cols]
        )
    else:
        weekly_picks = pd.DataFrame()

    # load in scores data
    try:
        weekly_scores_folder = app_config["output"]["weekly_scores_folder"]
        weekly_scores_path = Path(weekly_scores_folder) / f"week_{week}_scores.csv"
        scores = pd.read_csv(weekly_scores_path)
    except:
        scores = pd.DataFrame()

    # format if not empty
    if not scores.empty:
        score_cols = ["Total Points", "Survivor Point", "2 Point Spread Points",
                    "1 Point Spread (1) Points", "1 Point Spread (2) Points",
                    "1 Point Spread (3) Points", "1 Point Spread (4) Points"]
        score_data = (
            scores.copy()
            .sort_values(
                by="Player",
                key=lambda col: col.str.strip().str.lower()  # normalize for sorting
            )
            .set_index("Player")
            .loc[:, score_cols]
        )

    # define tabs
    tabs = st.tabs(["Picks", "Scores"])
    with tabs[0]:
        if not weekly_picks.empty:
            st.caption(f"Player selections for week {week}.")
            st.dataframe(
                weekly_picks,
                use_container_width=True,
                height=min(420, 46 + 34 * len(weekly_picks)),
                column_config={c: st.column_config.Column(width=140) for c in picks_cols},
            )
        else:
            st.caption(f"Pick released at kickoff of Sunday games.")

    with tabs[1]:
        if not scores.empty:
            st.caption(f"Scores for week {week}.")
            st.dataframe(
                score_data,
                use_container_width=True,
                height=min(480, 46 + 34 * len(score_data)),
                column_config={
                    "Total Points": st.column_config.NumberColumn(format="%d", width=110, help="Sum of all points"),
                    "Survivor Point": st.column_config.NumberColumn(format="%d", width=120),
                    "2 Point Spread Points": st.column_config.NumberColumn(format="%d", width=160),
                    "1 Point Spread (1) Points": st.column_config.NumberColumn(format="%d", width=170),
                    "1 Point Spread (2) Points": st.column_config.NumberColumn(format="%d", width=170),
                    "1 Point Spread (3) Points": st.column_config.NumberColumn(format="%d", width=170),
                    "1 Point Spread (4) Points": st.column_config.NumberColumn(format="%d", width=170),
                },
            )
        else:
            st.caption(f"Scores released Tuesday morning.")



    
    

def _inject_css():
    st.markdown(
        """
        <style>
        /* tighten vertical rhythm */
        .block-container {padding-top: 2rem; padding-bottom: 3rem;}
        /* title weight + letter-spacing */
        h1 {letter-spacing: .3px;}
        /* make widgets and tables breathe */
        div[data-baseweb="select"] {margin-bottom: .5rem;}
        /* compact dataframes + zebra rows */
        .stDataFrame [data-testid="stTable"] tbody tr td {padding-top: .35rem; padding-bottom: .35rem;}
        .stDataFrame table tbody tr:nth-child(odd) {background: rgba(255,255,255,.03);}
        /* sticky headers */
        .stDataFrame table thead th {position: sticky; top: 0; z-index: 1;}
        /* subtle rounded corners + border */
        .stDataFrame table {border-radius: 10px; overflow: hidden; border: 1px solid rgba(255,255,255,.08);}
        </style>
        """,
        unsafe_allow_html=True,
    )