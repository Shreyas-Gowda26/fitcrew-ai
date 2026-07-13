"""
tools/progress/report_tools.py

WeeklyReportTool -> aggregates workouts, meals, and weight entries over a
period (default 7 days, pass days=30 for a monthly report) into one summary.
"""
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from config.settings import settings
from database.connection import get_db
from database.collections import WORKOUTS, MEALS, PROGRESS


class WeeklyReportInput(BaseModel):
    days: int = Field(7, description="Report window in days: 7 for weekly, 30 for monthly")


class WeeklyReportTool(BaseTool):
    name: str = "get_period_report"
    description: str = (
        "Generate a report of activity over the given period (default 7 days for "
        "weekly, pass 30 for monthly): workouts logged, total training time, "
        "intensity breakdown, meals logged, and any weight entries in that window."
    )
    args_schema: Type[BaseModel] = WeeklyReportInput

    def _run(self, days: int = 7) -> str:
        db = get_db()
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        uid = settings.DEFAULT_USER_ID

        workouts = list(db[WORKOUTS].find({"user_id": uid, "date": {"$gte": cutoff}}, {"_id": 0}))
        meals = list(db[MEALS].find({"user_id": uid, "date": {"$gte": cutoff}}, {"_id": 0}))
        progress_entries = list(
            db[PROGRESS].find({"user_id": uid, "date": {"$gte": cutoff}}, {"_id": 0})
        )

        total_minutes = sum(w.get("duration_minutes") or 0 for w in workouts)
        intensity_counts = Counter(w.get("intensity", "unspecified") for w in workouts)
        intensity_str = ", ".join(f"{k}: {v}" for k, v in intensity_counts.items()) or "none"

        weight_entries = [p for p in progress_entries if p.get("weight_kg") is not None]
        weight_str = "no weight logged this period"
        if weight_entries:
            weights = [p["weight_kg"] for p in weight_entries]
            weight_str = f"{len(weight_entries)} entries, range {min(weights)}-{max(weights)}kg"

        return (
            f"Report for last {days} days:\n"
            f"  Workouts logged: {len(workouts)} (total {total_minutes} min, intensity: {intensity_str})\n"
            f"  Meals logged: {len(meals)}\n"
            f"  Weight entries: {weight_str}"
        )