"""
tools/fitness/calculator_tools.py

FitnessCalculatorTool -> one deterministic tool covering BMI, BMR, TDEE,
protein target, water target, and macro split. Merged into a single tool
(instead of 6 separate ones) so the agent doesn't have to guess between
near-identical tool names for what's really one family of arithmetic.
"""
from typing import Type, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

GOAL_CALORIE_ADJUSTMENTS = {
    "lose_weight": -500,
    "maintain": 0,
    "gain_muscle": 300,
}

VALID_OPERATIONS = ["bmi", "bmr", "tdee", "protein", "water", "macros"]


class FitnessCalculatorInput(BaseModel):
    operation: str = Field(..., description=f"One of: {VALID_OPERATIONS}")
    sex: Optional[str] = Field(None, description="'male' or 'female' (needed for bmr/tdee/macros)")
    age: Optional[int] = Field(None, description="Needed for bmr/tdee/macros")
    weight_kg: float = Field(..., description="Always required")
    height_cm: Optional[float] = Field(None, description="Needed for bmi/bmr/tdee/macros")
    activity_level: Optional[str] = Field(
        None, description=f"Needed for tdee/macros. One of: {list(ACTIVITY_MULTIPLIERS)}"
    )
    goal: Optional[str] = Field(
        None, description=f"Needed for macros. One of: {list(GOAL_CALORIE_ADJUSTMENTS)}"
    )


class FitnessCalculatorTool(BaseTool):
    name: str = "fitness_calculator"
    description: str = (
        "Deterministic fitness math: BMI, BMR, TDEE, daily protein target, daily "
        "water target, and full macro split. Always use this instead of estimating "
        "these numbers yourself. Pass `operation` plus whichever fields it needs "
        "(see each operation's requirements: bmi needs weight_kg+height_cm; "
        "bmr/tdee need sex+age+weight_kg+height_cm(+activity_level for tdee); "
        "protein needs weight_kg(+goal); water needs weight_kg; macros needs "
        "sex+age+weight_kg+height_cm+activity_level+goal)."
    )
    args_schema: Type[BaseModel] = FitnessCalculatorInput

    def _bmr(self, sex: str, age: int, weight_kg: float, height_cm: float) -> float:
        if sex == "male":
            return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    def _run(
        self,
        operation: str,
        weight_kg: float,
        sex: Optional[str] = None,
        age: Optional[int] = None,
        height_cm: Optional[float] = None,
        activity_level: Optional[str] = None,
        goal: Optional[str] = None,
    ) -> str:
        operation = operation.lower().strip()
        if operation not in VALID_OPERATIONS:
            return f"Invalid operation. Choose from: {VALID_OPERATIONS}"

        if operation == "bmi":
            if not height_cm:
                return "bmi requires height_cm."
            height_m = height_cm / 100
            bmi = weight_kg / (height_m ** 2)
            category = (
                "underweight" if bmi < 18.5 else
                "normal" if bmi < 25 else
                "overweight" if bmi < 30 else "obese"
            )
            return f"BMI: {bmi:.1f} ({category})"

        if operation == "water":
            # simple 35ml per kg baseline
            liters = (weight_kg * 35) / 1000
            return f"Recommended daily water intake: {liters:.1f} L"

        if operation == "protein":
            # 1.6-2.2 g/kg depending on goal; default to gain_muscle-friendly upper range
            per_kg = 2.0 if goal == "gain_muscle" else 1.8 if goal == "lose_weight" else 1.6
            grams = weight_kg * per_kg
            return f"Recommended daily protein: {grams:.0f}g ({per_kg}g/kg)"

        # bmr, tdee, macros all need sex/age/height
        if not all([sex, age, height_cm]):
            return f"'{operation}' requires sex, age, and height_cm."
        sex = sex.lower().strip()

        bmr = self._bmr(sex, age, weight_kg, height_cm)
        if operation == "bmr":
            return f"BMR: {bmr:.0f} kcal/day"

        if not activity_level or activity_level not in ACTIVITY_MULTIPLIERS:
            return f"'{operation}' requires a valid activity_level: {list(ACTIVITY_MULTIPLIERS)}"
        tdee = bmr * ACTIVITY_MULTIPLIERS[activity_level]

        if operation == "tdee":
            return f"BMR: {bmr:.0f} kcal/day, TDEE (maintenance): {tdee:.0f} kcal/day"

        # macros
        if not goal or goal not in GOAL_CALORIE_ADJUSTMENTS:
            return f"macros requires a valid goal: {list(GOAL_CALORIE_ADJUSTMENTS)}"
        target_calories = tdee + GOAL_CALORIE_ADJUSTMENTS[goal]
        protein_g = (target_calories * 0.30) / 4
        carbs_g = (target_calories * 0.40) / 4
        fat_g = (target_calories * 0.30) / 9

        return (
            f"BMR: {bmr:.0f} kcal/day\n"
            f"TDEE: {tdee:.0f} kcal/day\n"
            f"Target calories ('{goal}'): {target_calories:.0f} kcal/day\n"
            f"Macros -> Protein: {protein_g:.0f}g, Carbs: {carbs_g:.0f}g, Fat: {fat_g:.0f}g"
        )