"""
tools/recovery/fatigue_tools.py

FatigueAnalysisTool -> looks at the last 7 days of workout intensity to flag
overtraining/fatigue risk (distinct from RecoveryScoreTool's single-day
snapshot — this one looks at the trend).
"""
from datetime import datetime, timezone
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel

from config.settings import settings
from database.connection import get_db
from database.collections import WORKOUTS


class FatigueAnalysisInput(BaseModel):
    pass


class FatigueAnalysisTool(BaseTool):
    name: str = "analyze_fatigue_risk"
    description: str = (
        "Analyze the last 7 days of workout history to flag overtraining/fatigue "
        "risk as low, moderate, or high, based on volume and intensity trend."
    )
    args_schema: Type[BaseModel] = FatigueAnalysisInput

    def _run(self) -> str:
        db = get_db()
        recent = list(
            db[WORKOUTS]
            .find({"user_id": settings.DEFAULT_USER_ID}, {"_id": 0})
            .sort("date", -1)
            .limit(7)
        )

        if not recent:
            return "No workout history yet — fatigue risk: low (no data)."

        high_count = sum(1 for w in recent if w.get("intensity") == "high")
        total_sessions = len(recent)
        total_minutes = sum(w.get("duration_minutes") or 0 for w in recent)

        if high_count >= 5 or total_minutes > 600:
            risk = "high"
            advice = "Strongly consider a deload week or several rest days."
        elif high_count >= 3 or total_minutes > 400:
            risk = "moderate"
            advice = "Consider mixing in a lighter or active-recovery day soon."
        else:
            risk = "low"
            advice = "Training load looks sustainable."

        return (
            f"Fatigue risk: {risk}\n"
            f"  Sessions in last 7 days: {total_sessions}\n"
            f"  High-intensity sessions: {high_count}\n"
            f"  Total training time: {total_minutes} min\n"
            f"  {advice}"
        )