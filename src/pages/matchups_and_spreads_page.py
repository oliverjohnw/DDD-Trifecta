import streamlit as st
import pandas as pd
import numpy as np
import re

# local imports
from src.utils import calculate_week, load_yaml

def matchups_and_spreads_page(app_config: dict):
    """
    Displays weekly matchups in a clean, compact table (no scroll box).
    """
    # page centering
    left, mid, right = st.columns([0.35, 0.85, 0.35])

    # determine which week
    current_week = calculate_week()
    weeks = [f"Week {i}" for i in range(1, 19)]

    with mid:
        st.title(f"Matchups and Spreads")
        week_choice = st.selectbox("Select Week", weeks, index=8)
        week = int(re.search(r"\d+", week_choice).group())

    # load schedule
    sheet_id = app_config["data"]["games"]["sheet_id"]
    gid = app_config["data"]["games"]["gid"] 
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    schedule_data = pd.read_csv(csv_url)

    # subset data
    schedule_data = schedule_data.loc[schedule_data["Week"] == week, :]
    needed_cols = ["Weekday", "Kickoff Time", "Away Team", "Home Team", "Home Spread"]
    schedule_data = schedule_data.loc[:, needed_cols].copy()

    # format spread data
    sp = pd.to_numeric(schedule_data["Home Spread"], errors="coerce")
    schedule_data["Spread"] = np.where(
        sp.isna(),
        "Spreads Not Released",
        np.where(
            sp < 0,
            schedule_data["Away Team"] + " +" + (-sp).round(1).astype(str) + " | " + schedule_data["Home Team"] + " " + sp.round(1).astype(str),
            schedule_data["Away Team"] + " " + (-sp).round(1).astype(str) + " | " + schedule_data["Home Team"] + " +" + sp.round(1).astype(str),
        ),
    )

    # game time variable
    schedule_data["Kickoff Time"] = pd.to_datetime(
        schedule_data["Kickoff Time"], format="%H:%M"
    ).dt.strftime("%I:%M %p").str.lstrip("0")
    schedule_data["Game Time"] = schedule_data["Weekday"].astype(str) + " - " + schedule_data["Kickoff Time"].astype(str)

    # map logos
    team_logos = load_yaml(app_config["config"]["logos"])
    schedule_data["Away Logo"] = schedule_data["Away Team"].map(team_logos)
    schedule_data["Home Logo"] = schedule_data["Home Team"].map(team_logos)

    def img(url, height=140):
        if pd.isna(url) or not url:
            return ""
        return f"<img src='{url}' style='height:{height}px;'>"
    
    display_df = schedule_data.loc[:, ["Game Time", "Away Logo", "Home Logo", "Spread"]].copy()
    display_df["Away"] = display_df["Away Logo"].map(lambda u: img(u, height=40))
    display_df["Home"] = display_df["Home Logo"].map(lambda u: img(u, height=40))
    display_df = display_df.drop(columns=["Away Logo", "Home Logo"])
    display_df = display_df[["Game Time", "Away", "Home", "Spread"]]

    # badge-ify spread column
    def spread_badge(s):
        if s == "Spreads Not Released":
            return "<span class='badge badge-muted'>Spreads Not Released</span>"
        return f"<span class='badge'>{s}</span>"

    display_df["Spread"] = display_df["Spread"].map(spread_badge)

    # CSS that makes it feel like a UI component (rounded, zebra, hover)
    st.markdown(
        """
        <style>
        .matchups table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0 8px;   /* row gaps */
            table-layout: fixed;      /* <-- lets our column widths apply */
        }

        /* Bigger, bold headers */
        .matchups th {
            text-align: left;
            font-size: 18px;
            font-weight: 700;
            opacity: 0.95;
            padding: 8px 10px;
        }

        .matchups td {
            padding: 8px 10px;
            vertical-align: middle;
            font-size: 16px;
            white-space: nowrap;      /* keep single-line cells */
        }

        /* ----- Column widths (trim deadspace) ----- */
        /* 1: Game Time, 2: Away, 3: Home, 4: Spread */
        .matchups th:nth-child(1), .matchups td:nth-child(1) { width: 30%; }
        .matchups th:nth-child(2), .matchups td:nth-child(2) { width: 20%; }
        .matchups th:nth-child(3), .matchups td:nth-child(3) { width: 20%; }
        .matchups th:nth-child(4), .matchups td:nth-child(4) { width: 18%; }  /* narrower Spread */

        /* Slightly tighter padding on first/last columns */
        .matchups th:first-child, .matchups th:last-child,
        .matchups td:first-child, .matchups td:last-child {
            padding-left: 6px !important;
            padding-right: 6px !important;
        }

        /* card-like rows */
        .matchups tbody tr td {
            background: rgba(255,255,255,0.03);
            border-top: 1px solid rgba(255,255,255,0.08);
            border-bottom: 1px solid rgba(255,255,255,0.08);
        }
        .matchups tbody tr td:first-child {
            border-left: 1px solid rgba(255,255,255,0.08);
            border-top-left-radius: 12px;
            border-bottom-left-radius: 12px;
        }
        .matchups tbody tr td:last-child {
            border-right: 1px solid rgba(255,255,255,0.08);
            border-top-right-radius: 12px;
            border-bottom-right-radius: 12px;
        }

        /* zebra + hover */
        .matchups tbody tr:nth-child(odd) td { background: rgba(255,255,255,0.05); }
        .matchups tbody tr:hover td {
            background: rgba(255,255,255,0.08);
            transform: translateY(-1px);
            transition: background 120ms ease, transform 120ms ease;
        }

        /* center logos */
        .matchups td:nth-child(2), .matchups td:nth-child(3) { text-align: center; }

        /* Slightly larger Game Time for readability */
        .matchups td:first-child { font-size: 18px; }

        /* Spread badge */
        .badge {
            display: inline-block;
            padding: 2px 8px;         /* tighter badge padding */
            border-radius: 9999px;
            background: rgba(0, 200, 255, 0.18);
            border: 1px solid rgba(0, 200, 255, 0.35);
            font-size: 15px;
            line-height: 1.1;
            white-space: nowrap;
        }
        .badge-muted {
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.20);
            opacity: 0.9;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


    # style with pandas (just to hide index)
    styled = (
        display_df.style
            .hide(axis="index")
            .set_table_styles([{"selector": "th", "props": [("padding", "6px 12px")]}])
    )

    with mid:
        st.caption("Note: All times are in Eastern Time.")
        st.markdown(f"<div class='matchups'>{styled.to_html()}</div>", unsafe_allow_html=True)
        st.caption("Spreads are updated around **1:30 PM Eastern Time on Thursdays**.")
