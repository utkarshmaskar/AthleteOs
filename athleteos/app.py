import streamlit as st

from graph.graph import build_graph
from memory.user_store import log_session


def _default_state() -> dict:
    return {
        "messages": [],
        "user_name": "default_user",
        "age": 27,
        "weight_kg": 72.0,
        "goal": "build_muscle",
        "fitness_level": "intermediate",
        "training_days": 4,
        "sleep_hours": 7.0,
        "soreness_areas": [],
        "available_minutes": 60,
        "nutrition_plan": None,
        "workout_plan": None,
        "recovery_plan": None,
        "progress_summary": None,
        "conflicts_detected": [],
        "conflicts_resolved": [],
        "final_plan": None,
        "orchestrator_notes": None,
    }


st.set_page_config(page_title="AthleteOS", page_icon="🏋️", layout="wide")
st.title("AthleteOS: Multi-Agent Health Coaching System")
st.caption("Nutrition + Workout + Recovery + Progress agents orchestrated into one plan.")

with st.sidebar:
    st.header("User Inputs")
    user_name = st.text_input("User Name", "default_user")
    age = st.number_input("Age", min_value=16, max_value=80, value=27)
    weight_kg = st.number_input("Weight (kg)", min_value=35.0, max_value=180.0, value=72.0)
    goal = st.selectbox("Goal", ["lose_fat", "build_muscle", "maintain"], index=1)
    fitness_level = st.selectbox(
        "Fitness Level", ["beginner", "intermediate", "advanced"], index=1
    )
    training_days = st.slider("Training days/week", min_value=1, max_value=7, value=4)
    sleep_hours = st.slider("Sleep last night (hours)", min_value=3.0, max_value=10.0, value=7.0)
    available_minutes = st.slider("Available training time (minutes)", 20, 120, 60)
    soreness_raw = st.text_input(
        "Soreness areas (comma-separated)", "legs"
    )
    run = st.button("Generate Daily Plan", type="primary")


if run:
    soreness_areas = [s.strip() for s in soreness_raw.split(",") if s.strip()]
    state = _default_state()
    state.update(
        {
            "user_name": user_name,
            "age": int(age),
            "weight_kg": float(weight_kg),
            "goal": goal,
            "fitness_level": fitness_level,
            "training_days": int(training_days),
            "sleep_hours": float(sleep_hours),
            "available_minutes": int(available_minutes),
            "soreness_areas": soreness_areas,
        }
    )

    app_graph = build_graph()
    result = app_graph.invoke(state)

    st.subheader("Final Unified Plan")
    st.text(result.get("final_plan", "No output generated"))

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Conflict Detection")
        if result.get("conflicts_detected"):
            for item in result["conflicts_detected"]:
                st.error(item)
        else:
            st.success("No conflicts detected.")

    with c2:
        st.subheader("Conflict Resolution")
        if result.get("conflicts_resolved"):
            for item in result["conflicts_resolved"]:
                st.info(item)
        else:
            st.success("No plan overrides were needed.")

    st.subheader("Orchestrator Notes")
    st.code(result.get("orchestrator_notes", "No notes"), language="text")

    with st.expander("Raw Sub-Agent Outputs", expanded=False):
        st.markdown("**Nutrition Agent**")
        st.code(result.get("nutrition_plan", "N/A"), language="text")
        st.markdown("**Workout Agent**")
        st.code(result.get("workout_plan", "N/A"), language="text")
        st.markdown("**Recovery Agent**")
        st.code(result.get("recovery_plan", "N/A"), language="text")
        st.markdown("**Progress Agent**")
        st.code(result.get("progress_summary", "N/A"), language="text")

    log_session(user_name, result.get("final_plan", "No plan generated"))
