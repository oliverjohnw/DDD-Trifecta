from datetime import datetime, timedelta

def calculate_week():
    """
    Calculates week based on current time.
    """
    # NFL week 1 starting date
    contest_start = datetime(2025, 9, 4)

    # current time
    now = datetime.now()

    # calculate week number
    week_number = ((now - contest_start).days // 7) + 1

    # set boundaries
    if week_number < 1:
        week_number = 1
    if week_number > 18:
        week_number = 18

    return week_number