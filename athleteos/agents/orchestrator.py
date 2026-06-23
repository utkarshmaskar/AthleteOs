import re
from typing import List

from graph.state import AgentState


def _extract_field(text: str, key: str) -> str:
    pattern = rf"{re.escape(key)}\s*:\s*(.+)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _detect_conflicts(state: AgentState) -> List[str]:
    conflicts: List[str] = []
    recovery = state.get("recovery_plan") or ""
    workout = state.get("workout_plan") or ""

    fatigue = _extract_field(recovery, "FATIGUE LEVEL").lower()
    rec = _extract_field(recovery, "TRAINING RECOMMENDATION").upper()
    conflict_flag = _extract_field(recovery, "CONFLICT FLAG").upper()
    workout_text = workout.lower()

    lower_soreness = [s.lower() for s in state.get("soreness_areas", [])]
    heavy_lower_body_signal = any(
        token in workout_text
        for token in ["squat", "deadlift", "leg press", "lunge", "lower body", "leg day"]
    )
    leg_is_sore = "legs" in lower_soreness or "lower_back" in lower_soreness

    if conflict_flag == "YES":
        conflicts.append("Recovery agent explicitly flagged a workout conflict.")

    if fatigue in {"high", "critical"} and rec in {"MODIFY_WORKOUT", "REST_DAY"}:
        conflicts.append(
            f"Recovery agent marked fatigue as {fatigue.upper()} and requested {rec}."
        )

    if state.get("sleep_hours", 0) < 6 and "INTENSITY: HIGH" in workout.upper():
        conflicts.append("High-intensity workout proposed despite low sleep (<6h).")

    if leg_is_sore and heavy_lower_body_signal:
        conflicts.append("Workout heavily loads sore lower-body regions (legs/lower_back).")

    return conflicts


def _safe_workout_replacement(state: AgentState) -> str:
    duration = max(25, min(state.get("available_minutes", 45), 50))
    return f"""SESSION TYPE: Upper Body Recovery-Compatible Strength
DURATION: {duration} minutes
INTENSITY: Medium

WARMUP (10 min):
- Brisk walk x 5 min
- Shoulder circles + band pull-aparts x 2 sets

MAIN WORKOUT:
- Incline push-up or DB bench — 3 x 8-12 @ RPE 6-7
- Chest-supported row — 3 x 10-12 @ RPE 6-7
- Seated overhead press (light) — 3 x 8-10 @ RPE 6
- Pallof press + dead bug superset — 3 rounds

COOLDOWN (5 min):
- Thoracic rotation stretch
- Lat stretch + diaphragmatic breathing

COACH NOTES: Reduced lower-body loading due to fatigue/soreness risk while preserving training stimulus."""


def _build_final_plan(state: AgentState) -> str:
    conflict_block = (
        "\n".join(f"- {c}" for c in state["conflicts_detected"])
        if state["conflicts_detected"]
        else "- No actionable conflicts detected."
    )
    resolved_block = (
        "\n".join(f"- {c}" for c in state["conflicts_resolved"])
        if state["conflicts_resolved"]
        else "- No overrides required."
    )

    return f"""ATHLETEOS UNIFIED DAILY PLAN

USER: {state['user_name']} | Goal: {state['goal']} | Level: {state['fitness_level']}

=== CONFLICTS DETECTED ===
{conflict_block}

=== CONFLICTS RESOLVED ===
{resolved_block}

=== WORKOUT PLAN ===
{state.get('workout_plan', 'N/A')}

=== NUTRITION PLAN ===
{state.get('nutrition_plan', 'N/A')}

=== RECOVERY PLAN ===
{state.get('recovery_plan', 'N/A')}

=== PROGRESS ANALYSIS ===
{state.get('progress_summary', 'N/A')}
"""


def orchestrator_node(state: AgentState) -> AgentState:
    state["conflicts_detected"] = _detect_conflicts(state)
    state["conflicts_resolved"] = []

    if state["conflicts_detected"]:
        original = state.get("workout_plan", "")
        state["workout_plan"] = _safe_workout_replacement(state)
        state["conflicts_resolved"].append(
            "Workout plan overridden with a recovery-compatible upper-body session."
        )
        state["orchestrator_notes"] = (
            "Override applied because recovery/fatigue signals conflicted with training load.\n\n"
            f"Original workout proposal:\n{original}"
        )
    else:
        state["orchestrator_notes"] = "No override needed. Agent recommendations were compatible."

    state["final_plan"] = _build_final_plan(state)
    return state
