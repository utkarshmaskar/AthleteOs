from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from config import GROQ_API_KEY, MODEL_NAME
from graph.state import AgentState
from memory.user_store import get_profile

llm = ChatGroq(api_key=GROQ_API_KEY, model=MODEL_NAME)

PROGRESS_SYSTEM = """You are a data-driven athletic performance analyst.

Always output in this exact format:
SESSIONS COMPLETED: [number]
CURRENT STREAK: [number] days
PLATEAU RISK: [Low/Medium/High]

PROGRESS ANALYSIS:
- [insight about their training history]
- [trend observation]

RECOMMENDATIONS:
- [specific adjustment if plateau detected]
- [motivation or next milestone]

PLATEAU FLAG: [YES/NO]
If YES: [specific change to break plateau — deload week / change rep ranges / new progressive overload block]"""


def progress_node(state: AgentState) -> AgentState:
    profile = get_profile(state["user_name"])
    history = profile.get("session_history", [])[-3:]

    prompt = f"""
Analyze progress using this data:
- Total sessions completed: {profile.get('total_sessions', 0)}
- Current streak: {profile.get('current_streak', 0)}
- Plateau previously flagged: {profile.get('plateau_flagged', False)}
- Goal: {state['goal']}
- Fitness level: {state['fitness_level']}

Recent session history:
{history}
"""
    response = llm.invoke([SystemMessage(content=PROGRESS_SYSTEM), HumanMessage(content=prompt)])
    state["progress_summary"] = response.content
    return state
