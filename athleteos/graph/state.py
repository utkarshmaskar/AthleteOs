from typing import Annotated, List, Optional, TypedDict
import operator

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

    # User inputs
    user_name: str
    age: int
    weight_kg: float
    goal: str
    fitness_level: str
    training_days: int
    sleep_hours: float
    soreness_areas: List[str]
    available_minutes: int

    # Sub-agent outputs
    nutrition_plan: Optional[str]
    workout_plan: Optional[str]
    recovery_plan: Optional[str]
    progress_summary: Optional[str]

    # Conflict tracking
    conflicts_detected: List[str]
    conflicts_resolved: List[str]

    # Final output
    final_plan: Optional[str]
    orchestrator_notes: Optional[str]
