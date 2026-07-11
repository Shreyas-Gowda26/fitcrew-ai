"""
tools/recovery/injury_prevention_tools.py

InjuryPreventionTool -> curated, grounded injury-prevention tips per body
area/exercise type, so the agent doesn't invent medical-sounding advice.
"""
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

PREVENTION_TIPS = {
    "shoulders": [
        "Warm up with band pull-aparts and shoulder dislocates before pressing",
        "Avoid flaring elbows past 90 degrees on bench press",
        "Balance pushing volume with equal or greater pulling volume",
    ],
    "lower_back": [
        "Brace your core before every hinge/squat rep",
        "Avoid rounding the lower back under load (deadlifts, rows)",
        "Progress load gradually — don't jump more than ~10% week to week",
    ],
    "knees": [
        "Track knees in line with toes during squats/lunges",
        "Avoid locking out knees aggressively under heavy load",
        "Build quad and glute strength evenly to support the joint",
    ],
    "elbows": [
        "Avoid excessive volume of straight-bar curls if elbows are sensitive; try EZ-bar or neutral grip",
        "Warm up wrists/forearms before heavy pressing or pulling",
    ],
    "ankles": [
        "Include calf raises and ankle mobility work if doing running/jumping (e.g. cricket sprints)",
        "Avoid sudden increases in sprint/plyometric volume",
    ],
    "cricket_specific": [
        "Warm up rotational muscles before bowling/batting practice (torso twists, band rotations)",
        "Build up bowling workload gradually across a season, not in sudden spikes",
        "Include unilateral leg strength work to support lateral movement and sprinting",
    ],
}


class InjuryPreventionInput(BaseModel):
    body_area: str = Field(
        ..., description=f"One of: {list(PREVENTION_TIPS.keys())}"
    )


class InjuryPreventionTool(BaseTool):
    name: str = "get_injury_prevention_tips"
    description: str = (
        "Get grounded, general injury-prevention tips for a body area or "
        "cricket-specific training. Not a substitute for medical advice — always "
        "note that for actual pain/injury the user should see a professional."
    )
    args_schema: Type[BaseModel] = InjuryPreventionInput

    def _run(self, body_area: str) -> str:
        key = body_area.lower().strip().replace(" ", "_")
        if key not in PREVENTION_TIPS:
            return f"No tips for '{body_area}'. Known areas: {list(PREVENTION_TIPS.keys())}"
        tips = "\n".join(f"  - {t}" for t in PREVENTION_TIPS[key])
        return f"General tips for {key} (not medical advice):\n{tips}"