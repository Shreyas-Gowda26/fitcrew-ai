# FitCrew AI

A personal AI fitness & sports performance coach built with CrewAI, Gemini, and MongoDB Atlas.
CLI-only (no frontend) — see `AI Architecture` doc for full design.

## Status: Phase 1 — Project Setup

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# then edit .env and fill in GEMINI_API_KEY and MONGO_URI

# 4. Verify the setup
python main.py
```

You should see:
```
========================================
FitCrew AI — Phase 1 setup check
========================================
Checking MongoDB Atlas connection... OK ✔
Checking Gemini connection... OK ✔ (model replied: 'OK')
========================================
Phase 1 complete. Ready for Phase 2 (User profile + DB tools).
```

### Getting a Gemini API key
https://aistudio.google.com/apikey

### Getting a MongoDB Atlas connection string
Atlas dashboard → Database → Connect → Drivers → Python → copy the URI
(remember to add your current IP to the Atlas Network Access allow-list).

## Folder structure

```
fitcrew-ai/
├── agents/          # CrewAI Agent definitions (Coordinator, Workout, Nutrition, Recovery, Progress)
├── crews/            # Crew assembly (agents + tasks + process)
├── tasks/            # CrewAI Task definitions
├── tools/
│   ├── database/     # GetUserProfileTool, LogWorkoutTool, etc.
│   ├── fitness/       # BMICalculatorTool, BMRCalculatorTool, etc.
│   ├── nutrition/     # MealPlannerTool, MacroAnalyzerTool, etc.
│   ├── workout/       # WorkoutGeneratorTool, ExerciseRecommendationTool, etc.
│   └── progress/      # WeeklyReportTool, WeightTrendTool, etc.
├── database/          # Mongo connection + collection constants
├── prompts/           # Reusable prompt/backstory text, if split out later
├── reports/           # Generated execution reports
├── utils/             # Shared helpers (LLM instance, formatting, etc.)
├── config/            # Centralized settings loader
├── main.py            # Entry point / CLI
└── requirements.txt
```

## Roadmap
- [x] Phase 1 — Project setup, Gemini + Mongo connections
- [ ] Phase 2 — User profile, Mongo CRUD, database tools
- [ ] Phase 3 — Coordinator Agent, Workout Agent
- [ ] Phase 4 — Nutrition Agent
- [ ] Phase 5 — Recovery Agent
- [ ] Phase 6 — Progress Analyst
- [ ] Phase 7 — Agent delegation, execution reports, CLI polish
