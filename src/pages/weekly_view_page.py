import streamlit as st
import pandas as pd

# local imports
from src.utils import calculate_week

def weekly_view_page(app_config: dict):
    """
    Displays weekly matchups in a clean, compact table (no scroll box).
    """
    # page title
    week = calculate_week()
    st.title(f"Matchups and Spreads - Week {week}")

    # load schedule
    sheet_id = app_config["data"]["schedule"]["sheet_id"]
    gid = app_config["data"]["schedule"]["gid"] 
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    schedule_data = pd.read_csv(csv_url)

    # subset data to week
    schedule_data = schedule_data.loc[schedule_data["Week"] == week, :]

    # subset columns
    needed_cols = ["Weekday", "Kickoff Time", "Away Team", "Home Team", "Spread"]
    schedule_data = schedule_data.loc[:, needed_cols].copy()

    # if spread data is null - add message
    schedule_data["Spread"] = schedule_data["Spread"].fillna("Spreads Not Released")

    # game time variable
    schedule_data["Kickoff Time"] = pd.to_datetime(
        schedule_data["Kickoff Time"], format="%H:%M"
    ).dt.strftime("%I:%M %p").str.lstrip("0")
    schedule_data["Game Time"] = schedule_data["Weekday"].astype(str) + " - " + schedule_data["Kickoff Time"].astype(str)

    # matchup
    schedule_data["Matchup"] = schedule_data["Away Team"].astype(str) + " @ " + schedule_data["Home Team"].astype(str)

    # subset data
    schedule_data = schedule_data.loc[:, ["Game Time", "Matchup", "Spread"]]

    # ---- Table CSS (compact, sticky header, zebra, centered time/spread) ----
    st.markdown("""
    <style>
      /* tighten padding */
      .stDataFrame [data-testid="stTable"] td, 
      .stDataFrame [data-testid="stTable"] th { padding-top: 6px; padding-bottom: 6px; }
      /* sticky header */
      .stDataFrame thead tr th { position: sticky; top: 0; z-index: 1; background: var(--background-color); }
      /* zebra rows */
      .stDataFrame tbody tr:nth-child(even) { background-color: rgba(255,255,255,0.035); }
      /* center specific columns */
      .stDataFrame td:nth-child(2),  /* Kickoff (CT) */
      .stDataFrame td:nth-child(6) { /* Spread */
          text-align: center;
          font-variant-numeric: tabular-nums;
      }
      /* mono for times for readability */
      .stDataFrame td:nth-child(2) { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
      /* round corners a bit more */
      .stDataFrame [data-testid="stTable"] { border-radius: 12px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

    # Dynamic height so all games fit (no internal scrolling)
    rows = len(schedule_data)
    row_px = 34   # row height after compact padding
    header_px = 42
    extra_px = 12
    editor_height = header_px + rows * row_px + extra_px

    # Render table
    st.data_editor(
        schedule_data,
        use_container_width=True,
        hide_index=True,
        disabled=True,  # read-only
        height=editor_height,
        column_config={
            "Game Time": st.column_config.TextColumn("Game Time", width="small", help="Game weekday"),
            "Matchup": st.column_config.TextColumn("Matchup", width="small"),
            "Spread": st.column_config.TextColumn("Spread", width="medium")
        },
    )

    st.caption("Spreads are updated around **12 PM CT on Thursdays**.")