"""
tools/database/progress_tools.py

SaveProgressTool -> periodic body-metric snapshot (weight, measurements).
Distinct from daily_logs: this is for longer-term trend tracking
(weekly/monthly), used later by the Progress Analyst.
"""
from datetime import datetime, timezone
from typing import Type, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from config.settings import settings
from database.connection import get_db
from database.collections import PROGRESS


class SaveProgressInput(BaseModel):
    weight_kg: Optional[float] = None
    body_fat_percent: Optional[float] = None
    measurements: Optional[str] = Field(
        None, description="Free-text measurements, e.g. 'waist 82cm, chest 98cm'"
    )
    notes: Optional[str] = None


class SaveProgressTool(BaseTool):
    name: str = "save_progress"
    description: str = (
        "Save a periodic body-metric snapshot (weight, body fat %, measurements) "
        "for long-term progress tracking. Use this for weekly/periodic check-ins, "
        "not for daily workout/meal logging."
    )
    args_schema: Type[BaseModel] = SaveProgressInput

    def _run(
        self,
        weight_kg: Optional[float] = None,
        body_fat_percent: Optional[float] = None,
        measurements: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> str:
        db = get_db()
        db[PROGRESS].insert_one(
            {
                "user_id": settings.DEFAULT_USER_ID,
                "date": datetime.now(timezone.utc),
                "weight_kg": weight_kg,
                "body_fat_percent": body_fat_percent,
                "measurements": measurements,
                "notes": notes,
            }
        )
        return "Progress snapshot saved successfully."