"""
tools/workout/rest_day_tools.py

RestDayCheckerTool -> deterministic check of recent workout history to
flag when the user should take a rest day (consecutive high-intensity
days), instead of leaving that judgment purely to the LLM.
"""
from datetime import datetime, timezone
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel

from config.settings import settings
from database.connection import get_db
from database.collections import WORKOUTS

CONSECUTIVE_HIGH_INTENSITY_LIMIT = 3


class RestDayCheckerInput(BaseModel):
    pass


class RestDayCheckerTool(BaseTool):
    name: str = "check_rest_day_needed"
    description: str = (
        "Check the user's recent workout history to determine whether today "
        "should be a rest/active-recovery day, based on consecutive high-"
        "intensity training days."
    )
    args_schema: Type[BaseModel] = RestDayCheckerInput

    def _run(self) -> str:
        db = get_db()
        recent = list(
            db[WORKOUTS]
            .find({"user_id": settings.DEFAULT_USER_ID}, {"_id": 0})
            .sort("date", -1)
            .limit(7)
        )

        if not recent:
            return "No workout history yet — no rest day constraint applies."

        # Count consecutive most-recent days (by calendar date) that were high intensity
        consecutive_high = 0
        seen_dates = set()
        for entry in recent:
            date_val = entry.get("date")
            if isinstance(date_val, datetime):
                date_key = date_val.astimezone(timezone.utc).strftime("%Y-%m-%d")
            else:
                date_key = str(date_val)

            if date_key in seen_dates:
                continue
            seen_dates.add(date_key)

            if entry.get("intensity") == "high":
                consecutive_high += 1
            else:
                break

        if consecutive_high >= CONSECUTIVE_HIGH_INTENSITY_LIMIT:
            return (
                f"REST DAY RECOMMENDED: {consecutive_high} consecutive high-intensity "
                f"training days detected. Suggest active recovery or full rest."
            )
        return (
            f"No rest day required. {consecutive_high} consecutive high-intensity "
            f"day(s) detected (limit is {CONSECUTIVE_HIGH_INTENSITY_LIMIT})."
        )