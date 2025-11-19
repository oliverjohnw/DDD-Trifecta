import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re
import numpy as np

# local imports
from src.utils import calculate_week


def picks_page(app_config: dict, overall_scores: pd.DataFrame):
    """
    Show weekly picks with simple correctness coloring driven by overall_scores:
      - 1 => green
      - 0 => red
    """
    _inject_css()

    left, mid, right = st.columns([0.35, 1.0, 0.35])

    # --- week selector ---
    current_week = calculate_week()
    weeks = [f"Week {i}" for i in range(1, 19)]
    with mid:
        st.title("Picks and Scores")
        week_choice = st.selectbox("Select Week", weeks, index=current_week - 1)
        week = int(re.search(r"\d+", week_choice).group())

        # --- gating (hide picks until Sunday kickoff) ---
        ET = ZoneInfo("America/New_York")
        first_sunday = datetime(2025, 9, 7, 13, 0, 0, tzinfo=ET)  # CHANGE THIS if needed
        picks_release_date = first_sunday + timedelta(weeks=week - 1)
        current_time = datetime.now(ET)

        # --- load weekly picks (Google Sheet) ---
        weekly_picks = pd.DataFrame()
        if current_time > picks_release_date:
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
        else:
            st.caption("Picks released at kickoff of Sunday games.")
            return

        # --- filter overall_scores to selected week and align to players ---
        scores_week = (
            overall_scores.loc[overall_scores["Week"] == week]
            .copy()
            .set_index("Player")
        )

        col_map = {
            "Survivor Pick": "Survivor Point",
            "2 Point Spread": "2 Point Spread Points",
            "1 Point Spread (1)": "1 Point Spread (1) Points",
            "1 Point Spread (2)": "1 Point Spread (2) Points",
            "1 Point Spread (3)": "1 Point Spread (3) Points",
            "1 Point Spread (4)": "1 Point Spread (4) Points",
        }

        # 1 for correct (>0), 0 for incorrect (<=0)
        mask = pd.DataFrame(index=weekly_picks.index, columns=weekly_picks.columns, dtype=int)
        for pick_col, score_col in col_map.items():
            if score_col in scores_week.columns:
                mask[pick_col] = (
                    scores_week[score_col]
                    .reindex(weekly_picks.index)
                    .fillna(0)
                    .gt(0)
                    .astype(int)
                )
            else:
                mask[pick_col] = 0

        # append Total Points
        if "Total Points" in scores_week.columns:
            weekly_picks["Total Points"] = (
                scores_week["Total Points"]
                .reindex(weekly_picks.index)
                .fillna(0)
                .astype(float)
            )

        # --- styling (1 -> green, 0 -> red) ---
        GREEN = "background-color: rgba(34,197,94,.28);"  # green
        RED = "background-color: rgba(239,68,68,.28);"    # red

        def apply_mask(_df: pd.DataFrame):
            m = mask.loc[_df.index, _df.columns].to_numpy()
            return pd.DataFrame(
                np.where(m == 1, GREEN, RED),
                index=_df.index,
                columns=_df.columns,
            )

        # choose columns to style
        weekly_picks = weekly_picks.loc[
            :,
            [
                "Total Points",
                "Survivor Pick",
                "2 Point Spread",
                "1 Point Spread (1)",
                "1 Point Spread (2)",
                "1 Point Spread (3)",
                "1 Point Spread (4)",
            ],
        ]
        pick_cols_only = [c for c in weekly_picks.columns if c in col_map]
        styled = weekly_picks.style.apply(apply_mask, subset=pick_cols_only, axis=None)

        # ---- NEW row: table on the left, survivor breakdown on the right ----
        # table_col, side_col = st.columns([0.72, 0.28], gap="large")

        # with table_col:
        st.caption(f"Player selections for week {week}.")
        st.dataframe(
            styled.format(na_rep=""),
            use_container_width=True,  # fills the table column only
            height=min(780, 46 + 34 * len(weekly_picks)),
            column_config={
                "Total Points": st.column_config.NumberColumn(format="%.1f", width=90),
                "Survivor Pick": st.column_config.Column(width=90),
                "2 Point Spread": st.column_config.Column(width=110),
                "1 Point Spread (1)": st.column_config.Column(width=120),
                "1 Point Spread (2)": st.column_config.Column(width=120),
                "1 Point Spread (3)": st.column_config.Column(width=120),
                "1 Point Spread (4)": st.column_config.Column(width=120),
            },
        )

    # with side_col:
    #     st.subheader("Survivor breakdown")
    #     if not weekly_picks.empty and "Survivor Pick" in weekly_picks.columns:
    #         surv_counts = (
    #             weekly_picks["Survivor Pick"]
    #             .dropna().astype(str).str.strip().str.upper()
    #             .value_counts()
    #             .rename_axis("Team").reset_index(name="Picks")
    #         )
    #         total = surv_counts["Picks"].sum()
    #         surv_counts["%"] = (surv_counts["Picks"] / total * 100).round(1)

    #         st.dataframe(
    #             surv_counts,
    #             use_container_width=True,
    #             hide_index=True,
    #             column_config={
    #                 "Team": st.column_config.Column(width=70),
    #                 "Picks": st.column_config.NumberColumn(format="%d", width=70),
    #                 "%": st.column_config.NumberColumn(format="%.1f%%", width=80),
    #             },
    #             height=min(300, 52 + 30 * len(surv_counts)),
    #         )

    #         # small chart (optional)
    #         try:
    #             import altair as alt
    #             chart = (
    #                 alt.Chart(surv_counts)
    #                 .mark_bar()
    #                 .encode(
    #                     x=alt.X("Picks:Q", title="Picks"),
    #                     y=alt.Y("Team:N", sort="-x", title=None),
    #                     tooltip=["Team", "Picks", "%"],
    #                 )
    #                 .properties(height=max(150, 20 * len(surv_counts)))
    #             )
    #             st.altair_chart(chart, use_container_width=True)
    #         except Exception:
    #             st.bar_chart(data=surv_counts.set_index("Team")["Picks"])
    #     else:
    #         st.caption("No survivor picks available for this week.")

    return

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
        /* wider and centered layout */
        section.main > div.block-container {
            max-width: 2500px;  /* wider page */
            margin-left: auto;
            margin-right: auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )