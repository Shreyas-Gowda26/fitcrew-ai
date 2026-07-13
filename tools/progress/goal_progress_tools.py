"""
tools/progress/goal_progress_tools.py

GoalProgressTool -> compares the user's actual weight trend (from
save_progress entries) against what's expected for their stated goal
(lose_weight / maintain / gain_muscle), so feedback is grounded in real
data rather than generic encouragement.
"""
from datetime import datetime, timezone
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel

from config.settings import settings
from database.connection import get_db
from database.collections import PROGRESS, USERS

# Healthy expected rate ranges, kg/week
GOAL_EXPECTATIONS = {
    "lose_weight": {"direction": "losing", "min_rate": 0.25, "max_rate": 1.0},
    "gain_muscle": {"direction": "gaining", "min_rate": 0.1, "max_rate": 0.5},
    "maintain": {"direction": "stable", "min_rate": 0.0, "max_rate": 0.2},
}


class GoalProgressInput(BaseModel):
    pass


class GoalProgressTool(BaseTool):
    name: str = "check_goal_progress"
    description: str = (
        "Compare the user's actual weight trend against what's expected for their "
        "stated goal (lose_weight/maintain/gain_muscle), and report whether "
        "progress is on track, too slow, too fast, or going the wrong direction."
    )
    args_schema: Type[BaseModel] = GoalProgressInput

    def _run(self) -> str:
        db = get_db()
        profile = db[USERS].find_one({"user_id": settings.DEFAULT_USER_ID}, {"_id": 0})
        if not profile or "goal" not in profile:
            return "No profile/goal found. Set up the profile first."
        goal = profile["goal"]
        expectation = GOAL_EXPECTATIONS.get(goal)
        if not expectation:
            return f"Unknown goal '{goal}'."

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
                f"Not enough weight data yet ({len(entries)} entr{'y' if len(entries)==1 else 'ies'}) "
                f"to assess progress toward goal '{goal}'. Log at least 2 save_progress "
                f"entries with weight_kg over time."
            )

        first, last = entries[0], entries[-1]
        first_date, last_date = first["date"], last["date"]
        if isinstance(first_date, datetime) and isinstance(last_date, datetime):
            span_days = max((last_date - first_date).days, 1)
        else:
            span_days = max(len(entries) - 1, 1)

        change_kg = last["weight_kg"] - first["weight_kg"]
        rate_per_week = (change_kg / span_days) * 7
        actual_direction = "gaining" if change_kg > 0.1 else "losing" if change_kg < -0.1 else "stable"

        expected_dir = expectation["direction"]
        min_rate, max_rate = expectation["min_rate"], expectation["max_rate"]
        abs_rate = abs(rate_per_week)

        if actual_direction != expected_dir and expected_dir != "stable":
            verdict = f"WRONG DIRECTION for goal '{goal}': expected {expected_dir}, actual is {actual_direction}."
        elif expected_dir == "stable" and abs_rate > max_rate:
            verdict = f"Weight is fluctuating more than expected for a 'maintain' goal ({rate_per_week:+.2f} kg/week)."
        elif abs_rate < min_rate:
            verdict = f"On the right direction but SLOWER than expected ({rate_per_week:+.2f} kg/week, expected {min_rate}-{max_rate} kg/week)."
        elif abs_rate > max_rate:
            verdict = f"On the right direction but FASTER than the healthy range ({rate_per_week:+.2f} kg/week, expected {min_rate}-{max_rate} kg/week) — consider adjusting."
        else:
            verdict = f"ON TRACK for goal '{goal}' ({rate_per_week:+.2f} kg/week, within expected {min_rate}-{max_rate} kg/week range)."

        return (
            f"Goal: {goal}. Weight change over {span_days} days: {change_kg:+.1f} kg "
            f"({rate_per_week:+.2f} kg/week). {verdict}"
        )