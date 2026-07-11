"""
crews/fitness_crew.py

Assembles the crew: Coordinator as the hierarchical manager, delegating to
whichever specialist agents exist so far. Right now that's just the
Workout Agent (Phase 3) — Nutrition/Recovery/Progress Analyst get added to
the `agents=[...]` list in later phases, and the Coordinator will start
routing to them automatically without any other changes needed here.
"""
from crewai import Crew, Process, Task

from agents.coordinator import build_coordinator
from agents.workout_agent import build_workout_agent
from agents.nutrition_agent import build_nutrition_agent
from agents.recovery_agent import build_recovery_agent


def build_fitness_crew(user_query: str) -> Crew:
    coordinator = build_coordinator()
    workout_agent = build_workout_agent()
    nutrition_agent = build_nutrition_agent()
    recovery_agent = build_recovery_agent()

    task = Task(
        description=(
            f"User request: \"{user_query}\"\n\n"
            "Figure out what the user needs and delegate to the right specialist "
            "agent(s). Combine their output into one clear, well-formatted, "
            "final response addressed directly to the user."
        ),
        expected_output=(
            "A single, coherent, helpful response that fully addresses the "
            "user's request, with no mention of internal tools, agents, or "
            "delegation mechanics."
        ),
    )

    return Crew(
        agents=[workout_agent, nutrition_agent, recovery_agent],  # add progress_agent here later
        tasks=[task],
        process=Process.hierarchical,
        manager_agent=coordinator,
        verbose=True,
    )