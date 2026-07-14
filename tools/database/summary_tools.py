"""
tools/database/summary_tools.py

DailySummaryTool -> pulls together today's daily_logs doc into the
"Today's Summary" view used in the CLI (sleep/water/calories/workout ticks).
Sleep & water fields get populated once the Recovery Agent's tools exist
(Phase 5) — until then they'll just show as not logged yet.
"""
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel

from config.settings import settings
from database.daily_log_helpers import get_daily_log, today_str


class DailySummaryInput(BaseModel):
    pass


class DailySummaryTool(BaseTool):
    name: str = "get_daily_summary"
    description: str = (
        "Get today's summary: whether sleep, water, calories, and workout have "
        "been logged today, plus total calories logged so far. This tool takes "
        "NO arguments — call it with an empty input, never pass 'limit' or any "
        "other parameter (there is only ever one summary: today's)."
    )
    args_schema: Type[BaseModel] = DailySummaryInput

    def _run(self) -> str:
        log = get_daily_log(settings.DEFAULT_USER_ID) or {}

        def tick(key: str) -> str:
            return "✔" if log.get(key) else "✘"

        summary = (
            f"Summary for {today_str()}:\n"
            f"  Sleep:    {tick('sleep_logged')} "
            f"({log.get('sleep_hours', 'not logged')} hrs)\n"
            f"  Water:    {tick('water_logged')} "
            f"({log.get('water_liters', 'not logged')} L)\n"
            f"  Calories: {tick('calories_logged')} "
            f"({log.get('total_calories_today', 0)} kcal so far)\n"
            f"  Workout:  {tick('workout_logged')}\n"
        )
        return summary