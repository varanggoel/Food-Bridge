"""Node 4: NGO Selection Agent.

Selects exactly one NGO from the pre-filtered (distance-eligible) list,
"""
import json
from app.langgraph.state import GraphState
from app.services.groq_service import call_groq_json
from app.config import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are an AI Food Donation Coordinator working in India.

You must select exactly ONE NGO from the provided list of eligible NGOs to
receive this food donation. All NGOs given to you are already within an
acceptable pickup distance, so do not reject based on distance.

Rules:
- Choose exactly one NGO from the provided list only. Never invent an NGO
  name that is not in the list.
- Base your choice on suitability (e.g. proximity, matching food type if
  any preference is implied) and briefly justify it.
- Provide a concise reason (1-3 sentences).

Return ONLY valid JSON with this exact shape, nothing else:
{
  "accepted": true,
  "selectedNGO": "Exact NGO Name From List",
  "reason": "your explanation here",
  "emailSubject": "",
  "emailBody": ""
}

Leave emailSubject and emailBody as empty strings. Never return markdown.
"""


async def select_ngo_node(state: GraphState) -> GraphState:
    donation = state["donation"]
    eligible = state.get("eligible_ngos", [])

    ngo_list_str = "\n".join(
        f"- {n['name']} (city: {n.get('city', 'N/A')}, distance: {n['distance_km']}km)"
        for n in eligible
    )

    user_prompt = f"""Donation details:
Food Type: {donation['foodType']}
Quantity: {donation['quantity']} kg
Pickup City: {donation['city']}

Eligible NGOs (within range):
{ngo_list_str}
"""

    decision = call_groq_json(SYSTEM_PROMPT, user_prompt)

    # Validate the model actually picked from the provided list
    matched_ngo = next(
        (n for n in eligible if n["name"].strip().lower() == decision.selectedNGO.strip().lower()),
        None,
    )

    if matched_ngo is None:
        logger.warning(
            f"AI selected NGO '{decision.selectedNGO}' not found in eligible list; "
            f"falling back to nearest eligible NGO"
        )
        if eligible:
            matched_ngo = eligible[0]
            state["ngo_selection_reason"] = (
                f"AI selection could not be matched; nearest eligible NGO chosen automatically."
            )
        else:
            state["selected_ngo"] = None
            state["ngo_selection_reason"] = "No eligible NGO available."
            return state
    else:
        state["ngo_selection_reason"] = decision.reason

    state["selected_ngo"] = matched_ngo
    logger.info(f"NGO selected: {matched_ngo['name']}")
    return state
