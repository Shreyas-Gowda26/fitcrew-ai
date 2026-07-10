"""
agents/workout_agent.py

The Workout Agent: generates workout plans, applies progressive overload,
recommends exercises, handles home workouts and cricket-specific training,
and schedules weekly workouts.
"""
from crewai import Agent

from utils.llm import get_llm
from tools.database import GetUserProfileTool, LogWorkoutTool, WorkoutHistoryTool
from tools.workout import (
    ExerciseRecommendationTool,
    WorkoutGeneratorTool,
    WorkoutDifficultyTool,
    RestDayCheckerTool,
)


def build_workout_agent() -> Agent:
    return Agent(
        role="Workout Agent",
        goal=(
            "Design safe, effective, personalized workout plans and exercise "
            "recommendations based on the user's profile, training history, and "
            "recovery status. Apply progressive overload over time rather than "
            "repeating the same plan indefinitely."
        ),
        backstory=(
            "You are an experienced strength & conditioning coach, including "
            "sport-specific programming (e.g. cricket). You never invent exercise "
            "names or set/rep numbers from thin air — you always ground them using "
            "your tools (generate_workout_split, get_difficulty_scheme, "
            "recommend_exercises, check_rest_day_needed) and only use your own "
            "judgment to combine those grounded facts into a coherent, personalized "
            "plan and to explain the reasoning briefly."
        ),
        tools=[
            GetUserProfileTool(),
            WorkoutHistoryTool(),
            LogWorkoutTool(),
            WorkoutGeneratorTool(),
            WorkoutDifficultyTool(),
            ExerciseRecommendationTool(),
            RestDayCheckerTool(),
        ],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )