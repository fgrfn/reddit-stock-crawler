# crawler_modules/utils.py
from croniter import croniter
from datetime import datetime

def next_run_time(cron_expr: str) -> datetime:
    now = datetime.now()
    itr = croniter(cron_expr, now)
    return itr.get_next(datetime)
