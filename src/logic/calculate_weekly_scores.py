import pandas as pd
import numpy as np

def calculate_weekly_scores(app_config, week):
    """
    Calculates weekly scores and returns as dataframe.
    """
    # load picks
    sheet_id = app_config["data"]["picks"]["sheet_id"]
    gid = app_config["data"]["picks"]["gid"][f"week{week}"]
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    picks_data = pd.read_csv(csv_url)

    # load schedule
    sheet_id = app_config["data"]["schedule"]["sheet_id"]
    gid = app_config["data"]["schedule"]["gid"] 
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    schedule_data = pd.read_csv(csv_url)

    # subset schedule data
    schedule_data = schedule_data.loc[schedule_data["Week"] == week, :]
    score_data = schedule_data.loc[:, ["Away Team", "Home Team", "Home Spread", "Away Score", "Home Score"]]

    # add scoring info
    score_data["Winner"] = np.where(
        score_data["Home Score"] > score_data["Away Score"],
        schedule_data["Home Team"],
        schedule_data["Away Team"]
    )
    score_data["Spread Winner"] = np.select(
        [
            (score_data["Home Score"] + score_data["Home Spread"]) > score_data["Away Score"],
            (score_data["Home Score"] + score_data["Home Spread"]) < score_data["Away Score"]
        ],
        [
            score_data["Home Team"],
            score_data["Away Team"]
        ],
        default="PUSH"
    )

    # score submissions
    team_index = build_team_index(score_data)

    SPREAD_WEIGHTS = {
        "2 Point Spread": 2.0,
        "1 Point Spread (1)": 1.0,
        "1 Point Spread (2)": 1.0,
        "1 Point Spread (3)": 1.0,
        "1 Point Spread (4)": 1.0,
    }

    def _score_player_row(row):
        # Survivor
        surv_team = row.get("Survivor Pick")
        surv_game = team_index.get(surv_team) if pd.notna(surv_team) else None
        survivor_win = bool(surv_game is not None and surv_game["Winner"] == surv_team)
        survivor_outcome = "win" if survivor_win else ("no_game" if surv_game is None else "loss")

        # Spreads (only count if survivor won)
        spread_points = 0.0
        spread_breakdown = {}

        for col, w in SPREAD_WEIGHTS.items():
            team = row.get(col)
            if pd.isna(team) or not team:
                spread_breakdown[col + " Outcome"] = "no_pick"
                spread_breakdown[col + " Points"] = 0.0
                continue

            g = team_index.get(team)
            if g is None:
                spread_breakdown[col + " Outcome"] = "no_game"
                spread_breakdown[col + " Points"] = 0.0
                continue

            spread_winner = g["Spread Winner"]  # either a team string or "Push"
            if spread_winner == "Push":
                base = 0.5
                outcome = "push"
            elif spread_winner == team:
                base = 1.0
                outcome = "win"
            else:
                base = 0.0
                outcome = "loss"

            pts = (base * w) if survivor_win else 0.0  # survivor gate
            spread_points += pts
            spread_breakdown[col + " Outcome"] = outcome
            spread_breakdown[col + " Points"] = pts

        return pd.Series({
            "Survivor Team": surv_team,
            "Survivor Outcome": survivor_outcome,
            "Total Points": spread_points,
            **spread_breakdown
        })
    
    scored = picks_data.join(picks_data.apply(_score_player_row, axis=1))
    scored = scored.sort_values("Total Points", ascending=False)

    return scored

def build_team_index(games_df: pd.DataFrame):
    # Map each team to the single row of its game
    idx = {}
    for _, g in games_df.iterrows():
        idx[g["Home Team"]] = g
        idx[g["Away Team"]] = g
    return idx
