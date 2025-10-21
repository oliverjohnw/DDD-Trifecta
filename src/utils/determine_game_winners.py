import pandas as pd
import numpy as np

def determine_game_winners(
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