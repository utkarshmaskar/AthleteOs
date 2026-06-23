from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from config import GROQ_API_KEY, MODEL_NAME
from graph.state import AgentState

llm = ChatGroq(api_key=GROQ_API_KEY, model=MODEL_NAME)

NUTRITION_SYSTEM = """You are an elite sports nutritionist. Your job is to create a precise daily nutrition plan.

Always output your plan in this exact format:
DAILY CALORIE TARGET: [number] kcal
MACROS: Protein [g]g | Carbs [g]g | Fats [g]g

MEALS:
- Breakfast: [meal] (~[cal] kcal)
- Pre-workout: [snack] (~[cal] kcal)
- Post-workout: [meal] (~[cal] kcal)
- Dinner: [meal] (~[cal] kcal)

KEY NOTES: [2-3 specific notes for this user's goal]

Be specific and evidence-based. Adjust macros based on goal (fat loss = caloric deficit, muscle = surplus)."""


def nutrition_node(state: AgentState) -> AgentState:
    prompt = f"""
Create a daily nutrition plan for:
- Goal: {state['goal']}
- Weight: {state['weight_kg']}kg
- Age: {state['age']}
- Fitness level: {state['fitness_level']}
- Training today: YES (adjust pre/post workout nutrition accordingly)
"""
    response = llm.invoke(
        [SystemMessage(content=NUTRITION_SYSTEM), HumanMessage(content=prompt)]
    )
    state["nutrition_plan"] = response.content
    return state
