"""
tools/database/meal_tools.py

LogMealTool -> record a meal + its calories/macros, and roll the calories
into today's daily_logs summary.
"""
from datetime import datetime, timezone
from typing import Type, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from config.settings import settings
from database.connection import get_db
from database.collections import MEALS
from database.daily_log_helpers import upsert_daily_log


class LogMealInput(BaseModel):
    meal_type: str = Field(..., description="'breakfast', 'lunch', 'dinner', or 'snack'")
    food_items: str = Field(..., description="Description of what was eaten")
    calories: Optional[float] = Field(None, description="Estimated calories for this meal")
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None


class LogMealTool(BaseTool):
    name: str = "log_meal"
    description: str = (
        "Record a meal the user ate today, including estimated calories/macros "
        "if known. Rolls the calories into today's daily summary total."
    )
    args_schema: Type[BaseModel] = LogMealInput

    def _run(
        self,
        meal_type: str,
        food_items: str,
        calories: Optional[float] = None,
        protein_g: Optional[float] = None,
        carbs_g: Optional[float] = None,
        fat_g: Optional[float] = None,
    ) -> str:
        db = get_db()
        db[MEALS].insert_one(
            {
                "user_id": settings.DEFAULT_USER_ID,
                "date": datetime.now(timezone.utc),
                "meal_type": meal_type,
                "food_items": food_items,
                "calories": calories,
                "protein_g": protein_g,
                "carbs_g": carbs_g,
                "fat_g": fat_g,
            }
        )
        upsert_daily_log(
            settings.DEFAULT_USER_ID,
            calories_logged=True,
            increments={"total_calories_today": calories or 0},
        )
        return "Meal logged successfully."