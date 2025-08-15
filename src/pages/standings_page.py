import streamlit as st
import pandas as pd
import numpy as np

# =========================
# Sample data (replace later)
# =========================
np.random.seed(42)

PLAYERS = ["Mr_Tuxedo", "Edub1321", "OtherDDDMember", "JordanLoveMVP", "DataDawg"]
WEEKS = list(range(1, 19))
SAMPLE_POINTS = [0.0, 0.5, 1.0, 2.0]

_records = [{"Player": p, "Week": w, "Total Points": np.random.choice(SAMPLE_POINTS)}
            for p in PLAYERS for w in WEEKS]
SCORES_LONG = pd.DataFrame(_records)


# =========================
# Compute helpers
# =========================
def compute_overall(weekly_long: pd.DataFrame) -> pd.DataFrame:
    df = (weekly_long.groupby("Player", as_index=False)["Total Points"]
          .sum()
          .rename(columns={"Total Points": "Season Points"})
          .sort_values("Season Points", ascending=False))
    df["Rank"] = df["Season Points"].rank(method="dense", ascending=False).astype(int)
    df = df[["Rank", "Player", "Season Points"]].sort_values(["Rank", "Player"])
    return df

def compute_window(weekly_long: pd.DataFrame, start_wk: int, end_wk: int, label: str) -> pd.DataFrame:
    m = (weekly_long["Week"].between(start_wk, end_wk))
    df = (weekly_long.loc[m].groupby("Player", as_index=False)["Total Points"].sum()
          .rename(columns={"Total Points": label})
          .sort_values(label, ascending=False))
    df["Rank"] = df[label].rank(method="dense", ascending=False).astype(int)
    return df[["Rank", "Player", label]].sort_values(["Rank", "Player"])

def pivot_weekly(weekly_long: pd.DataFrame) -> pd.DataFrame:
    p = (weekly_long.pivot_table(index="Player", columns="Week",
                                 values="Total Points", aggfunc="sum", fill_value=0.0)
         .reindex(sorted(WEEKS), axis=1)
         .reset_index())
    p.columns = ["Player"] + [f"W{w}" for w in WEEKS]
    return p


# =========================
# HTML/CSS render helpers
# =========================
def _rank_badge(val: int) -> str:
    return f"<span class='badge badge-rank'>#{int(val)}</span>"

def _fmt_pts(val: float) -> str:
    return f"{val:.1f}"

def _style_table(df: pd.DataFrame, *, numeric_cols: list[str], table_class: str) -> str:
    """Return safe HTML for a styled table. Uses HTML badges for Rank."""
    # Convert numeric-cols to strings while preserving alignment via CSS
    render = df.copy()

    # Rank -> badge HTML
    if "Rank" in render.columns:
        render["Rank"] = render["Rank"].map(_rank_badge)

    # Format numeric columns (e.g., Season Points, W1-6 Points, etc.)
    for c in numeric_cols:
        if c in render.columns:
            render[c] = render[c].astype(float).map(_fmt_pts)

    # Build a Styler to handle basic spacing/headers and to avoid escaping our HTML badges
    sty = (render.style
           .hide(axis="index")
           .set_table_styles([
               {"selector": "th", "props": [("text-align", "left"), ("font-weight", "700"), ("padding", "8px 10px")]},
               {"selector": "td", "props": [("padding", "8px 10px"), ("vertical-align", "middle")]}
           ]))

    # IMPORTANT: escape=False to keep our badge <span> intact
    html = sty.to_html(escape=False)

    # Wrap in our class for CSS targeting
    return f"<div class='{table_class}'>{html}</div>"

def _inject_css():
    st.markdown("""
    <style>
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


# =========================
# Page (HTML/CSS rendering)
# =========================
def standings_page(_: dict | None = None):
    """
    Standings page.
    """
    # page centering
    left, mid, right = st.columns([0.35, 0.9, 0.35])
    _inject_css()

    overall = compute_overall(SCORES_LONG)
    w1_6   = compute_window(SCORES_LONG, 1, 6,  "W1-6 Points")
    w7_12  = compute_window(SCORES_LONG, 7, 12, "W7-12 Points")
    w13_18 = compute_window(SCORES_LONG, 13, 18, "W13-18 Points")
    weekly = pivot_weekly(SCORES_LONG)

    with mid:
        st.title("Standings")

        tab1, tab2, tab3, tab4 = st.tabs(
            ["Overall", "Weeks 1-6", "Weeks 7-12", "Weeks 13-18"]
        )

        with tab1:
            html = _style_table(overall, numeric_cols=["Season Points"], table_class="standings")
            st.markdown(html, unsafe_allow_html=True)

        with tab2:
            html = _style_table(w1_6, numeric_cols=["W1-6 Points"], table_class="standings")
            st.markdown(html, unsafe_allow_html=True)

        with tab3:
            html = _style_table(w7_12, numeric_cols=["W7-12 Points"], table_class="standings")
            st.markdown(html, unsafe_allow_html=True)

        with tab4:
            html = _style_table(w13_18, numeric_cols=["W13-18 Points"], table_class="standings")
            st.markdown(html, unsafe_allow_html=True)