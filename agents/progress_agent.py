"""
agents/progress_agent.py

The Progress Analyst: weekly/monthly reports, plateau detection,
consistency analysis, weight trend tracking, and goal progress.
"""
from crewai import Agent

from utils.llm import get_llm
from tools.database import GetUserProfileTool, WorkoutHistoryTool, SaveProgressTool
from tools.progress import (
    WeeklyReportTool,
    WeightTrendTool,
    ConsistencyAnalyzerTool,
    GoalProgressTool,
)


def build_progress_agent() -> Agent:
    return Agent(
        role="Progress Analyst",
        goal=(
            "Give the user an honest, data-grounded picture of their progress: "
            "weekly/monthly activity reports, weight trend and plateau detection, "
            "workout consistency, and how their actual progress compares to their "
            "stated goal."
        ),
        backstory=(
            "You are a data-driven coach who looks at trends over time rather than "
            "reacting to any single data point. You never invent progress or "
            "consistency numbers — you always ground them using get_period_report, "
            "get_weight_trend, analyze_consistency, and check_goal_progress. When "
            "there isn't enough logged data yet, you say so plainly instead of "
            "making up a trend, and you tell the user what to log to get a real "
            "answer next time. Before ever asking the user a question, you check "
            "get_user_profile and get_workout_history — the user may have already "
            "saved what you need."
        ),
        tools=[
            GetUserProfileTool(),
            WorkoutHistoryTool(),
            SaveProgressTool(),
            WeeklyReportTool(),
            WeightTrendTool(),
            ConsistencyAnalyzerTool(),
            GoalProgressTool(),
        ],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )