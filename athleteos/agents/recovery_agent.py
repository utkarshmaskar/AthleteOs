from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from config import GROQ_API_KEY, MODEL_NAME
from graph.state import AgentState

llm = ChatGroq(api_key=GROQ_API_KEY, model=MODEL_NAME)

RECOVERY_SYSTEM = """You are a sports physiotherapist and recovery specialist.

Always output in this exact format:
FATIGUE LEVEL: [Low/Medium/High/Critical]
TRAINING RECOMMENDATION: [TRAIN_NORMALLY | MODIFY_WORKOUT | REST_DAY]

RECOVERY PROTOCOL:
- Mobility work: [specific stretches for sore areas, duration]
- Sleep optimization: [specific advice]
- Nutrition for recovery: [specific foods/timing]
- Additional: [ice/heat/foam rolling recommendations]

CONFLICT FLAG: [YES/NO]
If YES, explain: [what the conflict is with the planned workout]

Be direct. If fatigue is High or Critical, always flag a conflict."""


def recovery_node(state: AgentState) -> AgentState:
    soreness = ", ".join(state["soreness_areas"]) if state["soreness_areas"] else "None"
    prompt = f"""
Assess recovery status and flag any conflicts with today's planned workout:
- Sleep last night: {state['sleep_hours']} hours
- Soreness areas: {soreness}
- Current workout plan proposes: Check for heavy loading on sore areas
- Fitness level: {state['fitness_level']}
- Goal: {state['goal']}

If sleep < 6 hours or multiple sore areas, flag HIGH fatigue and recommend workout modification.
"""
    response = llm.invoke(
        [SystemMessage(content=RECOVERY_SYSTEM), HumanMessage(content=prompt)]
    )
    state["recovery_plan"] = response.content
    return state
