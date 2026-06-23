from langgraph.graph import END, StateGraph

from agents.nutrition_agent import nutrition_node
from agents.orchestrator import orchestrator_node
from agents.progress_agent import progress_node
from agents.recovery_agent import recovery_node
from agents.workout_agent import workout_node
from graph.state import AgentState


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("nutrition", nutrition_node)
    graph.add_node("workout", workout_node)
    graph.add_node("recovery", recovery_node)
    graph.add_node("progress", progress_node)
    graph.add_node("orchestrator", orchestrator_node)

    graph.set_entry_point("nutrition")
    graph.add_edge("nutrition", "workout")
    graph.add_edge("workout", "recovery")
    graph.add_edge("recovery", "progress")
    graph.add_edge("progress", "orchestrator")
    graph.add_edge("orchestrator", END)

    return graph.compile()
