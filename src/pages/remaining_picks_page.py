import os
import glob
import pandas as pd
import streamlit as st

# local imports
from src.utils import calculate_week

NFL_TEAMS = [
    "ARI","ATL","BAL","BUF","CAR","CHI","CIN","CLE","DAL","DEN","DET","GB","HOU","IND",
    "JAX","KC","LAC","LAR","LV","MIA","MIN","NE","NO","NYG","NYJ","PHI","PIT","SEA","SF","TB","TEN","WAS"
]

# --------- small CSS for pretty "chips" ----------
CHIP_CSS = """
<style>
.badges {display:flex; flex-wrap:wrap; gap:.4rem; margin:.25rem 0 1rem 0;}
.badge {padding:.25rem .6rem; border-radius:999px; font-weight:600; font-size:.9rem;}
.badge.used {background:rgba(59,130,246,.18); color:#93c5fd; border:1px solid rgba(59,130,246,.35);}
.badge.remaining {background:rgba(34,197,94,.18); color:#86efac; border:1px solid rgba(34,197,94,.35);}
</style>
"""
# -------------------------------------------------


def remaining_picks_page(app_config: dict):
    """
    Displays Survivor: teams a player has USED and which are still AVAILABLE.
    """
    st.markdown(CHIP_CSS, unsafe_allow_html=True)

    # centered header row
    left, mid, right = st.columns([0.1, 1.0, 0.1])
    with mid:
        st.title("Remaining Picks")

    current_week = calculate_week()

    # ----- load all weekly score csvs -----
    scores_folder = app_config["output"]["weekly_scores_folder"]
    if not os.path.isdir(scores_folder):
        st.info("Survivor picks will update after Week 1.")
        return

    @st.cache_data(show_spinner=False)
    def _load_scores(folder: str) -> pd.DataFrame:
        files = sorted(glob.glob(os.path.join(folder, "week_*_scores.csv")))
        dfs = []
        for f in files:
            try:
                df = pd.read_csv(f, dtype=str).fillna("")
                dfs.append(df)
            except Exception:
                continue
        if not dfs:
            return pd.DataFrame()
        out = pd.concat(dfs, ignore_index=True)
        # normalize types/columns we need
        for c in ["Player", "Survivor Pick", "Week"]:
            if c not in out.columns:
                out[c] = ""
        # keep only necessary cols
        return out[["Player", "Survivor Pick", "Week"]]

    score_data = _load_scores(scores_folder)
    if score_data.empty:
        st.info("No score files found yet.")
        return

    # players list (case-insensitive sort)
    players = sorted(score_data["Player"].dropna().unique().tolist(), key=lambda s: s.strip().lower())

    with mid:
        selected_player = st.selectbox(
            "Select player (type to search)",
            options=players,
            index=0 if players else None,
        )

    if not selected_player:
        return

    # Filter + tidy
    df_player = (
        score_data.loc[score_data["Player"] == selected_player, ["Week", "Survivor Pick"]]
        .copy()
    )
    # Normalize abbreviations
    df_player["Survivor Pick"] = (
        df_player["Survivor Pick"]
        .astype(str).str.strip().str.upper().replace({"": None})
    )
    # Sort by week (numeric if possible)
    with pd.option_context("mode.chained_assignment", None):
        df_player["Week"] = pd.to_numeric(df_player["Week"], errors="coerce")
    df_player = df_player.sort_values("Week")

    used = [t for t in df_player["Survivor Pick"].dropna().tolist() if t]
    used_unique = []
    seen = set()
    for t in used:  # preserve first-use order
        if t not in seen:
            used_unique.append(t)
            seen.add(t)

    # Remaining = all NFL teams not yet used
    remaining = [t for t in NFL_TEAMS if t not in seen]

    # ----------- render -----------
    body_l, body_r = st.columns([0.52, 0.48], gap="large")

    with body_l:
        st.subheader(f"{selected_player} — Used teams")
        if used_unique:
            st.markdown('<div class="badges">' + "".join([f'<span class="badge used">{t}</span>' for t in used_unique]) + "</div>", unsafe_allow_html=True)
        else:
            st.info("No Survivor picks recorded yet for this player.")

        # Week-by-week table
        if not df_player.empty:
            # show most recent first, compact
            tbl = df_player.dropna(subset=["Survivor Pick"]).sort_values("Week", ascending=False)
            tbl = tbl.rename(columns={"Survivor Pick": "Team"})
            tbl = tbl.sort_values(by = "Week")
            st.dataframe(
                tbl,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Week": st.column_config.NumberColumn(format="%d", width=60, help="Week number"),
                    "Team": st.column_config.Column(width=70, help="Team abbreviation"),
                },
                height=46 + 30 * len(tbl),  # <--- Dynamic height: renders full table, no scroll
            )

    with body_r:
        st.subheader("Remaining teams")
        if remaining:
            st.markdown('<div class="badges">' + "".join([f'<span class="badge remaining">{t}</span>' for t in remaining]) + "</div>", unsafe_allow_html=True)
            st.caption(f"{len(remaining)} of {len(NFL_TEAMS)} teams available.")
        else:
            st.success("No teams remaining — you’ve used them all!")

