import pandas as pd

def calculate_weekly_scores(
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