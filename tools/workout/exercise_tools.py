"""
tools/workout/exercise_tools.py

ExerciseRecommendationTool -> deterministic lookup of candidate exercises
for a muscle group given available equipment, so the agent grounds its
plan in a real exercise list instead of inventing names.
"""
from typing import Type, List

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# Small curated exercise bank. Not exhaustive — enough to ground the LLM's
# choices. Easy to extend later.
EXERCISE_BANK = {
    "chest": {
        "bodyweight": ["Push-ups", "Incline push-ups", "Diamond push-ups"],
        "dumbbell": ["Dumbbell bench press", "Dumbbell flyes", "Dumbbell floor press"],
        "gym": ["Barbell bench press", "Incline barbell press", "Cable crossover", "Chest dip"],
    },
    "back": {
        "bodyweight": ["Pull-ups", "Inverted rows", "Superman holds"],
        "dumbbell": ["Single-arm dumbbell row", "Renegade rows"],
        "gym": ["Deadlift", "Lat pulldown", "Barbell row", "Seated cable row"],
    },
    "legs": {
        "bodyweight": ["Bodyweight squats", "Lunges", "Glute bridges", "Wall sit"],
        "dumbbell": ["Goblet squats", "Dumbbell lunges", "Romanian deadlift (dumbbell)"],
        "gym": ["Barbell squat", "Leg press", "Leg curl", "Leg extension", "Hip thrust"],
    },
    "shoulders": {
        "bodyweight": ["Pike push-ups", "Handstand hold"],
        "dumbbell": ["Dumbbell shoulder press", "Lateral raises", "Front raises"],
        "gym": ["Barbell overhead press", "Cable lateral raise", "Face pulls"],
    },
    "arms": {
        "bodyweight": ["Chin-ups", "Bench dips"],
        "dumbbell": ["Dumbbell curls", "Overhead tricep extension", "Hammer curls"],
        "gym": ["Barbell curl", "Cable tricep pushdown", "Preacher curl"],
    },
    "core": {
        "bodyweight": ["Plank", "Bicycle crunches", "Leg raises", "Mountain climbers"],
        "dumbbell": ["Weighted sit-ups", "Russian twists (weighted)"],
        "gym": ["Cable crunch", "Ab wheel rollout", "Hanging leg raise"],
    },
    "cardio": {
        "bodyweight": ["Jumping jacks", "Burpees", "High knees", "Shadow boxing"],
        "dumbbell": ["Dumbbell thrusters"],
        "gym": ["Treadmill intervals", "Rowing machine", "Stair climber"],
    },
    "cricket_specific": {
        "bodyweight": [
            "Rotational medicine ball throws (bodyweight variant: standing twists)",
            "Lateral bounds",
            "Sprint starts (10-20m)",
            "Shadow bowling action drills",
        ],
        "dumbbell": ["Single-arm dumbbell rotational press", "Dumbbell woodchoppers"],
        "gym": ["Cable rotational chops", "Box jumps", "Sled pushes"],
    },
}


class ExerciseRecommendationInput(BaseModel):
    muscle_group: str = Field(
        ..., description=f"One of: {list(EXERCISE_BANK.keys())}"
    )
    equipment: str = Field(
        ..., description="One of: 'bodyweight', 'dumbbell', 'gym'"
    )


class ExerciseRecommendationTool(BaseTool):
    name: str = "recommend_exercises"
    description: str = (
        "Get a grounded list of real candidate exercises for a specific muscle "
        "group and equipment level (bodyweight/dumbbell/gym), including "
        "cricket_specific drills. Use this instead of inventing exercise names."
    )
    args_schema: Type[BaseModel] = ExerciseRecommendationInput

    def _run(self, muscle_group: str, equipment: str) -> str:
        muscle_group = muscle_group.lower().strip()
        equipment = equipment.lower().strip()

        if muscle_group not in EXERCISE_BANK:
            return f"Unknown muscle_group. Choose from: {list(EXERCISE_BANK.keys())}"
        if equipment not in ("bodyweight", "dumbbell", "gym"):
            return "equipment must be 'bodyweight', 'dumbbell', or 'gym'."

        options: List[str] = EXERCISE_BANK[muscle_group][equipment]
        return f"{muscle_group} ({equipment}): " + ", ".join(options)