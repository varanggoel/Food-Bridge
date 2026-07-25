"""Node 5: Email Generation Agent.

Generates a professional notification email subject + body for the
selected NGO using Groq.
"""
from app.langgraph.state import GraphState
from app.services.groq_service import call_groq_json
from app.config import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are an AI Food Donation Coordinator working in India.

Write a professional, warm, and clear notification email to an NGO
informing them of an available food donation they have been matched with.

Rules:
- Subject should be concise and informative.
- Body should include: restaurant name, food type, quantity, pickup
  address, pickup city, and preparation/ready time. Sign off as
  "FoodBridge India Coordination Team".
- Professional tone, no slang, properly formatted paragraphs (use \\n for
  line breaks within the JSON string).

Return ONLY valid JSON with this exact shape, nothing else:
{
  "accepted": true,
  "selectedNGO": "",
  "reason": "",
  "emailSubject": "your subject here",
  "emailBody": "your full email body here"
}

Leave selectedNGO and reason as empty strings. Never return markdown.
"""


async def generate_email_node(state: GraphState) -> GraphState:
    donation = state["donation"]
    ngo = state.get("selected_ngo")

    if ngo is None:
        state["email_subject"] = ""
        state["email_body"] = ""
        return state

    user_prompt = f"""Generate the notification email.

NGO Name: {ngo['name']}

Donation details:
Restaurant: {donation['restaurantName']}
Food Type: {donation['foodType']}
Quantity: {donation['quantity']} kg
Preparation/Ready Time: {donation['preparationTime']}
Pickup Address: {donation['pickupAddress']}, {donation['city']}
Restaurant Contact Phone: {donation['restaurantPhone']}
Notes: {donation.get('notes', 'None')}
"""

    decision = call_groq_json(SYSTEM_PROMPT, user_prompt)

    state["email_subject"] = decision.emailSubject or f"Food Donation Available: {donation['foodType']}"
    state["email_body"] = decision.emailBody or (
        f"Dear {ngo['name']},\n\n"
        f"A food donation is available from {donation['restaurantName']}.\n"
        f"Food Type: {donation['foodType']}\nQuantity: {donation['quantity']} kg\n"
        f"Pickup Address: {donation['pickupAddress']}, {donation['city']}\n"
        f"Ready Time: {donation['preparationTime']}\n\n"
        f"Regards,\nFoodBridge India Coordination Team"
    )

    logger.info(f"Email generated with subject: {state['email_subject']}")
    return state
