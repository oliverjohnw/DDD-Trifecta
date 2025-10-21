import pandas as pd
import streamlit as st
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# local imports
from src.utils import calculate_week


def breakdown_page(app_config: dict, overall_scores: pd.DataFrame):
    """
    Breakdown of spreads and survivor picks.
    """
    _inject_css()

    # ---------- Row 1: centered header + week selector ----------
    hdr_l, hdr_mid, hdr_r = st.columns([0.1, 1.0, 0.1])

    current_week = calculate_week()
    weeks = [f"Week {i}" for i in range(1, 19)]
    with hdr_mid:
        st.title("Breakdown")
        week_choice = st.selectbox("Select Week", weeks, index=current_week - 1)
        week = int(re.search(r"\d+", week_choice).group())

    # ---------- Data load (not inside a narrow column) ----------
    ET = ZoneInfo("America/New_York")
    first_sunday = datetime(2025, 9, 7, 13, 0, 0, tzinfo=ET)  # CHANGE THIS if needed
    picks_release_date = first_sunday + timedelta(weeks=week - 1)
    current_time = datetime.now(ET)

    # gate: hide picks until kickoff
    if current_time <= picks_release_date:
        with hdr_mid:
            st.caption("Picks released at kickoff of Sunday games.")
        return

    # load weekly picks
    sheet_id = app_config["data"]["picks"]["sheet_id"]
    gid = app_config["data"]["picks"]["gid"][f"week{week}"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)

    picks_cols = [
        "Survivor Pick",
        "2 Point Spread",
        "1 Point Spread (1)",
        "1 Point Spread (2)",
        "1 Point Spread (3)",
        "1 Point Spread (4)",
    ]
    weekly_picks = (
        df.copy()
        .sort_values(by="Player", key=lambda c: c.str.strip().str.lower())
        .set_index("Player")
        .reindex(columns=picks_cols)
    )

    # prepare series for breakdowns
    survivor_series = weekly_picks["Survivor Pick"] if "Survivor Pick" in weekly_picks.columns else pd.Series(dtype=str)

    spread_cols = [
        "2 Point Spread",
        "1 Point Spread (1)",
        "1 Point Spread (2)",
        "1 Point Spread (3)",
        "1 Point Spread (4)",
    ]
    existing_spread_cols = [c for c in spread_cols if c in weekly_picks.columns]
    spread_series = weekly_picks[existing_spread_cols].stack(dropna=True) if existing_spread_cols else pd.Series(dtype=str)

    # ---------- Row 2: two wide columns for the breakdowns ----------
    col_left, col_right = st.columns([0.5, 0.5], gap="large")

    with col_left:
        st.subheader("Survivor breakdown")
        if not survivor_series.empty:
            _breakdown_table(survivor_series, "Survivor picks", chart = False, type = "Survivor")
        else:
            st.caption("No survivor picks available for this week.")

    with col_right:
        st.subheader("Spread breakdown")
        if not spread_series.empty:
            _breakdown_table(spread_series, "spread picks", chart = False, type = "Spread")
        else:
            st.caption("No spread picks available for this week.")


def _inject_css():
    st.markdown(
        """
        <style>
        .block-container {padding-top: 2rem; padding-bottom: 3rem;}
        h1 {letter-spacing: .3px;}
        div[data-baseweb="select"] {margin-bottom: .5rem;}
        .stDataFrame table {border-radius: 12px !important; border: 1px solid rgba(255,255,255,0.05);}
        .stDataFrame table th {background-color: rgba(255,255,255,0.04);}
        .stDataFrame [data-testid="stTable"] tbody tr td {padding-top: 6px !important; padding-bottom: 6px !important;}
        /* wider centered page */
        section.main > div.block-container {
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _breakdown_table(series: pd.Series, label: str, chart: bool, type: str):
    if series.empty:
        st.caption(f"No {label.lower()} available for this week.")
        return

    counts = (
        series.dropna().astype(str).str.strip().str.upper()
        .value_counts()
        .rename_axis("Team").reset_index(name="Picks")
    )
    total = counts["Picks"].sum()
    counts["%"] = (counts["Picks"] / total * 100).round(1)

    if type == "Survivor":
        height_dim = 500
    else:
        height_dim = 1800

    st.dataframe(
        counts,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Team": st.column_config.Column(width=70),
            "Picks": st.column_config.NumberColumn(format="%d", width=70),
            "%": st.column_config.NumberColumn(format="%.1f%%", width=80),
        },
        height=min(height_dim, 62 + 30 * len(counts)),
    )

    # quick bar (horizontal)
    if chart:
        try:
            import altair as alt
            chart = (
                alt.Chart(counts)
                .mark_bar()
                .encode(
                    x=alt.X("Picks:Q", title="Picks"),
                    y=alt.Y("Team:N", sort="-x", title=None),
                    tooltip=["Team", "Picks", "%"],
                )
                .properties(height=max(150, 20 * len(counts)))
            )
            st.altair_chart(chart, use_container_width=True)
        except Exception:
            st.bar_chart(data=counts.set_index("Team")["Picks"])
