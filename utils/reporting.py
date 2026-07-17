"""
utils/reporting.py

Builds, prints, and persists the per-query "Execution Report" described in
the original spec (timestamp, query, tools used, execution time, final
response), and logs the query/response pair to the chat_history collection.

Kept deliberately separate from report_tracker.py: the tracker collects raw
data during the crew run, this module turns that into the user-facing report
and writes it to Mongo.
"""
from datetime import datetime, timezone
from typing import Optional

from config.settings import settings
from database.connection import get_db
from database.collections import REPORTS, CHAT_HISTORY


def build_report(
    query: str,
    response: str,
    tracker,
    started_at: datetime,
    elapsed_seconds: float,
) -> dict:
    return {
        "user_id": settings.DEFAULT_USER_ID,
        "timestamp": started_at,
        "user_query": query,
        "agents_executed": tracker.agents_seen or ["not exposed by this CrewAI version"],
        "tools_used": tracker.tools_used,
        "tool_call_count": len(tracker.tool_calls),
        "execution_time_sec": round(elapsed_seconds, 2),
        "final_response": response,
    }


def print_report(report: dict) -> None:
    print("\n" + "-" * 40)
    print("Execution Report")
    print("-" * 40)
    print(f"Timestamp:      {report['timestamp'].strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Query:          {report['user_query']}")
    print(f"Agents:         {', '.join(report['agents_executed'])}")
    print(f"Tools Used:     {', '.join(report['tools_used']) or 'none'}")
    print(f"Tool Calls:     {report['tool_call_count']}")
    print(f"Execution Time: {report['execution_time_sec']}s")
    print("-" * 40)


def save_report(report: dict) -> None:
    """Persist the report. Never let a reporting failure break the CLI flow."""
    try:
        db = get_db()
        db[REPORTS].insert_one(report)
    except Exception as e:
        print(f"(note: couldn't save execution report: {e})")


def save_chat_history(query: str, response: str, started_at: Optional[datetime] = None) -> None:
    """Persist the query/response pair. Never let this break the CLI flow."""
    try:
        db = get_db()
        db[CHAT_HISTORY].insert_one(
            {
                "user_id": settings.DEFAULT_USER_ID,
                "timestamp": started_at or datetime.now(timezone.utc),
                "query": query,
                "response": response,
            }
        )
    except Exception as e:
        print(f"(note: couldn't save chat history: {e})")