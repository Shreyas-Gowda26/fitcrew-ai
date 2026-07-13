"""
tools/progress/weight_trend_tools.py

WeightTrendTool -> reads the user's weight history from the `progress`
collection (populated by save_progress) and reports direction, rate of
change, and whether it looks like a plateau.
"""
from datetime import datetime, timezone
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from config.settings import settings
from database.connection import get_db
from database.collections import PROGRESS

PLATEAU_THRESHOLD_KG = 0.3  # total swing below this over the window counts as a plateau


class WeightTrendInput(BaseModel):
    days: int = Field(30, description="How many days back to look (default 30)")


class WeightTrendTool(BaseTool):
    name: str = "get_weight_trend"
    description: str = (
        "Analyze the user's logged weight history (from save_progress entries) over "
        "the given number of days: direction of change, rate per week, and whether "
        "it looks like a plateau. Returns 'not enough data' if fewer than 2 weight "
        "entries exist in that window."
    )
    args_schema: Type[BaseModel] = WeightTrendInput

    def _run(self, days: int = 30) -> str:
        db = get_db()
        entries = list(
            db[PROGRESS]
            .find(
                {"user_id": settings.DEFAULT_USER_ID, "weight_kg": {"$ne": None}},
                {"_id": 0, "date": 1, "weight_kg": 1},
            )
            .sort("date", 1)
        )

        if len(entries) < 2:
            return (
                f"Not enough weight data yet ({len(entries)} entr{'y' if len(entries)==1 else 'ies'} "
                f"logged). Need at least 2 save_progress entries with weight_kg to compute a trend."
            )

        first, last = entries[0], entries[-1]
        first_date, last_date = first["date"], last["date"]
        if isinstance(first_date, datetime) and isinstance(last_date, datetime):
            span_days = max((last_date - first_date).days, 1)
        else:
            span_days = max(len(entries) - 1, 1)

        change_kg = last["weight_kg"] - first["weight_kg"]
        rate_per_week = (change_kg / span_days) * 7

        direction = "gaining" if change_kg > 0 else "losing" if change_kg < 0 else "stable"
        plateau = abs(change_kg) < PLATEAU_THRESHOLD_KG and span_days >= 14

        result = (
            f"Weight trend over {span_days} days ({len(entries)} entries): "
            f"{direction}, {change_kg:+.1f} kg total ({rate_per_week:+.2f} kg/week). "
            f"First: {first['weight_kg']}kg, Latest: {last['weight_kg']}kg."
        )
        if plateau:
            result += " This looks like a PLATEAU (minimal change over 2+ weeks)."
        return result