"""Builds and compiles the LangGraph StateGraph for the donation workflow.

Graph shape (with real conditional branching, not a straight pipeline):

    receive_donation
          |
    validate_donation
          |
   [conditional] --invalid or no NGO in range--> rejection --> END
          |
        valid, NGO(s) available
          |
    evaluate_donation (AI)
          |
   [conditional] --ai rejects--> rejection --> END
          |
        ai accepts
          |
    select_ngo (AI)
          |
    generate_email (AI)
          |
    final_decision --> END
"""
from langgraph.graph import StateGraph, END
from app.langgraph.state import GraphState
from app.langgraph.nodes.validation import receive_donation_node, validate_donation_node
from app.langgraph.nodes.evaluation import evaluate_donation_node
from app.langgraph.nodes.ngo_selection import select_ngo_node
from app.langgraph.nodes.email_generation import generate_email_node
from app.langgraph.nodes.final_node import final_decision_node, rejection_node


def route_after_validation(state: GraphState) -> str:
    if state.get("validation_status") == "invalid":
        return "reject"
    if not state.get("eligible_ngos"):
        return "reject"
    return "continue"


def route_after_evaluation(state: GraphState) -> str:
    if not state.get("ai_accepted", False):
        return "reject"
    return "continue"


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("receive_donation", receive_donation_node)
    graph.add_node("validate_donation", validate_donation_node)
    graph.add_node("evaluate_donation", evaluate_donation_node)
    graph.add_node("select_ngo", select_ngo_node)
    graph.add_node("generate_email", generate_email_node)
    graph.add_node("final_decision", final_decision_node)
    graph.add_node("rejection", rejection_node)

    graph.set_entry_point("receive_donation")

    graph.add_edge("receive_donation", "validate_donation")

    graph.add_conditional_edges(
        "validate_donation",
        route_after_validation,
        {"reject": "rejection", "continue": "evaluate_donation"},
    )

    graph.add_conditional_edges(
        "evaluate_donation",
        route_after_evaluation,
        {"reject": "rejection", "continue": "select_ngo"},
    )

    graph.add_edge("select_ngo", "generate_email")
    graph.add_edge("generate_email", "final_decision")

    graph.add_edge("final_decision", END)
    graph.add_edge("rejection", END)

    return graph.compile()


# Compiled once at import time and reused across requests
compiled_graph = build_graph()


async def run_donation_workflow(donation_dict: dict) -> GraphState:
    initial_state: GraphState = {"donation": donation_dict}
    result = await compiled_graph.ainvoke(initial_state)
    return result
