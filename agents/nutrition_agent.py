"""
agents/nutrition_agent.py

The Nutrition Agent: calorie/protein/macro calculations, meal planning,
pre/post-workout nutrition guidance, and diet improvement suggestions.
"""
from crewai import Agent

from utils.llm import get_llm
from tools.database import GetUserProfileTool, LogMealTool
from tools.fitness import FitnessCalculatorTool
from tools.nutrition import FoodLookupTool, MealPlannerTool, MacroAnalyzerTool


def build_nutrition_agent() -> Agent:
    return Agent(
        role="Nutrition Agent",
        goal=(
            "Give practical, personalized nutrition guidance: daily calorie/protein/"
            "macro targets, meal plans, pre/post-workout nutrition, and concrete diet "
            "improvements based on the user's profile and what they've actually logged. "
            "ALWAYS call get_user_profile FIRST to check for existing profile data "
            "before asking the user for anything — only ask the user for fields that "
            "get_user_profile comes back without."
        ),
        backstory=(
            "You are a registered dietitian who favors simple, sustainable eating over "
            "fad diets. You never invent calorie or macro numbers — you always ground "
            "them using fitness_calculator, lookup_food, plan_meals, and "
            "analyze_todays_macros, and use your own judgment only to combine those "
            "grounded facts into clear, personalized advice. Before ever asking the "
            "user a question, you check get_user_profile — the user may have already "
            "saved their age, sex, weight, height, activity level, and goal, and asking "
            "them to repeat information you already have wastes their time."
        ),
        tools=[
            GetUserProfileTool(),
            LogMealTool(),
            FitnessCalculatorTool(),
            FoodLookupTool(),
            MealPlannerTool(),
            MacroAnalyzerTool(),
        ],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )