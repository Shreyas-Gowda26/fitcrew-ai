"""
agents/workout_agent.py

The Workout Agent: generates workout plans, applies progressive overload,
recommends exercises, handles home workouts and cricket-specific training,
and schedules weekly workouts.
"""
from crewai import Agent

from config.settings import settings
from utils.llm import get_llm
from tools.database import GetUserProfileTool, LogWorkoutTool, WorkoutHistoryTool
from tools.workout import (
    ExerciseRecommendationTool,
    WorkoutGeneratorTool,
    WorkoutDifficultyTool,
    RestDayCheckerTool,
)

# Web search is optional: only enabled if SERPER_API_KEY is set, so the app
# still works fine for anyone who hasn't signed up for a Serper key.
_search_tools = []
if settings.SERPER_API_KEY:
    from crewai_tools import SerperDevTool
    _search_tools = [SerperDevTool()]


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
            "plan and to explain the reasoning briefly. Before ever asking the user a "
            "question, you check get_user_profile and get_workout_history — the user "
            "may have already saved their experience level, goal, and equipment, and "
            "asking them to repeat information you already have wastes their time. "
            "Only ask the user for fields that come back missing. If web search is "
            "available and the user asks about something your curated tools don't "
            "cover (e.g. proper technique for a specific unusual movement, or "
            "current best practice for a sport-specific drill), you may search the "
            "web — but still prefer your own grounded tools first for anything they "
            "already cover, and never search for things (like set/rep schemes) that "
            "generate_workout_split or get_difficulty_scheme already answer."
        ),
        tools=[
            GetUserProfileTool(),
            WorkoutHistoryTool(),
            LogWorkoutTool(),
            WorkoutGeneratorTool(),
            WorkoutDifficultyTool(),
            ExerciseRecommendationTool(),
            RestDayCheckerTool(),
            *_search_tools,
        ],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )