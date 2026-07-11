"""
agents/recovery_agent.py

The Recovery Agent: sleep analysis, recovery scoring, hydration guidance,
fatigue analysis, rest day recommendations, and injury prevention.
"""
from crewai import Agent

from utils.llm import get_llm
from tools.database import (
    GetUserProfileTool,
    DailySummaryTool,
    LogSleepTool,
    LogWaterTool,
    WorkoutHistoryTool,
)
from tools.fitness import FitnessCalculatorTool
from tools.workout import RestDayCheckerTool
from tools.recovery import RecoveryScoreTool, FatigueAnalysisTool, InjuryPreventionTool


def build_recovery_agent() -> Agent:
    return Agent(
        role="Recovery Agent",
        goal=(
            "Help the user recover well: assess sleep and hydration, compute a "
            "recovery score, flag fatigue/overtraining risk, recommend rest days, "
            "and give general injury-prevention guidance."
        ),
        backstory=(
            "You are a sports science-minded recovery coach. You never diagnose "
            "injuries or give medical advice — for actual pain or injury you always "
            "recommend seeing a professional. You ground every assessment in the "
            "tools available (get_recovery_score, analyze_fatigue_risk, "
            "check_rest_day_needed, fitness_calculator's water operation, "
            "get_injury_prevention_tips) rather than guessing."
        ),
        tools=[
            GetUserProfileTool(),
            DailySummaryTool(),
            LogSleepTool(),
            LogWaterTool(),
            WorkoutHistoryTool(),
            FitnessCalculatorTool(),
            RestDayCheckerTool(),
            RecoveryScoreTool(),
            FatigueAnalysisTool(),
            InjuryPreventionTool(),
        ],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )