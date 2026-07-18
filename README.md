# FitCrew AI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A personal AI fitness & sports performance coach — a multi-agent system built with
**CrewAI**, an LLM of your choice (Gemini / OpenAI / OpenRouter), and **MongoDB Atlas**
for persistence. CLI-only, no frontend by design.

A single **Coordinator** agent talks to the user and delegates to four specialists —
**Workout**, **Nutrition**, **Recovery**, and **Progress Analyst** — each backed by
custom, deterministic tools so numbers (calories, macros, BMI, recovery scores, etc.)
come from real calculations and real logged data, not LLM guesswork.

## Status: All 7 phases complete ✅

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# then edit .env — see "Choosing an LLM provider" below, and add MONGO_URI

# 4. Run it
python main.py
```

### Getting a MongoDB Atlas connection string
Atlas dashboard → Database → Connect → Drivers → Python → copy the URI
(remember to add your current IP to the Atlas Network Access allow-list).

## Choosing an LLM provider

The app is provider-agnostic — set `GEMINI_MODEL` in `.env` to any of these
(despite the variable name, it accepts any CrewAI/LiteLLM model string) and
add the matching API key. No code changes needed either way.

| Provider | `.env` setting | Key needed |
|---|---|---|
| Gemini | `GEMINI_MODEL=gemini/gemini-2.5-flash` | `GEMINI_API_KEY` ([aistudio.google.com/apikey](https://aistudio.google.com/apikey)) |
| OpenAI | `GEMINI_MODEL=openai/gpt-4o-mini` | `OPENAI_API_KEY` |
| OpenRouter | `GEMINI_MODEL=openrouter/<provider>/<model>` | `OPENROUTER_API_KEY` ([openrouter.ai](https://openrouter.ai)) |

**Note on free tiers:** in practice, free-tier models (Gemini free tier, and
OpenRouter's `:free` models) hit rate limits, provider outages, or quota
exhaustion fairly often under real use — you'll likely see occasional
503/429/402 errors that are unrelated to this codebase. A paid key (even a
few dollars of OpenAI credit) removes this class of problem entirely.

Optional: set `SERPER_API_KEY` (get one free at [serper.dev](https://serper.dev)) to give the
Workout Agent live web search for things its curated tools don't cover.

## What it does

Run `python main.py` for an interactive menu:

1. **Workout Recommendation** — personalized plan grounded in a curated exercise
   bank, split/difficulty decision tables, and your logged training history
2. **Nutrition Advice** — calorie/macro targets (Mifflin-St Jeor + activity
   multiplier), meal ideas grounded in a food database, macro tracking against logged meals
3. **Recovery Analysis** — a 0–100 recovery score from sleep/hydration/training
   load, fatigue risk, rest-day recommendations, injury-prevention tips
4. **Progress Report** — weight trend & plateau detection, workout consistency,
   goal-progress tracking (needs a few weeks of logged data to say anything meaningful)
5. **Daily Summary** — quick sleep/water/calories/workout status for today
6. **Update Profile** — age, sex, height, weight, activity level, goal, sport, equipment
7. **Ask AI** — open-ended question, routed to whichever specialist(s) fit
8. **Exit**

Every crew run also prints and persists an **Execution Report** (tools used,
call count, timing) to Mongo's `reports` collection, and logs the
query/response pair to `chat_history`.

## Folder structure

```
fitcrew-ai/
├── agents/            # Coordinator + Workout/Nutrition/Recovery/Progress agent definitions
├── crews/              # Crew assembly (hierarchical process, manager + specialists)
├── tasks/               # (reserved for standalone Task definitions)
├── tools/
│   ├── database/       # Profile, workout/meal/sleep/water logging & history, daily summary
│   ├── fitness/         # FitnessCalculatorTool (BMI/BMR/TDEE/protein/water/macros)
│   ├── nutrition/       # Food lookup, meal planning, macro analysis
│   ├── workout/         # Exercise recommendations, split/difficulty generators, rest-day check
│   └── progress/        # Weekly/monthly reports, weight trend, consistency, goal progress
├── database/            # Mongo connection, collection name constants, daily-log helpers
├── prompts/             # (reserved)
├── reports/             # (execution reports are stored in Mongo, not this folder)
├── utils/               # LLM factory (provider-agnostic), execution tracker, reporting
├── config/              # Centralized settings loader
├── main.py              # CLI entry point
└── requirements.txt
```

## Architecture notes

- **Hierarchical delegation**: the Coordinator is CrewAI's `manager_agent` in a
  `Process.hierarchical` crew. It has no tools of its own — its job is purely
  to route work to the right specialist(s) and merge their answers. CrewAI
  gives it an implicit delegate/ask-coworker tool at runtime.
- **Tools are deterministic where it matters**: calorie math, exercise lists,
  recovery scoring, etc. all live in plain Python, not LLM-generated text —
  agents call these tools instead of guessing numbers.
- **Agents check saved data before asking the user anything.** Every
  specialist is explicitly instructed to call `get_user_profile` /
  `get_workout_history` / etc. first, and the Coordinator is explicitly
  forbidden from fabricating data when a specialist reports something
  genuinely doesn't exist (e.g. "no meals logged yet") — it must relay that
  honestly rather than inventing plausible-looking history.
- **Single-user app** (`DEFAULT_USER_ID=me` in `.env`) — no auth, by design,
  per the V1 scope below.

## Roadmap
- [x] Phase 1 — Project setup, LLM + Mongo connections
- [x] Phase 2 — User profile, Mongo CRUD, database tools
- [x] Phase 3 — Coordinator Agent, Workout Agent
- [x] Phase 4 — Nutrition Agent
- [x] Phase 5 — Recovery Agent
- [x] Phase 6 — Progress Analyst
- [x] Phase 7 — Agent delegation, execution reports, CLI polish

## Future enhancements (out of scope for V1)
FastAPI backend, Streamlit/React frontend, voice interaction, food image
recognition, workout posture analysis, Google Calendar / Fit / Apple Health
integration, PDF report generation, notifications, MCP integration,
authentication and multi-user support.
