"""
utils/report_tracker.py

Lightweight tracker used to build the "Execution Report" the CLI prints
after each crew run, and to persist it to the `reports` collection.

Hooked in via CrewAI's Crew-level `step_callback`, which fires after every
agent step (tool call or final answer). NOTE: the exact shape of the "step"
object has shifted across CrewAI versions in our own testing (see the
agent_executor/flow_runtime internals we've hit in tracebacks), so this
reads fields defensively with getattr(...) rather than assuming a fixed
schema. If a field isn't present, we just skip that detail instead of
crashing the whole crew run over a reporting feature.
"""
from datetime import datetime, timezone


class ExecutionTracker:
    def __init__(self):
        self.reset()

    def reset(self):
        self.tool_calls: list[str] = []   # every tool call, in order (may repeat)
        self.tools_used: list[str] = []   # deduped, in first-seen order
        self.agents_seen: list[str] = []  # deduped agent roles, if the step exposes one
        self.steps_seen = 0

    def step_callback(self, step) -> None:
        """Passed to Crew(step_callback=...). Called after every agent step."""
        self.steps_seen += 1

        tool_name = getattr(step, "tool", None)
        if tool_name:
            self.tool_calls.append(tool_name)
            if tool_name not in self.tools_used:
                self.tools_used.append(tool_name)

        # Not all CrewAI versions expose the acting agent on the step object;
        # only record it if present, otherwise leave agents_seen empty rather
        # than guessing.
        agent_role = getattr(step, "agent", None)
        if agent_role and agent_role not in self.agents_seen:
            self.agents_seen.append(str(agent_role))