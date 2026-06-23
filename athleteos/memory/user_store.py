import json
import os
from datetime import date

PROFILES_DIR = "./memory/profiles"


def get_profile(user_name: str = "default_user") -> dict:
    path = os.path.join(PROFILES_DIR, f"{user_name}.json")
    if not os.path.exists(path):
        return create_default_profile(user_name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def update_profile(user_name: str, updates: dict):
    path = os.path.join(PROFILES_DIR, f"{user_name}.json")
    profile = get_profile(user_name)
    profile.update(updates)
    profile["last_updated"] = str(date.today())
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)


def log_session(user_name: str, session_summary: str):
    profile = get_profile(user_name)
    if "session_history" not in profile:
        profile["session_history"] = []
    profile["session_history"].append(
        {"date": str(date.today()), "summary": session_summary[:200]}
    )
    profile["total_sessions"] = len(profile["session_history"])
    update_profile(user_name, profile)


def create_default_profile(user_name: str) -> dict:
    profile = {
        "user_name": user_name,
        "total_sessions": 0,
        "current_streak": 0,
        "last_updated": str(date.today()),
        "session_history": [],
        "plateau_flagged": False,
    }
    os.makedirs(PROFILES_DIR, exist_ok=True)
    path = os.path.join(PROFILES_DIR, f"{user_name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
    return profile
