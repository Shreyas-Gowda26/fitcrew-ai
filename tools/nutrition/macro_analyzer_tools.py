"""
tools/nutrition/macro_analyzer_tools.py

MacroAnalyzerTool -> sums today's logged meals (from the `meals` collection)
and compares them against a given target, so "how am I doing today" is
answered from real logged data, not guesswork.
"""
from datetime import datetime, timezone
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from config.settings import settings
from database.connection import get_db
from database.collections import MEALS


class MacroAnalyzerInput(BaseModel):
    target_calories: float = Field(..., description="Daily calorie target to compare against")
    target_protein_g: float = Field(..., description="Daily protein target (g) to compare against")


class MacroAnalyzerTool(BaseTool):
    name: str = "analyze_todays_macros"
    description: str = (
        "Sum up all meals logged today and compare totals against a given "
        "calorie/protein target, reporting how much room is left for the day."
    )
    args_schema: Type[BaseModel] = MacroAnalyzerInput

    def _run(self, target_calories: float, target_protein_g: float) -> str:
        db = get_db()
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        meals_today = list(
            db[MEALS].find(
                {"user_id": settings.DEFAULT_USER_ID, "date": {"$gte": today_start}},
                {"_id": 0},
            )
        )

        if not meals_today:
            return (
                f"No meals logged yet today. Target: {target_calories:.0f} kcal, "
                f"{target_protein_g:.0f}g protein remaining."
            )

        total_cal = sum(m.get("calories") or 0 for m in meals_today)
        total_protein = sum(m.get("protein_g") or 0 for m in meals_today)

        cal_remaining = target_calories - total_cal
        protein_remaining = target_protein_g - total_protein

        return (
            f"Logged today: {total_cal:.0f} kcal / {target_calories:.0f} kcal target "
            f"({cal_remaining:.0f} kcal remaining)\n"
            f"Protein: {total_protein:.0f}g / {target_protein_g:.0f}g target "
            f"({protein_remaining:.0f}g remaining)\n"
            f"Meals logged: {len(meals_today)}"
        )