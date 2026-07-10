"""
tools/database/user_tools.py

GetUserProfileTool  -> read the user's profile
UpdateUserProfileTool -> partial update (upsert) of the user's profile
"""
from datetime import datetime, timezone
from typing import Type, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from config.settings import settings
from database.connection import get_db
from database.collections import USERS

VALID_ACTIVITY_LEVELS = ["sedentary", "light", "moderate", "active", "very_active"]
VALID_GOALS = ["lose_weight", "maintain", "gain_muscle"]
VALID_EXPERIENCE = ["beginner", "intermediate", "advanced"]


# ---------------------------------------------------------------------
class GetUserProfileInput(BaseModel):
    pass  # single-user app for now, no args needed


class GetUserProfileTool(BaseTool):
    name: str = "get_user_profile"
    description: str = (
        "Fetch the user's fitness profile: name, age, sex, height, weight, "
        "activity level, goal, experience level, sport (if any), dietary "
        "restrictions, and available equipment. Call this before generating "
        "any workout or nutrition plan."
    )
    args_schema: Type[BaseModel] = GetUserProfileInput

    def _run(self) -> str:
        db = get_db()
        profile = db[USERS].find_one({"user_id": settings.DEFAULT_USER_ID}, {"_id": 0})
        if not profile:
            return (
                "No profile found yet. Use update_user_profile (or CLI option "
                "'Update Profile') to create one first."
            )
        return str(profile)


# ---------------------------------------------------------------------
class UpdateUserProfileInput(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = Field(None, description="'male' or 'female'")
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = Field(
        None, description=f"One of: {VALID_ACTIVITY_LEVELS}"
    )
    goal: Optional[str] = Field(None, description=f"One of: {VALID_GOALS}")
    experience_level: Optional[str] = Field(
        None, description=f"One of: {VALID_EXPERIENCE}"
    )
    sport: Optional[str] = Field(
        None, description="Sport the user trains for, e.g. 'cricket' (optional)"
    )
    dietary_restrictions: Optional[str] = None
    equipment_available: Optional[str] = None


class UpdateUserProfileTool(BaseTool):
    name: str = "update_user_profile"
    description: str = (
        "Create or partially update the user's fitness profile. Only pass the "
        "fields that are changing; existing fields are preserved."
    )
    args_schema: Type[BaseModel] = UpdateUserProfileInput

    def _run(self, **kwargs) -> str:
        # Drop unset (None) fields so we only ever write what changed
        updates = {k: v for k, v in kwargs.items() if v is not None}

        if "activity_level" in updates and updates["activity_level"] not in VALID_ACTIVITY_LEVELS:
            return f"Invalid activity_level. Choose from: {VALID_ACTIVITY_LEVELS}"
        if "goal" in updates and updates["goal"] not in VALID_GOALS:
            return f"Invalid goal. Choose from: {VALID_GOALS}"
        if "experience_level" in updates and updates["experience_level"] not in VALID_EXPERIENCE:
            return f"Invalid experience_level. Choose from: {VALID_EXPERIENCE}"

        if not updates:
            return "No fields provided to update."

        updates["updated_at"] = datetime.now(timezone.utc)

        db = get_db()
        db[USERS].update_one(
            {"user_id": settings.DEFAULT_USER_ID},
            {
                "$set": updates,
                "$setOnInsert": {
                    "user_id": settings.DEFAULT_USER_ID,
                    "created_at": datetime.now(timezone.utc),
                },
            },
            upsert=True,
        )
        return f"Profile updated: {list(updates.keys())}"