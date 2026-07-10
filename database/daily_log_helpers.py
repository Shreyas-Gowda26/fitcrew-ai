"""
Small shared helper: daily_logs uses one document per user per calendar day
(keyed by "date_str"), so LogWorkoutTool / LogMealTool / (later) sleep &
water tools can all tick off fields on the same day's document instead of
creating scattered separate records.
"""
from datetime import datetime, timezone

from database.connection import get_db
from database.collections import DAILY_LOGS


def today_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def upsert_daily_log(user_id: str, date_str: str | None = None, **fields):
    """
    Merge `fields` into today's (or a given date's) daily_logs doc for user_id.
    Uses $set for plain fields and $inc for anything passed under `increments`.
    """
    date_str = date_str or today_str()
    db = get_db()

    increments = fields.pop("increments", None)
    update = {"$set": {**fields, "user_id": user_id, "date": date_str}}
    if increments:
        update["$inc"] = increments

    db[DAILY_LOGS].update_one(
        {"user_id": user_id, "date": date_str},
        update,
        upsert=True,
    )


def get_daily_log(user_id: str, date_str: str | None = None) -> dict | None:
    date_str = date_str or today_str()
    db = get_db()
    return db[DAILY_LOGS].find_one(
        {"user_id": user_id, "date": date_str}, {"_id": 0}
    )