import re
from collections import defaultdict

_sessions: dict[str, dict] = defaultdict(lambda: {"history": [], "preferences": {}})


def get_session(session_id: str) -> dict:
    return _sessions[session_id]


def update_memory(session_id: str, message: str) -> dict:
    session = get_session(session_id)
    session["history"].append(message)
    prefs = session["preferences"]
    text = message.lower()

    if "kid" in text or "child" in text or "family" in text:
        prefs["traveller_type"] = "family with children"
    if "culture" in text or "heritage" in text:
        prefs["interest"] = "culture and heritage"
    if "food" in text or "hawker" in text:
        prefs["food_interest"] = "local food and hawker centres"
    if "budget" in text or "cheap" in text:
        prefs["budget_style"] = "budget-conscious"
    if "luxury" in text:
        prefs["budget_style"] = "premium"
    if "indoor" in text:
        prefs["activity_preference"] = "indoor activities"
    if "outdoor" in text:
        prefs["activity_preference"] = "outdoor activities"

    days = re.search(r"(\d+)\s*[- ]?day", text)
    if days:
        prefs["trip_length_days"] = days.group(1)
    elif "three-day" in text or "three day" in text:
        prefs["trip_length_days"] = "3"

    return prefs


def memory_text(session_id: str) -> str:
    prefs = get_session(session_id)["preferences"]
    if not prefs:
        return "No explicit user preferences retained yet."
    return "\n".join(f"- {k}: {v}" for k, v in prefs.items())
