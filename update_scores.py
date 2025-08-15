import pandas as pd
import numpy as np

# local imports
from src.utils import load_yaml, calculate_week

def main():
    """
    Updates scores when executed.
    My vision is to run this, or schedule this to run, every Tuesday morning.
    Therefore, it should be run on the week before current week.
    """
    # determine current week
    current_week = calculate_week()
    #### TEMP CODE TO TEST
    current_week = 2
    previous_week = current_week - 1
    print(f"Calculating scores for week: {current_week - 1}")

    # load in app config
    app_config_path = "config/app_config.yaml"
    app_config = load_yaml(app_config_path)

    # load in picks
    sheet_id = app_config["data"]["picks"]["sheet_id"]
    picks_data = dict()
    for i in range(1, 17):
        gid = app_config["data"]["picks"]["gid"][f"week{i}"]
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        data = pd.read_csv(url)
        picks_data[f"Week {i}"] = data

    # load in scores
    sheet_id = app_config["data"]["games"]["sheet_id"]
    gid = app_config["data"]["games"]["gid"] 
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    scores_data = pd.read_csv(url)

    # trim anything that is NA
    scores_data = scores_data.dropna(axis = 0)

    # calculate game winner and spread winner
    scores_data["Game Winner"] = np.where(
        scores_data["Home Score"] == scores_data["Away Score"],
        "Tie",
        np.where(
            scores_data["Home Score"] > scores_data["Away Score"],
            scores_data["Home Team"],
            scores_data["Away Team"],
        ),
    )
    scores_data["Spread Winner"] = np.where(
        (scores_data["Home Score"] + scores_data["Home Spread"]) == scores_data["Away Score"],
        "Push",
        np.where(
            (scores_data["Home Score"] + scores_data["Home Spread"]) > scores_data["Away Score"],
            scores_data["Home Team"],
            scores_data["Away Team"],
        ),
    )

    # filter to previous week
    weekly_picks = picks_data[f"Week {previous_week}"]
    scores_data = scores_data.loc[scores_data["Week"] == previous_week, :]

    # determine points for survivor
    weekly_picks["Survivor Points"] = weekly_picks["Survivor Pick"].isin(scores_data["Game Winner"]).astype(int)

    # determine points for spread
    rows = []
    for _, r in scores_data.iterrows():
        home, away, sw = r["Home Team"], r["Away Team"], r["Spread Winner"]

        if isinstance(sw, str) and sw.strip().lower() == "push":
            rows.append({"Team": home, "base": 0.5})
            rows.append({"Team": away, "base": 0.5})
        else:
            # winner gets 1.0, the other team gets 0.0
            rows.append({"Team": sw, "base": 1.0})
            other = away if sw == home else home
            rows.append({"Team": other, "base": 0.0})

    team_base = pd.DataFrame(rows)
    base_map = team_base.set_index("Team")["base"]

    p = weekly_picks.copy()

    def score_col(df, col, weight):
        return df[col].map(base_map).fillna(0).mul(weight)
    
    p["2 Point Spread Points"] = score_col(p, "2 Point Spread", 2)
    p["1 Point Spread (1) Points"] = score_col(p, "1 Point Spread (1)", 1)
    p["1 Point Spread (2) Points"] = score_col(p, "1 Point Spread (2)", 1)
    p["1 Point Spread (3) Points"] = score_col(p, "1 Point Spread (3)", 1)
    p["1 Point Spread (4) Points"] = score_col(p, "1 Point Spread (4)", 1)
    p["Player"] = weekly_picks["Player"]
    p = p.loc[:, ["Player", "Survivor Points", "1 Point Spread (1) Points", "1 Point Spread (2) Points", "1 Point Spread (3) Points", "1 Point Spread (4) Points"]]

    


if __name__ == "__main__":
    main()