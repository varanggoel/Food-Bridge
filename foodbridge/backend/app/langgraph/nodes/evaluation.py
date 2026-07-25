"""Node 3: AI Evaluation Agent.

Uses Gemini to evaluate the food donation for suitability.
The AI should only reject donations when the city/location information
suggests the donation is not feasible for redistribution.
"""
from app.langgraph.state import GraphState
from app.services.groq_service import call_groq_json
from app.config import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are an AI Food Donation Coordinator working in India.

Your task right now is ONLY to evaluate whether a submitted food donation
is suitable to be accepted for redistribution to an NGO. You are not
selecting an NGO or writing an email yet.

Rules:
- Accept the donation if the food type and quantity are reasonable for
  redistribution and the pickup city is a valid Indian city.
- Reject only if the donation restaurant city is too far from the pickup city
- Do NOT reject based on any dates, times, or scheduling information.
- Do NOT reject based on food freshness assumptions or expiry guesses.
- When in doubt, ACCEPT the donation.
- Provide a concise explanation (1-3 sentences).

Return ONLY valid JSON with this exact shape, nothing else:
{
  "accepted": true,
  "selectedNGO": "",
  "reason": "your explanation here",
  "emailSubject": "",
  "emailBody": ""
}

Leave selectedNGO, emailSubject, and emailBody as empty strings — those are
handled by a later step. Never return markdown or text outside the JSON object.
"""


async def evaluate_donation_node(state: GraphState) -> GraphState:
    donation = state["donation"]

    user_prompt = f"""Evaluate this donation:

Food Type: {donation['foodType']}
Quantity: {donation['quantity']} kg
Pickup City: {donation['city']}
Notes: {donation.get('notes', 'None')}
"""

    decision = call_groq_json(SYSTEM_PROMPT, user_prompt)

    state["ai_accepted"] = decision.accepted
    state["ai_eval_reason"] = decision.reason

    logger.info(f"AI evaluation: accepted={decision.accepted} reason={decision.reason}")
    return state
