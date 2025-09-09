import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

def standings_page(app_config: dict):
    """
    Displays standings.
    
    Standings are broken into the following subsections:
        * Overall
        * Weeks 1-6
        * Weeks 7-12
        * Weeks 13-18
        
    And there is a special tab for the Special Prize.
    """
    # styling
    _inject_css()

    # load players
    sheet_id = app_config["data"]["picks"]["sheet_id"]
    gid = app_config["data"]["picks"]["gid"][f"player_pool"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    player_pool = pd.read_csv(url)
    players = player_pool["Players"]

    # player scores path
    weekly_scores_folder = Path(app_config["output"]["weekly_scores_folder"])

    # overall scores
    overall_scores = pd.DataFrame()

    # load scores
    for week in range(1,19):

        # attempt to load scores
        try:
            score_data = pd.read_csv(weekly_scores_folder / f"week_{week}_scores.csv")
            score_data = score_data.loc[:, ["Player", "Week", "Total Points", "Special"]]

        # if scores haven't happened yet, make blank dataset with 0's
        except:
            score_data = pd.DataFrame({"Player": players, "Week": week, "Total Points": 0, "Special": 0})

        # combine to overall scores
        overall_scores = pd.concat([overall_scores, score_data], axis = 0)

    # calculate points
    overall_points = _calculate_points(overall_scores, "all")
    first_period_points = _calculate_points(overall_scores, "first")
    second_period_points = _calculate_points(overall_scores, "second")
    third_period_points = _calculate_points(overall_scores, "third")

    # calculate special prize winners
    special_prize_winners = _calculate_special(overall_scores)

    # formatting
    left, mid, right = st.columns([0.35, 0.9, 0.35])
    with mid:
        st.title("Standings")
        
        # define tabs
        overall, period_one, period_two, period_three, special_prize = st.tabs(
            ["Overall", "Weeks 1-6", "Weeks 7-12", "Weeks 13-18", "Special Prize"]
        )

        # display
        with overall:
            html = _style_table(overall_points, numeric_cols=["Overall"], table_class="standings")
            st.markdown(html, unsafe_allow_html=True)

        with period_one:
            html = _style_table(first_period_points, numeric_cols=["Weeks 1-6"], table_class="standings")
            st.markdown(html, unsafe_allow_html=True)

        with period_two:
            html = _style_table(second_period_points, numeric_cols=["Weeks 7-12"], table_class="standings")
            st.markdown(html, unsafe_allow_html=True)

        with period_three:
            html = _style_table(third_period_points, numeric_cols=["Weeks 13-18"], table_class="standings")
            st.markdown(html, unsafe_allow_html=True)

        with special_prize:
            if not special_prize_winners:
                st.header("No winners yet!")
            else:
                st.header(f"Special prize winners:")
                for winner in special_prize_winners:
                    st.write(f" - {winner}")

    return


def _calculate_special(overall_scores: pd.DataFrame):
    """
    Displays all players who score a 6 on the spread picks and a 0 for survivor.
    """
    # filter 
    special_winners = overall_scores.loc[overall_scores["Special"] == 1, "Player"]
    
    # unique winners
    unique_winners = set(special_winners)

    return unique_winners



def _calculate_points(
    overall_scores: pd.DataFrame,
    term: str
):
    """
    Filters data by term, then calculates scores.
    """
    # make data copy
    temp_scores = overall_scores.copy()

    # define time period
    if term == "all":
        start_week = 1
        end_week = 18
        label = "Overall"
    elif term == "first":
        start_week = 1
        end_week = 6
        label = "Weeks 1-6"
    elif term == "second":
        start_week = 7
        end_week = 12
        label = "Weeks 7-12"
    elif term == "third":
        start_week = 13
        end_week = 18
        label = "Weeks 13-18"

    # filter dates
    temp_scores = temp_scores.loc[
        (temp_scores["Week"] >= start_week) & (temp_scores["Week"] <= end_week),
        :
        ]
    
    # coerce for pushes
    temp_scores["Total Points"] = pd.to_numeric(temp_scores["Total Points"], errors="coerce").fillna(0.0)
    
    # calculate scores
    scores = (
        temp_scores.groupby("Player", as_index=False)["Total Points"]
        .sum()
        .rename(columns={"Total Points": label})
        .sort_values(label, ascending=False)
    )

    # # add rank
    # scores["Rank"] = scores[label].rank(method="dense", ascending=False).astype(int)
    # scores = scores[["Rank", "Player", label]].sort_values(["Rank", "Player"])

    # sort first by score (descending), then player (alphabetical)
    scores = scores.sort_values(
        [label, "Player"],
        ascending=[False, True],
        key=lambda col: col.str.lower() if col.name == "Player" else col
    )

    # assign rank with ties handled
    scores["Rank"] = (
        scores[label]
        .rank(method="min", ascending=False)  # "min" ensures ties share the same rank
        .astype(int)
    )

    # reorder columns
    scores = scores[["Rank", "Player", label]]

    return scores

def _inject_css():
    st.markdown("""
    <style>
    /* Default badge */
    .badge-rank {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 15px;
        line-height: 1.1;
        white-space: nowrap;
        background: rgba(0, 200, 255, 0.18);
        border: 1px solid rgba(0, 200, 255, 0.35);
    }

    /* Rank-specific styles */
    .badge-rank.gold {
        background: gold;
        border: 1px solid goldenrod;
        color: black;
        font-weight: 700;
    }
    .badge-rank.silver {
        background: silver;
        border: 1px solid gray;
        color: black;
        font-weight: 700;
    }
    .badge-rank.bronze {
        background: peru;
        border: 1px solid saddlebrown;
        color: white;
        font-weight: 700;
    }
                


    /* Generic table shell */
    .standings table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0 8px;     /* row gaps */
        table-layout: fixed;
    }
    .standings th {
        text-align: left;
        font-size: 18px;
        font-weight: 700;
        opacity: 0.95;
        padding: 8px 10px;
        white-space: nowrap;
    }
    .standings td {
        padding: 8px 10px;
        vertical-align: middle;
        font-size: 16px;
        white-space: nowrap;
    }

    /* card-like rows */
    .standings tbody tr td {
        background: rgba(255,255,255,0.03);
        border-top: 1px solid rgba(255,255,255,0.08);
        border-bottom: 1px solid rgba(255,255,255,0.08);
    }
    .standings tbody tr td:first-child {
        border-left: 1px solid rgba(255,255,255,0.08);
        border-top-left-radius: 12px;
        border-bottom-left-radius: 12px;
    }
    .standings tbody tr td:last-child {
        border-right: 1px solid rgba(255,255,255,0.08);
        border-top-right-radius: 12px;
        border-bottom-right-radius: 12px;
    }

    /* zebra + hover */
    .standings tbody tr:nth-child(odd) td { background: rgba(255,255,255,0.05); }
    .standings tbody tr:hover td {
        background: rgba(255,255,255,0.08);
        transform: translateY(-1px);
        transition: background 120ms ease, transform 120ms ease;
    }

    /* Alignments */
    .standings td:nth-child(1) { width: 12%; }   /* Rank */
    .standings td:nth-child(2) { width: 38%; }   /* Player */
    /* Remaining numeric columns share the rest. */

    /* Badges */
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 15px;
        line-height: 1.1;
        white-space: nowrap;
    }
    .badge-rank {
        background: rgba(0, 200, 255, 0.18);
        border: 1px solid rgba(0, 200, 255, 0.35);
    }

    /* Week-by-week scroll container */
    .scroll-x {
        overflow-x: auto;
        padding-bottom: 4px;
    }
    .scroll-x .standings table { min-width: 900px; } /* give it some width to scroll */

    /* Slightly larger first column for readability on narrow screens */
    @media (max-width: 900px) {
        .standings td:nth-child(1) { width: 18%; }
        .standings td:nth-child(2) { width: 42%; }
    }
    </style>
    """, unsafe_allow_html=True)

def _rank_badge(val: int) -> str:
    if val == 1:
        cls = "badge-rank gold"
    elif val == 2:
        cls = "badge-rank silver"
    elif val == 3:
        cls = "badge-rank silver"
    elif val == 4:
        cls = "badge-rank silver"
    elif val == 5:
        cls = "badge-rank silver"
    elif val == 6:
        cls = "badge-rank bronze"
    elif val == 7:
        cls = "badge-rank bronze"
    elif val == 8:
        cls = "badge-rank bronze"
    elif val == 9:
        cls = "badge-rank bronze"
    elif val == 10:
        cls = "badge-rank bronze"
    else:
        cls = "badge-rank"
    return f"<span class='{cls}'>#{int(val)}</span>"

def _fmt_pts(val: float) -> str:
    return f"{val:.1f}"

def _style_table(df: pd.DataFrame, *, numeric_cols: list[str], table_class: str) -> str:
    """
    Return safe HTML for a styled table (works with your CSS).
    Renders Rank as a badge and formats numeric columns to 1 decimal.
    """
    render = df.copy()

    if "Rank" in render.columns:
        render["Rank"] = render["Rank"].map(_rank_badge)

    for c in numeric_cols:
        if c in render.columns:
            render[c] = render[c].astype(float).map(_fmt_pts)

    sty = (render.style
           .hide(axis="index")
           .set_table_styles([
               {"selector": "th", "props": [("text-align", "left"), ("font-weight", "700"), ("padding", "8px 10px")]},
               {"selector": "td", "props": [("padding", "8px 10px"), ("vertical-align", "middle")]}
           ]))

    html = sty.to_html(escape=False)
    return f"<div class='{table_class}'>{html}</div>"