"""Node 6: Final Decision Node, plus a Rejection Node used by conditional edges."""
from app.langgraph.state import GraphState
from app.config import get_logger

logger = get_logger(__name__)


async def final_decision_node(state: GraphState) -> GraphState:
    """Reached only when validation passed, an NGO was found in range, and
    the AI evaluation accepted the donation."""
    state["final_status"] = "accepted"
    state["final_reason"] = state.get("ngo_selection_reason", state.get("ai_eval_reason", ""))
    logger.info("Final decision: ACCEPTED")
    return state


async def rejection_node(state: GraphState) -> GraphState:
    """Reached via conditional edges when validation fails, no NGO is in
    range, or the AI evaluation rejects the donation. Ensures the graph
    short-circuits instead of wasting further LLM calls."""
    if state.get("validation_status") == "invalid":
        reason = "; ".join(state.get("validation_errors", []))
    elif not state.get("eligible_ngos"):
        reason = "No registered NGO found within the allowed pickup distance."
    else:
        reason = state.get("ai_eval_reason", "Donation was rejected by AI evaluation.")

    state["final_status"] = "rejected"
    state["final_reason"] = reason
    state["selected_ngo"] = state.get("selected_ngo")
    state["email_subject"] = ""
    state["email_body"] = ""
    logger.info(f"Final decision: REJECTED ({reason})")
    return state
