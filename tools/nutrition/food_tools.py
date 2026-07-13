"""
tools/nutrition/food_tools.py

FoodLookupTool -> curated calorie/macro lookup per 100g for common foods
(including Indian staples), so the agent grounds meal suggestions in real
numbers instead of guessing calorie counts.
"""
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# Values are per 100g, approximate. Small curated bank — easy to extend.
FOOD_DB = {
    "rice (cooked)": {"calories": 130, "protein_g": 2.7, "carbs_g": 28, "fat_g": 0.3},
    "roti / chapati": {"calories": 297, "protein_g": 9, "carbs_g": 59, "fat_g": 4},
    "dal (cooked lentils)": {"calories": 116, "protein_g": 9, "carbs_g": 20, "fat_g": 0.4},
    "paneer": {"calories": 265, "protein_g": 18, "carbs_g": 6, "fat_g": 20},
    "cottage cheese": {"calories": 98, "protein_g": 11, "carbs_g": 3.4, "fat_g": 4.3},
    "chicken breast (cooked)": {"calories": 165, "protein_g": 31, "carbs_g": 0, "fat_g": 3.6},
    "salmon (cooked)": {"calories": 208, "protein_g": 20, "carbs_g": 0, "fat_g": 13},
    "tofu": {"calories": 76, "protein_g": 8, "carbs_g": 1.9, "fat_g": 4.8},
    "egg (whole, boiled)": {"calories": 155, "protein_g": 13, "carbs_g": 1.1, "fat_g": 11},
    "curd / yogurt (plain)": {"calories": 61, "protein_g": 3.5, "carbs_g": 4.7, "fat_g": 3.3},
    "greek yogurt (low-fat)": {"calories": 73, "protein_g": 10, "carbs_g": 3.9, "fat_g": 1.9},
    "milk (whole)": {"calories": 61, "protein_g": 3.2, "carbs_g": 4.8, "fat_g": 3.3},
    "banana": {"calories": 89, "protein_g": 1.1, "carbs_g": 23, "fat_g": 0.3},
    "apple": {"calories": 52, "protein_g": 0.3, "carbs_g": 14, "fat_g": 0.2},
    "oats (dry)": {"calories": 389, "protein_g": 17, "carbs_g": 66, "fat_g": 7},
    "quinoa (cooked)": {"calories": 120, "protein_g": 4.4, "carbs_g": 21, "fat_g": 1.9},
    "millet (cooked)": {"calories": 119, "protein_g": 3.5, "carbs_g": 23, "fat_g": 1},
    "whole wheat bread": {"calories": 247, "protein_g": 13, "carbs_g": 41, "fat_g": 3.4},
    "almonds": {"calories": 579, "protein_g": 21, "carbs_g": 22, "fat_g": 50},
    "walnuts": {"calories": 654, "protein_g": 15, "carbs_g": 14, "fat_g": 65},
    "peanut butter": {"calories": 588, "protein_g": 25, "carbs_g": 20, "fat_g": 50},
    "honey": {"calories": 304, "protein_g": 0.3, "carbs_g": 82, "fat_g": 0},
    "sweet potato (cooked)": {"calories": 90, "protein_g": 2, "carbs_g": 21, "fat_g": 0.1},
    "spinach (cooked)": {"calories": 23, "protein_g": 2.9, "carbs_g": 3.6, "fat_g": 0.4},
    "chickpeas (cooked)": {"calories": 164, "protein_g": 9, "carbs_g": 27, "fat_g": 2.6},
    "whey protein (generic)": {"calories": 400, "protein_g": 80, "carbs_g": 8, "fat_g": 5},
}


class FoodLookupInput(BaseModel):
    food_name: str = Field(..., description="Food to look up, e.g. 'roti', 'chicken breast'")


class FoodLookupTool(BaseTool):
    name: str = "lookup_food"
    description: str = (
        "Look up calories and macros per 100g for a common food (Indian staples "
        "included: rice, roti, dal, paneer, curd, etc). Use this to ground meal "
        "plan calorie/macro numbers instead of estimating them."
    )
    args_schema: Type[BaseModel] = FoodLookupInput

    def _run(self, food_name: str) -> str:
        query = food_name.lower().strip()

        # exact match first, then substring match
        if query in FOOD_DB:
            match = query
        else:
            candidates = [k for k in FOOD_DB if query in k or k in query]
            if not candidates:
                return (
                    f"'{food_name}' not in the food database. Known foods: "
                    f"{', '.join(FOOD_DB.keys())}"
                )
            match = candidates[0]

        data = FOOD_DB[match]
        return (
            f"{match} (per 100g): {data['calories']} kcal, "
            f"Protein: {data['protein_g']}g, Carbs: {data['carbs_g']}g, Fat: {data['fat_g']}g"
        )