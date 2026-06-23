"""
AthleteOS API

FastAPI wrapper around the existing LangGraph multi-agent pipeline
(nutrition -> workout -> recovery -> progress -> orchestrator).

This is the ONLY new backend file. It does not change any agent logic —
it just gives the existing graph/build_graph() pipeline an HTTP interface
so a frontend (built separately) can call it.

Run locally:
    uvicorn main:app --reload --port 8000

Endpoints:
    GET  /api/health
    POST /api/plan
    GET  /api/profile/{user_name}
"""

import os
from typing import List, Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Load .env so GROQ_API_KEY / TAVILY_API_KEY are available when running locally
load_dotenv()

from graph.graph import build_graph
from memory.user_store import get_profile, log_session

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AthleteOS API",
    description=(
        "Multi-agent health coaching system (Nutrition + Workout + Recovery + Progress, "
        "orchestrated with conflict detection/resolution)."
    ),
    version="1.0.0",
)

# Configure allowed frontend origin(s) via env var, e.g.:
#   ALLOWED_ORIGINS=https://athleteos-frontend.onrender.com,http://localhost:5173
_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
_allow_origins = (
    ["*"]
    if _origins_env.strip() == "*"
    else [o.strip() for o in _origins_env.split(",") if o.strip()]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Build the LangGraph pipeline once at startup and reuse it for every request.
_graph = build_graph()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class PlanRequest(BaseModel):
    user_name: str = Field(default="default_user", min_length=1, max_length=64)
    age: int = Field(ge=16, le=80)
    weight_kg: float = Field(ge=35, le=180)
    goal: Literal["lose_fat", "build_muscle", "maintain"]
    fitness_level: Literal["beginner", "intermediate", "advanced"]
    training_days: int = Field(ge=1, le=7)
    sleep_hours: float = Field(ge=0, le=14)
    available_minutes: int = Field(ge=10, le=180)
    soreness_areas: List[str] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_name": "alex",
                "age": 27,
                "weight_kg": 72.0,
                "goal": "build_muscle",
                "fitness_level": "intermediate",
                "training_days": 4,
                "sleep_hours": 7.0,
                "available_minutes": 60,
                "soreness_areas": ["legs"],
            }
        }
    }


class PlanResponse(BaseModel):
    final_plan: Optional[str] = None
    orchestrator_notes: Optional[str] = None
    conflicts_detected: List[str] = []
    conflicts_resolved: List[str] = []
    nutrition_plan: Optional[str] = None
    workout_plan: Optional[str] = None
    recovery_plan: Optional[str] = None
    progress_summary: Optional[str] = None


class ProfileResponse(BaseModel):
    user_name: str
    total_sessions: int = 0
    current_streak: int = 0
    last_updated: Optional[str] = None
    plateau_flagged: bool = False
    session_history: List[dict] = []


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/api/health", tags=["system"])
def health() -> dict:
    """Lightweight check the frontend/host can poll. Also flags missing API keys."""
    missing = [k for k in ("GROQ_API_KEY", "TAVILY_API_KEY") if not os.getenv(k)]
    return {"status": "ok", "missing_env_vars": missing}


@app.post("/api/plan", response_model=PlanResponse, tags=["agent"])
def generate_plan(payload: PlanRequest) -> PlanResponse:
    """Run the full agent pipeline and return the unified daily plan."""
    state = {
        "messages": [],
        "user_name": payload.user_name,
        "age": payload.age,
        "weight_kg": payload.weight_kg,
        "goal": payload.goal,
        "fitness_level": payload.fitness_level,
        "training_days": payload.training_days,
        "sleep_hours": payload.sleep_hours,
        "soreness_areas": payload.soreness_areas,
        "available_minutes": payload.available_minutes,
        "nutrition_plan": None,
        "workout_plan": None,
        "recovery_plan": None,
        "progress_summary": None,
        "conflicts_detected": [],
        "conflicts_resolved": [],
        "final_plan": None,
        "orchestrator_notes": None,
    }

    try:
        result = _graph.invoke(state)
    except Exception as exc:  # surface a clean error instead of a raw 500 trace
        raise HTTPException(
            status_code=502,
            detail=f"Agent pipeline failed: {exc}",
        ) from exc

    log_session(payload.user_name, result.get("final_plan", "No plan generated"))

    return PlanResponse(
        final_plan=result.get("final_plan"),
        orchestrator_notes=result.get("orchestrator_notes"),
        conflicts_detected=result.get("conflicts_detected", []),
        conflicts_resolved=result.get("conflicts_resolved", []),
        nutrition_plan=result.get("nutrition_plan"),
        workout_plan=result.get("workout_plan"),
        recovery_plan=result.get("recovery_plan"),
        progress_summary=result.get("progress_summary"),
    )


@app.get("/api/profile/{user_name}", response_model=ProfileResponse, tags=["profile"])
def profile(user_name: str) -> ProfileResponse:
    """Return a user's stored progress profile (session history, streak, etc.)."""
    data = get_profile(user_name)
    return ProfileResponse(
        user_name=data.get("user_name", user_name),
        total_sessions=data.get("total_sessions", 0),
        current_streak=data.get("current_streak", 0),
        last_updated=data.get("last_updated"),
        plateau_flagged=data.get("plateau_flagged", False),
        session_history=data.get("session_history", []),
    )
