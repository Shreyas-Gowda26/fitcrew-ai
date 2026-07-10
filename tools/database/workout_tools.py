"""
tools/database/workout_tools.py

LogWorkoutTool     -> record a completed workout
WorkoutHistoryTool -> fetch recent workout entries
"""
from datetime import datetime, timezone
from typing import Type, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from config.settings import settings
from database.connection import get_db
from database.collections import WORKOUTS
from database.daily_log_helpers import upsert_daily_log


class LogWorkoutInput(BaseModel):
    workout_type: str = Field(..., description="e.g. 'strength', 'cardio', 'cricket_training', 'rest'")
    description: str = Field(..., description="What was done, e.g. 'Upper body: bench press, rows, curls'")
    duration_minutes: Optional[int] = Field(None, description="Duration of the session in minutes")
    intensity: Optional[str] = Field(None, description="'low', 'moderate', or 'high'")
    notes: Optional[str] = None


class LogWorkoutTool(BaseTool):
    name: str = "log_workout"
    description: str = (
        "Record a workout the user completed today. Also ticks off today's "
        "workout status in the daily summary."
    )
    args_schema: Type[BaseModel] = LogWorkoutInput

    def _run(
        self,
        workout_type: str,
        description: str,
        duration_minutes: Optional[int] = None,
        intensity: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> str:
        db = get_db()
        db[WORKOUTS].insert_one(
            {
                "user_id": settings.DEFAULT_USER_ID,
                "date": datetime.now(timezone.utc),
                "workout_type": workout_type,
                "description": description,
                "duration_minutes": duration_minutes,
                "intensity": intensity,
                "notes": notes,
            }
        )
        upsert_daily_log(settings.DEFAULT_USER_ID, workout_logged=True)
        return "Workout logged successfully."


class WorkoutHistoryInput(BaseModel):
    limit: int = Field(10, description="Max number of recent workouts to fetch")


class WorkoutHistoryTool(BaseTool):
    name: str = "get_workout_history"
    description: str = (
        "Fetch the user's most recent logged workouts, newest first. Useful "
        "for checking consistency, applying progressive overload, or deciding "
        "today's session."
    )
    args_schema: Type[BaseModel] = WorkoutHistoryInput

    def _run(self, limit: int = 10) -> str:
        db = get_db()
        entries = list(
            db[WORKOUTS]
            .find({"user_id": settings.DEFAULT_USER_ID}, {"_id": 0})
            .sort("date", -1)
            .limit(limit)
        )
        if not entries:
            return "No workout history found yet."
        return str(entries)