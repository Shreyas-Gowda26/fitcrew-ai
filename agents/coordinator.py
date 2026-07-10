"""
agents/coordinator.py

The Coordinator Agent: the only agent that talks to the user directly.
It reads the user's request, decides which specialist agent(s) are needed,
delegates the work, and merges the results into one coherent answer.

Implementation note: this agent is used as the `manager_agent` of a
Process.hierarchical Crew (see crews/fitness_crew.py). CrewAI's hierarchical
manager already gets an implicit "delegate work to coworker" / "ask
question to coworker" tool at runtime, so we deliberately give the
Coordinator no extra tools of its own — its job is orchestration, not
doing the specialist work itself.
"""
from crewai import Agent

from utils.llm import get_llm


def build_coordinator() -> Agent:
    return Agent(
        role="Coordinator",
        goal=(
            "Understand what the user actually needs, delegate to the right "
            "specialist agent(s) (Workout, Nutrition, Recovery, Progress Analyst — "
            "whichever are available and relevant), and merge their responses into "
            "a single, clear, well-organized final answer for the user."
        ),
        backstory=(
            "You are the front-of-house coach who never guesses at workout, "
            "nutrition, recovery, or progress specifics yourself — you always route "
            "those questions to the right specialist and synthesize their answers. "
            "You keep the final response focused and free of internal jargon like "
            "tool names or delegation mechanics; the user should just see one "
            "coherent, helpful answer."
        ),
        llm=get_llm(temperature=0.3),
        verbose=True,
        allow_delegation=True,
    )