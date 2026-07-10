"""
tools/nutrition/meal_planner_tools.py

MealPlannerTool -> deterministic split of a daily calorie/macro target
across breakfast/lunch/dinner/snack, plus grounded meal ideas filtered by
dietary preference. The agent still writes the actual narrative plan, but
the numbers and food ideas come from here.
"""
from typing import Type, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# % of daily calories per meal
MEAL_SPLIT = {
    "breakfast": 0.25,
    "lunch": 0.35,
    "dinner": 0.30,
    "snacks": 0.10,
}

MEAL_IDEAS = {
    "vegetarian": {
        "breakfast": ["Oats with milk and banana", "Vegetable poha", "Idli with sambar"],
        "lunch": ["Rice, dal, sabzi, curd", "Chapati with paneer curry and salad"],
        "dinner": ["Khichdi with vegetables", "Roti with dal and mixed vegetables"],
        "snacks": ["Roasted chana", "Fruit + almonds", "Curd with fruit"],
    },
    "eggetarian": {
        "breakfast": ["Boiled eggs with toast", "Egg bhurji with roti"],
        "lunch": ["Rice, dal, egg curry, salad"],
        "dinner": ["Egg curry with roti", "Omelette with vegetables"],
        "snacks": ["Boiled eggs", "Fruit + peanut butter"],
    },
    "non_vegetarian": {
        "breakfast": ["Egg whites with oats", "Chicken sausage with toast"],
        "lunch": ["Rice, dal, chicken curry, salad"],
        "dinner": ["Grilled chicken breast with sweet potato and vegetables"],
        "snacks": ["Whey protein shake", "Boiled eggs", "Fruit + almonds"],
    },
}


class MealPlannerInput(BaseModel):
    target_calories: float = Field(..., description="Total daily calorie target")
    dietary_preference: str = Field(
        ..., description="One of: vegetarian, eggetarian, non_vegetarian"
    )


class MealPlannerTool(BaseTool):
    name: str = "plan_meals"
    description: str = (
        "Split a daily calorie target across breakfast/lunch/dinner/snacks and "
        "suggest grounded meal ideas based on dietary preference (vegetarian/"
        "eggetarian/non_vegetarian). Use lookup_food afterward for exact macros "
        "of chosen items."
    )
    args_schema: Type[BaseModel] = MealPlannerInput

    def _run(self, target_calories: float, dietary_preference: str) -> str:
        pref = dietary_preference.lower().strip()
        if pref not in MEAL_IDEAS:
            return f"dietary_preference must be one of: {list(MEAL_IDEAS.keys())}"

        lines = []
        for meal, pct in MEAL_SPLIT.items():
            cals = target_calories * pct
            ideas = ", ".join(MEAL_IDEAS[pref][meal])
            lines.append(f"{meal.capitalize()} (~{cals:.0f} kcal): e.g. {ideas}")

        return "\n".join(lines)