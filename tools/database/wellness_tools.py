"""
tools/database/wellness_tools.py

LogSleepTool -> record last night's sleep, ticks today's daily summary
LogWaterTool -> record water intake (accumulates across the day)
"""
from typing import Type, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from config.settings import settings
from database.daily_log_helpers import upsert_daily_log


class LogSleepInput(BaseModel):
    hours: float = Field(..., description="Hours of sleep last night")
    quality: Optional[str] = Field(None, description="'poor', 'okay', or 'good'")


class LogSleepTool(BaseTool):
    name: str = "log_sleep"
    description: str = "Record last night's sleep duration (and quality, if known) for today."
    args_schema: Type[BaseModel] = LogSleepInput

    def _run(self, hours: float, quality: Optional[str] = None) -> str:
        upsert_daily_log(
            settings.DEFAULT_USER_ID,
            sleep_logged=True,
            sleep_hours=hours,
            sleep_quality=quality,
        )
        return f"Sleep logged: {hours}h" + (f" ({quality})" if quality else "")


class LogWaterInput(BaseModel):
    liters: float = Field(..., description="Amount of water drunk just now, in liters (added to today's total)")


class LogWaterTool(BaseTool):
    name: str = "log_water"
    description: str = "Add a water intake entry (in liters) to today's running total."
    args_schema: Type[BaseModel] = LogWaterInput

    def _run(self, liters: float) -> str:
        upsert_daily_log(
            settings.DEFAULT_USER_ID,
            water_logged=True,
            increments={"water_liters": liters},
        )
        return f"Logged {liters}L of water."