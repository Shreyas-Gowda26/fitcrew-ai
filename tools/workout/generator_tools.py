"""
tools/workout/generator_tools.py

WorkoutGeneratorTool  -> deterministic weekly split selector based on
                         experience level, goal, and days available.
WorkoutDifficultyTool -> deterministic sets/reps/rest scheme based on
                         experience level and goal.

Both are "decision tables", not full plan writers — the agent still uses
the LLM + recommend_exercises to fill in actual exercises. This keeps the
numbers/structure grounded instead of left to the LLM to invent.
"""
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

SPLITS = {
    ("beginner", 3): "Full Body A/B/C — Mon/Wed/Fri, all major muscle groups each session",
    ("beginner", 4): "Upper/Lower split — Mon/Tue/Thu/Fri",
    ("intermediate", 4): "Upper/Lower split with volume progression — Mon/Tue/Thu/Fri",
    ("intermediate", 5): "Push/Pull/Legs + Upper/Lower — Mon-Fri",
    ("advanced", 5): "Push/Pull/Legs/Push/Pull — Mon-Fri, accessory work daily",
    ("advanced", 6): "Push/Pull/Legs x2 — Mon-Sat",
}

DIFFICULTY_SCHEMES = {
    ("beginner", "lose_weight"): "3 sets x 12-15 reps, 60s rest, focus on form + higher volume",
    ("beginner", "maintain"): "3 sets x 10-12 reps, 60-90s rest",
    ("beginner", "gain_muscle"): "3 sets x 8-12 reps, 90s rest, moderate weight",
    ("intermediate", "lose_weight"): "4 sets x 12-15 reps, 45-60s rest, add supersets",
    ("intermediate", "maintain"): "4 sets x 8-12 reps, 90s rest",
    ("intermediate", "gain_muscle"): "4 sets x 6-10 reps, 90-120s rest, progressive overload weekly",
    ("advanced", "lose_weight"): "4-5 sets x 12-20 reps, 30-45s rest, circuit-style",
    ("advanced", "maintain"): "4 sets x 6-10 reps, 2 min rest",
    ("advanced", "gain_muscle"): "5 sets x 4-8 reps, 2-3 min rest, strict progressive overload",
}


class WorkoutGeneratorInput(BaseModel):
    experience_level: str = Field(..., description="beginner, intermediate, or advanced")
    days_per_week: int = Field(..., description="How many days per week the user can train")
    goal: str = Field(..., description="lose_weight, maintain, or gain_muscle")


class WorkoutGeneratorTool(BaseTool):
    name: str = "generate_workout_split"
    description: str = (
        "Get the recommended weekly workout split structure (which days train "
        "which muscle groups) based on experience level, days available, and goal. "
        "Call this first, then use recommend_exercises to fill in each day."
    )
    args_schema: Type[BaseModel] = WorkoutGeneratorInput

    def _run(self, experience_level: str, days_per_week: int, goal: str) -> str:
        experience_level = experience_level.lower().strip()
        key = (experience_level, days_per_week)
        split = SPLITS.get(key)

        if not split:
            # fall back to nearest available day count for that experience level
            candidates = [d for (lvl, d) in SPLITS if lvl == experience_level]
            if not candidates:
                return f"No split data for experience_level '{experience_level}'."
            nearest = min(candidates, key=lambda d: abs(d - days_per_week))
            split = SPLITS[(experience_level, nearest)]
            return (
                f"No exact match for {days_per_week} days/week at '{experience_level}' level. "
                f"Closest available ({nearest} days/week): {split}"
            )

        return f"Recommended split: {split}"


class WorkoutDifficultyInput(BaseModel):
    experience_level: str = Field(..., description="beginner, intermediate, or advanced")
    goal: str = Field(..., description="lose_weight, maintain, or gain_muscle")


class WorkoutDifficultyTool(BaseTool):
    name: str = "get_difficulty_scheme"
    description: str = (
        "Get the recommended sets/reps/rest scheme for a given experience level "
        "and goal. Use this to fill in prescriptions for each exercise."
    )
    args_schema: Type[BaseModel] = WorkoutDifficultyInput

    def _run(self, experience_level: str, goal: str) -> str:
        experience_level = experience_level.lower().strip()
        goal = goal.lower().strip()
        scheme = DIFFICULTY_SCHEMES.get((experience_level, goal))
        if not scheme:
            return (
                f"No scheme found for experience_level='{experience_level}', goal='{goal}'. "
                f"Valid experience levels: beginner, intermediate, advanced. "
                f"Valid goals: lose_weight, maintain, gain_muscle."
            )
        return scheme