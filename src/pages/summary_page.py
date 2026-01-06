import pandas as pd
import streamlit as st

SURVIVOR_WEEKS = 18
ATS_PICKS_PER_WEEK = 5
score_cols = [
        "2 Point Spread Points",
        "1 Point Spread (1) Points",
        "1 Point Spread (2) Points",
        "1 Point Spread (3) Points",
        "1 Point Spread (4) Points",
    ]
pick_cols = [
        "2 Point Spread",
        "1 Point Spread (1)",
        "1 Point Spread (2)",
        "1 Point Spread (3)",
        "1 Point Spread (4)",
    ]

def summary_page(app_config: dict, overall_scores: pd.DataFrame):
    # select player
    st.header("Summary")
    players = sorted(
        overall_scores["Player"].dropna().unique().tolist(),
        key=lambda s: s.strip().lower()
    )
    selected_player = st.selectbox(
        "Player",
        options=players,
        index=0 if players else None,
        placeholder="Type to search..."
    )
    if not selected_player:
        st.info("Select a player to view stats.")
        return

    # subset to player
    df_player = overall_scores.loc[overall_scores["Player"] == selected_player].copy()

    # calculate survivor score
    survivor_hit_num = int(df_player["Survivor Point"].sum())
    survivor_hit_rate = (survivor_hit_num / SURVIVOR_WEEKS) * 100

    # biggest survivor let down
    losing_survivor_df = df_player.loc[df_player["Survivor Point"] == 0, :]
    losing_survivor_df["total_spread_points"] = losing_survivor_df[score_cols].sum(axis=1)
    max_spread = losing_survivor_df["total_spread_points"].max()
    worst_survivor_weeks = losing_survivor_df.loc[
        losing_survivor_df["total_spread_points"] == max_spread
    ]
    worst_survivor = worst_survivor_weeks["Survivor Pick"].iloc[0]
    worst_week = worst_survivor_weeks["Week"].iloc[0]

    # calculate ATS scores
    ats_score_no_survivor = float(df_player[score_cols].sum().sum())
    ats_score_survivor = float(df_player["Total Points"].sum())
    ats_success = ats_score_survivor / ats_score_no_survivor * 100

    # ATS: compute without mutating df_player
    ats_correct = float((
        (df_player["2 Point Spread Points"] / 2)
        + df_player["1 Point Spread (1) Points"]
        + df_player["1 Point Spread (2) Points"]
        + df_player["1 Point Spread (3) Points"]
        + df_player["1 Point Spread (4) Points"]
    ).sum())
    ats_hit_rate = (ats_correct / (SURVIVOR_WEEKS * ATS_PICKS_PER_WEEK)) * 100

    # calculate 2 point success
    two_point_success = df_player["2 Point Spread Points"].sum()/36 * 100
    
    # most picked teams
    s = (
        df_player[pick_cols]
        .astype("string")          # handles mixed types safely
        .apply(lambda col: col.str.strip())
        .stack(dropna=True)
    )
    empty_tokens = {"", "nan", "none", "null", "-", "—", "N/A"}
    s = s[~s.str.lower().isin(empty_tokens)]
    counts = s.value_counts()
    top = counts[counts == counts.max()]

    # --- Formatting helpers ---
    def fmt_int(x): return f"{int(x):,}"
    def fmt_num(x): return f"{x:,.1f}".rstrip("0").rstrip(".")
    def fmt_pct(x): return f"{x:.1f}%"

    # --- Tabs make it feel “designed” ---
    tab_survivor, tab_ats, tab_scoring = st.tabs(["Survivor", "ATS", "Scoring"])

    with tab_survivor:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Correct Survivor Picks", fmt_int(survivor_hit_num))
        c2.metric("Survivor Hit Rate", fmt_pct(survivor_hit_rate))
        c3.metric("Biggest Letdown", f"{worst_survivor} - Week {worst_week}")
        c4.metric("Points Missed", f"{max_spread}")

    with tab_ats:
        st.caption("This simply calculates the number and percentage of ATS picks you correctly picked this year - regardless of the survivor/scoring portion.")
        c1, c2 = st.columns([1, 1])
        c1.metric("Correct ATS Picks", fmt_int(ats_correct))
        c2.metric("Correct ATS %", fmt_pct(ats_hit_rate))

    with tab_scoring:
        st.caption("'Total Possible Points' are the number of points you would have scored if you got each survivor pick right.")
        c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])
        c1.metric("Final Score", fmt_num(ats_score_survivor))
        c2.metric("Total Possible Points", fmt_int(ats_score_no_survivor))
        c3.metric("ATS Conversion", fmt_pct(ats_success))
        c4.metric("2 Point Success", fmt_pct(two_point_success))
        c5.metric("Most Picked ATS", f"{top.index[0]} ({top.iloc[0]} times)")

    st.divider()

    sorted_cols = ["Week", "Survivor Pick", "Survivor Point",
                   "2 Point Spread", "2 Point Spread Points",
                   "1 Point Spread (1)", "1 Point Spread (1) Points",
                   "1 Point Spread (2)", "1 Point Spread (2) Points",
                   "1 Point Spread (3)", "1 Point Spread (3) Points",
                   "1 Point Spread (4)", "1 Point Spread (4) Points",
                   "Total Points"]
    display_df = df_player.loc[:, sorted_cols]
    st.dataframe(display_df)

#     # --- Leaderboard (all players) ---
#     st.subheader("Leaderboard")
#     leaderboard = _build_leaderboard(overall_scores)
    
#     st.dataframe(
#         leaderboard,
#         use_container_width=True,
#         hide_index=True,
#         column_config={
#             "Rank": st.column_config.NumberColumn("Rank", width="small"),
#             "Player": st.column_config.TextColumn("Player", width="medium"),
#             "Survivor Correct": st.column_config.NumberColumn("Survivor Correct", width="small"),
#             "Survivor Hit Rate": st.column_config.NumberColumn("Survivor Hit Rate", format="%.1f%%", width="small"),
#             "ATS Correct": st.column_config.NumberColumn("ATS Correct", format="%.1f", width="small"),
#             "ATS Hit Rate": st.column_config.NumberColumn("ATS Hit Rate", format="%.1f%%", width="small"),
#             "Final Score": st.column_config.NumberColumn("Final Score", format="%.1f", width="small"),
#         }
#     )

# def _build_leaderboard(overall_scores: pd.DataFrame) -> pd.DataFrame:
#     """Creates one row per player for display. No styling here—just aggregation."""
#     score_cols = [
#         "2 Point Spread Points",
#         "1 Point Spread (1) Points",
#         "1 Point Spread (2) Points",
#         "1 Point Spread (3) Points",
#         "1 Point Spread (4) Points",
#     ]

#     def per_player(g: pd.DataFrame) -> pd.Series:
#         survivor_correct = float(g["Survivor Point"].sum())
#         survivor_hit_rate = (survivor_correct / SURVIVOR_WEEKS) * 100

#         final_score = float(g[score_cols].sum().sum())

#         ats_correct = float((
#             (g["2 Point Spread Points"] / 2)
#             + g["1 Point Spread (1) Points"]
#             + g["1 Point Spread (2) Points"]
#             + g["1 Point Spread (3) Points"]
#             + g["1 Point Spread (4) Points"]
#         ).sum())
#         ats_hit_rate = (ats_correct / (SURVIVOR_WEEKS * ATS_PICKS_PER_WEEK)) * 100

#         return pd.Series({
#             "Player": g["Player"].iloc[0],
#             "Survivor Correct": survivor_correct,
#             "Survivor Hit Rate": survivor_hit_rate,
#             "ATS Correct": ats_correct,
#             "ATS Hit Rate": ats_hit_rate,
#             "Final Score": final_score,
#         })

#     out = overall_scores.groupby("Player", dropna=True).apply(per_player).reset_index(drop=True)
#     return out