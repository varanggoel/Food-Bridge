"""Shared state object passed between LangGraph nodes."""
from typing import TypedDict, Optional, List, Dict, Any


class DonationInput(TypedDict):
    restaurantName: str
    restaurantEmail: str
    restaurantPhone: str
    foodType: str
    quantity: float
    preparationTime: str
    pickupAddress: str
    city: str
    notes: Optional[str]


class GraphState(TypedDict, total=False):
    # Input
    donation: DonationInput

    # Node 2: Validate Donation
    validation_status: str          # "valid" | "invalid"
    validation_errors: List[str]

    # Geocoding + distance filtering (part of validation stage)
    donation_lat: Optional[float]
    donation_lon: Optional[float]
    eligible_ngos: List[Dict[str, Any]]   # NGOs within MAX_DISTANCE_KM

    # Node 3: AI Evaluation
    ai_accepted: bool
    ai_eval_reason: str

    # Node 4: NGO Selection
    selected_ngo: Optional[Dict[str, Any]]
    ngo_selection_reason: str

    # Node 5: Email Generation
    email_subject: str
    email_body: str

    # Node 6: Final Decision
    final_status: str      # "accepted" | "rejected"
    final_reason: str

    # Post-graph (set by FastAPI after email send)
    email_sent: bool
