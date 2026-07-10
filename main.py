"""
FitCrew AI — CLI entry point.

Phase 3 status: options 1 (Workout Recommendation) and 7 (Ask AI) are live,
routed through the Coordinator -> Workout Agent crew. Nutrition (2),
Recovery (3), and Progress Report (4) are placeholders until their agents
exist (Phases 4-6).
"""
from config.settings import settings
from database.connection import ping
from tools.database import GetUserProfileTool, UpdateUserProfileTool, DailySummaryTool
from crews.fitness_crew import build_fitness_crew

VALID_ACTIVITY_LEVELS = ["sedentary", "light", "moderate", "active", "very_active"]
VALID_GOALS = ["lose_weight", "maintain", "gain_muscle"]
VALID_EXPERIENCE = ["beginner", "intermediate", "advanced"]


def get_profile_name() -> str:
    from database.connection import get_db
    from database.collections import USERS

    profile = get_db()[USERS].find_one({"user_id": settings.DEFAULT_USER_ID}, {"_id": 0})
    return profile.get("name", "there") if profile else "there"


def print_header():
    print("=" * 40)
    print("🏋️  FitCrew AI")
    print("=" * 40)
    print(f"\nHello {get_profile_name()} 👋\n")
    print("Today's Summary\n")
    print(DailySummaryTool()._run())
    print("-" * 40)


def print_menu():
    print("""
1. Workout Recommendation
2. Nutrition Advice          (coming in Phase 4)
3. Recovery Analysis         (coming in Phase 5)
4. Progress Report           (coming in Phase 6)
5. Daily Summary
6. Update Profile
7. Ask AI
8. Exit
""")


def run_crew(query: str):
    print("\n(thinking... this calls Gemini + your tools, may take a moment)\n")
    crew = build_fitness_crew(query)
    result = crew.kickoff()
    print("\n" + "=" * 40)
    print(result)
    print("=" * 40 + "\n")


def handle_workout_recommendation():
    query = input(
        "What kind of workout do you want today? (or press Enter for 'recommend today's workout'): "
    ).strip()
    if not query:
        query = "Recommend today's workout for me based on my profile and recent history."
    run_crew(query)


def handle_ask_ai():
    query = input("Ask me anything fitness-related: ").strip()
    if query:
        run_crew(query)


def handle_daily_summary():
    print("\n" + DailySummaryTool()._run())


def handle_update_profile():
    print("\nLeave a field blank to keep it unchanged.\n")
    fields = {}

    name = input("Name: ").strip()
    if name:
        fields["name"] = name

    age = input("Age: ").strip()
    if age:
        fields["age"] = int(age)

    sex = input("Sex (male/female): ").strip().lower()
    if sex:
        fields["sex"] = sex

    height = input("Height (cm): ").strip()
    if height:
        fields["height_cm"] = float(height)

    weight = input("Weight (kg): ").strip()
    if weight:
        fields["weight_kg"] = float(weight)

    activity = input(f"Activity level {VALID_ACTIVITY_LEVELS}: ").strip().lower()
    if activity:
        fields["activity_level"] = activity

    goal = input(f"Goal {VALID_GOALS}: ").strip().lower()
    if goal:
        fields["goal"] = goal

    experience = input(f"Experience level {VALID_EXPERIENCE}: ").strip().lower()
    if experience:
        fields["experience_level"] = experience

    sport = input("Sport you train for, if any (e.g. cricket): ").strip()
    if sport:
        fields["sport"] = sport

    equipment = input("Equipment available (bodyweight/dumbbell/gym): ").strip().lower()
    if equipment:
        fields["equipment_available"] = equipment

    result = UpdateUserProfileTool()._run(**fields)
    print(f"\n{result}\n")


def main():
    settings.validate()
    if not ping():
        print("⚠️  Could not connect to MongoDB. Check MONGO_URI in your .env file.")
        return

    while True:
        print_header()
        print_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            handle_workout_recommendation()
        elif choice == "2":
            print("\nNutrition Advice is coming in Phase 4.\n")
        elif choice == "3":
            print("\nRecovery Analysis is coming in Phase 5.\n")
        elif choice == "4":
            print("\nProgress Report is coming in Phase 6.\n")
        elif choice == "5":
            handle_daily_summary()
        elif choice == "6":
            handle_update_profile()
        elif choice == "7":
            handle_ask_ai()
        elif choice == "8":
            print("\nSee you next time! 👋")
            break
        else:
            print("\nInvalid option, try again.\n")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
