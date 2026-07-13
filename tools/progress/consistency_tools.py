"""
tools/progress/consistency_tools.py

ConsistencyAnalyzerTool -> compares actual logged workouts over a period
against an expected frequency derived from the user's activity_level, so
"how consistent have I been" is grounded in real logs, not vibes.
"""
from datetime import datetime, timedelta, timezone
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from config.settings import settings
from database.connection import get_db
from database.collections import WORKOUTS, USERS

# Rough expected training days/week by activity_level (used only as a
# reference point for consistency %, not a hard rule).
EXPECTED_DAYS_PER_WEEK = {
    "sedentary": 1,
    "light": 2,
    "moderate": 4,
    "active": 6,
    "very_active": 6,
}


class ConsistencyInput(BaseModel):
    days: int = Field(7, description="How many days back to analyze (7 for weekly, 30 for monthly)")


class ConsistencyAnalyzerTool(BaseTool):
    name: str = "analyze_consistency"
    description: str = (
        "Analyze workout consistency over the given period (default 7 days): how "
        "many sessions were logged vs. roughly expected for the user's activity "
        "level, as a percentage."
    )
    args_schema: Type[BaseModel] = ConsistencyInput

    def _run(self, days: int = 7) -> str:
        db = get_db()
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        sessions = db[WORKOUTS].count_documents(
            {"user_id": settings.DEFAULT_USER_ID, "date": {"$gte": cutoff}}
        )

        profile = db[USERS].find_one({"user_id": settings.DEFAULT_USER_ID}, {"_id": 0})
        activity_level = (profile or {}).get("activity_level", "moderate")
        expected_per_week = EXPECTED_DAYS_PER_WEEK.get(activity_level, 4)
        expected = round(expected_per_week * (days / 7), 1)

        pct = round((sessions / expected) * 100) if expected > 0 else 0

        if pct >= 90:
            verdict = "Excellent consistency"
        elif pct >= 60:
            verdict = "Reasonable consistency, some room to improve"
        elif sessions == 0:
            verdict = "No workouts logged in this period"
        else:
            verdict = "Consistency is low relative to your activity level"

        return (
            f"Last {days} days: {sessions} workout(s) logged vs. ~{expected} expected "
            f"for '{activity_level}' activity level ({pct}%). {verdict}."
        )