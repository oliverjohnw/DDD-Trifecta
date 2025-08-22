import argparse
import pandas as pd
import numpy as np
from pathlib import Path

# local imports
from src.utils import load_yaml, calculate_week

# GLOBAL VARIABLES
app_config_path = "config/app_config.yaml"
app_config = load_yaml(app_config_path)

def parse_args() -> argparse.Namespace:
    """Function to parse command line arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument('--week', type=str, help='Week to calculate scores for')
    args = parser.parse_args()

    return args

def main():
    """
    Script that will calculate scores for a week that is specified by the user.
    Script will error out if:
        * Weekly scores have already been calculated.
        * The selected week has not occured yet.
    """
    # script arguments
    args = parse_args()

    # determine current week
    current_week = calculate_week()

    # # throw error if user-selected week is greater than or equal to current week
    # if int(args.week) >= current_week:
    #     raise RuntimeError("Error: Games for this week have not finished yet.")
    
    # determine save path
    output_folder = app_config["output"]["weekly_scores_folder"]
    output_path = Path(output_folder) / f"week_{args.week}_scores.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # throw error if file exists
    if output_path.exists():
        raise FileExistsError(f"File already exists: {output_path}")
    
    # load in picks for the week
    sheet_id = app_config["data"]["picks"]["sheet_id"]
    gid = app_config["data"]["picks"]["gid"][f"week{args.week}"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    weekly_picks = pd.read_csv(url)

    # load in scores for week
    sheet_id = app_config["data"]["games"]["sheet_id"]
    gid = app_config["data"]["games"]["gid"] 
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    outcome_data = pd.read_csv(url)
    weekly_outcomes = outcome_data.loc[outcome_data["Week"] == int(args.week), :]

    # calculate game + spread winners in games
    weekly_outcomes = _determine_game_winners(weekly_outcomes)
    
    # calculate score for week
    weekly_scores = _calculate_weekly_scores(weekly_picks, weekly_outcomes, args.week)

    # save data
    weekly_scores.to_csv(output_path, index = False)

    return

def _calculate_weekly_scores(
    weekly_picks: pd.DataFrame,
    weekly_outcomes: pd.DataFrame,
    week: str
):
    """
    Calculates weekly score given the picks and outcomes of each game.
    """
    # determine points for survivor
    weekly_picks["Survivor Point"] = weekly_picks["Survivor Pick"].isin(weekly_outcomes["Game Winner"]).astype(int)

    # determine points for spread
    rows = []
    for _, r in weekly_outcomes.iterrows():
        home_team, away_team, spread_winner = r["Home Team"], r["Away Team"], r["Spread Winner"]

        # pushes are worth 0.5x for both teams
        if isinstance(spread_winner, str) and spread_winner.strip().lower() == "push":
            rows.append({"Team": home_team, "base": 0.5})
            rows.append({"Team": away_team, "base": 0.5})
        else:
            # winner gets 1.0, the other team gets 0.0
            rows.append({"Team": spread_winner, "base": 1.0})
            spread_loser = away_team if spread_winner == home_team else home_team
            rows.append({"Team": spread_loser, "base": 0.0})

    # map into dataframe
    team_base = pd.DataFrame(rows)
    base_map = team_base.set_index("Team")["base"]

    # copy dataframe
    points_data = weekly_picks.copy()

    # applies mapping from above with custom scale
    def score_col(df, col, weight):
        return df[col].map(base_map).fillna(0).mul(weight)
    
    # calculate 2 point spread (worth two points)
    points_data["2 Point Spread Points"] = score_col(points_data, "2 Point Spread", 2)

    # calculate 1 point spread (worth one point)
    points_data["1 Point Spread (1) Points"] = score_col(points_data, "1 Point Spread (1)", 1)
    points_data["1 Point Spread (2) Points"] = score_col(points_data, "1 Point Spread (2)", 1)
    points_data["1 Point Spread (3) Points"] = score_col(points_data, "1 Point Spread (3)", 1)
    points_data["1 Point Spread (4) Points"] = score_col(points_data, "1 Point Spread (4)", 1)

    # total points
    points_data["Total Points"] = points_data["Survivor Point"] * (
        points_data["2 Point Spread Points"] + 
        points_data["1 Point Spread (1) Points"] + 
        points_data["1 Point Spread (2) Points"] +
        points_data["1 Point Spread (3) Points"] +
        points_data["1 Point Spread (4) Points"]
        ) 
    
    # add special prize calculation
    spread_cols = [
        "2 Point Spread Points",
        "1 Point Spread (1) Points",
        "1 Point Spread (2) Points",
        "1 Point Spread (3) Points",
        "1 Point Spread (4) Points",
    ]
    points_data["Special"] = (
        (points_data["Survivor Point"].eq(0)) &
        (points_data[spread_cols].sum(axis=1).eq(6))
    ).astype(int)

    # add week
    points_data["Week"] = week

    return points_data

def _determine_game_winners(
    weekly_outcomes: pd.DataFrame
):
    """
    For each game in the dataframe, this function will determine
    which team won, and which team covered the spread.

    The following columns are added:
        * Game Winner
        * Spread Winner
    
    NOTE: Ties and pushes are included.
    """
    # calculate game winner
    # NOTE: Ties are included.
    weekly_outcomes["Game Winner"] = np.where(
        weekly_outcomes["Home Score"] == weekly_outcomes["Away Score"],
        "Tie",
        np.where(
            weekly_outcomes["Home Score"] > weekly_outcomes["Away Score"],
            weekly_outcomes["Home Team"],
            weekly_outcomes["Away Team"],
        ),
    )
    # calculate spread winner
    # NOTE: Pushes are included
    weekly_outcomes["Spread Winner"] = np.where(
        (weekly_outcomes["Home Score"] + weekly_outcomes["Home Spread"]) == weekly_outcomes["Away Score"],
        "Push",
        np.where(
            (weekly_outcomes["Home Score"] + weekly_outcomes["Home Spread"]) > weekly_outcomes["Away Score"],
            weekly_outcomes["Home Team"],
            weekly_outcomes["Away Team"],
        ),
    )

    return weekly_outcomes


if __name__ == "__main__":
    main()