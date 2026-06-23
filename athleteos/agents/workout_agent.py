from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from config import GROQ_API_KEY, MODEL_NAME
from graph.state import AgentState

llm = ChatGroq(api_key=GROQ_API_KEY, model=MODEL_NAME)

WORKOUT_SYSTEM = """You are an elite strength and conditioning coach. Design evidence-based training sessions.

Always output in this exact format:
SESSION TYPE: [e.g. Upper Body Hypertrophy | Full Body Strength | HIIT Cardio]
DURATION: [X] minutes
INTENSITY: [Low/Medium/High]

WARMUP (10 min):
- [exercise] x [sets/reps/duration]

MAIN WORKOUT:
- [exercise] — [sets] x [reps] @ [RPE or %1RM hint]

COOLDOWN (5 min):
- [stretches]

COACH NOTES: [1-2 notes specific to this user's goal and level]

Be specific. Match exercises to fitness level. If time is short, cut volume not intensity."""


def workout_node(state: AgentState) -> AgentState:
    soreness = ", ".join(state["soreness_areas"]) if state["soreness_areas"] else "None"
    prompt = f"""
Design today's training session for:
- Goal: {state['goal']}
- Fitness level: {state['fitness_level']}
- Available time: {state['available_minutes']} minutes
- Soreness areas: {soreness}
- Sleep last night: {state['sleep_hours']} hours
- Training days per week: {state['training_days']}

Note: If soreness is reported in specific areas, avoid direct loading of those areas.
"""
    response = llm.invoke(
        [SystemMessage(content=WORKOUT_SYSTEM), HumanMessage(content=prompt)]
    )
    state["workout_plan"] = response.content
    return state
