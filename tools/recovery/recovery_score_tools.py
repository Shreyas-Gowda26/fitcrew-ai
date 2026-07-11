"""
tools/recovery/recovery_score_tools.py

RecoveryScoreTool -> deterministic composite score (0-100) from today's
sleep, hydration, and recent training load, so "how recovered am I" is
answered from actual logged data, not vibes.
"""
from datetime import datetime, timezone
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel

from config.settings import settings
from database.connection import get_db
from database.collections import WORKOUTS
from database.daily_log_helpers import get_daily_log


class RecoveryScoreInput(BaseModel):
    pass


class RecoveryScoreTool(BaseTool):
    name: str = "get_recovery_score"
    description: str = (
        "Compute today's recovery score (0-100) from logged sleep hours, water "
        "intake, and recent training intensity/consistency. Higher is more recovered."
    )
    args_schema: Type[BaseModel] = RecoveryScoreInput

    def _run(self) -> str:
        log = get_daily_log(settings.DEFAULT_USER_ID) or {}
        db = get_db()

        recent_workouts = list(
            db[WORKOUTS]
            .find({"user_id": settings.DEFAULT_USER_ID}, {"_id": 0})
            .sort("date", -1)
            .limit(3)
        )

        score = 100
        notes = []

        # Sleep component (out of 40 points)
        sleep_hours = log.get("sleep_hours")
        if sleep_hours is None:
            score -= 20
            notes.append("Sleep not logged today (assumed average, -20)")
        elif sleep_hours < 6:
            score -= 30
            notes.append(f"Low sleep ({sleep_hours}h, -30)")
        elif sleep_hours < 7:
            score -= 10
            notes.append(f"Slightly low sleep ({sleep_hours}h, -10)")

        # Hydration component (out of 20 points)
        water_liters = log.get("water_liters", 0)
        if water_liters < 1.5:
            score -= 15
            notes.append(f"Low hydration ({water_liters}L logged, -15)")

        # Recent training load component (out of 40 points)
        high_intensity_recent = sum(1 for w in recent_workouts if w.get("intensity") == "high")
        if high_intensity_recent >= 3:
            score -= 25
            notes.append(f"{high_intensity_recent} recent high-intensity sessions (-25)")
        elif high_intensity_recent == 2:
            score -= 10
            notes.append(f"{high_intensity_recent} recent high-intensity sessions (-10)")

        score = max(0, min(100, score))

        if score >= 80:
            status = "Well recovered"
        elif score >= 60:
            status = "Adequately recovered"
        elif score >= 40:
            status = "Under-recovered — consider lighter training"
        else:
            status = "Poorly recovered — rest or active recovery recommended"

        result = f"Recovery score: {score}/100 — {status}"
        if notes:
            result += "\n" + "\n".join(f"  - {n}" for n in notes)
        return result