"""Node 1: Receive Donation, Node 2: Validate Donation.

Validation includes:
 - required field checks
 - quantity sanity check
 - preparation time non-empty
 - pickup address non-empty
 - geocoding pickup address
 - filtering NGOs to those within MAX_DISTANCE_KM (Haversine)

If no NGOs are within range, validation_status is still "valid" but
eligible_ngos will be empty — this is caught later by a conditional edge
that routes straight to rejection instead of wasting an LLM call.
"""
from app.langgraph.state import GraphState
from app.services.geocode import geocode_address, haversine_km
from app.services.mongodb import ngos_collection
from app.config import settings, get_logger

logger = get_logger(__name__)

REQUIRED_FIELDS = [
    "restaurantName",
    "restaurantEmail",
    "restaurantPhone",
    "foodType",
    "quantity",
    "preparationTime",
    "pickupAddress",
    "city",
]

MAX_QUANTITY_KG = 5000  # sanity ceiling to catch obvious typos


async def receive_donation_node(state: GraphState) -> GraphState:
    """Node 1: entry point. Donation is already placed into state by the
    GraphQL resolver before graph invocation; this node just logs receipt."""
    logger.info(f"Received donation from {state['donation'].get('restaurantName')}")
    return state


async def validate_donation_node(state: GraphState) -> GraphState:
    """Node 2: field validation + distance-based NGO filtering."""
    donation = state["donation"]
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        value = donation.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"Missing required field: {field}")

    quantity = donation.get("quantity")
    if quantity is not None:
        try:
            qty = float(quantity)
            if qty <= 0:
                errors.append("Quantity must be greater than 0")
            elif qty > MAX_QUANTITY_KG:
                errors.append(f"Quantity exceeds sane maximum of {MAX_QUANTITY_KG}kg")
        except (TypeError, ValueError):
            errors.append("Quantity must be a number")

    if errors:
        logger.warning(f"Validation failed: {errors}")
        state["validation_status"] = "invalid"
        state["validation_errors"] = errors
        state["eligible_ngos"] = []
        return state

    # Geocode pickup address
    coords = geocode_address(donation["pickupAddress"], donation["city"])
    if coords is None:
        # Geocoding failed (common on cloud hosts where Nominatim blocks requests).
        # Instead of rejecting the donation, skip distance filtering and include
        # ALL NGOs so the AI can still pick the best match by city name.
        logger.warning("Geocoding failed — skipping distance filter, including all NGOs")
        donation_lat, donation_lon = None, None
    else:
        donation_lat, donation_lon = coords

    state["donation_lat"] = donation_lat
    state["donation_lon"] = donation_lon

    # Fetch NGOs and filter by distance (if coordinates available)
    ngos_cursor = ngos_collection().find({})
    all_ngos = await ngos_cursor.to_list(length=500)

    eligible = []
    if donation_lat is not None and donation_lon is not None:
        # Distance-based filtering
        for ngo in all_ngos:
            ngo_lat = ngo.get("lat")
            ngo_lon = ngo.get("lon")
            if ngo_lat is None or ngo_lon is None:
                continue
            distance = haversine_km(donation_lat, donation_lon, ngo_lat, ngo_lon)
            if distance <= settings.MAX_DISTANCE_KM:
                ngo_copy = dict(ngo)
                ngo_copy["_id"] = str(ngo_copy["_id"])
                ngo_copy["distance_km"] = round(distance, 2)
                eligible.append(ngo_copy)
        eligible.sort(key=lambda n: n["distance_km"])
    else:
        # No coordinates — include all NGOs, prefer same-city ones first
        donation_city = donation.get("city", "").strip().lower()
        for ngo in all_ngos:
            ngo_copy = dict(ngo)
            ngo_copy["_id"] = str(ngo_copy["_id"])
            ngo_copy["distance_km"] = 0.0 if ngo.get("city", "").strip().lower() == donation_city else 999.0
            eligible.append(ngo_copy)
        eligible.sort(key=lambda n: n["distance_km"])

    state["validation_status"] = "valid"
    state["validation_errors"] = []
    state["eligible_ngos"] = eligible

    logger.info(f"Validation passed. {len(eligible)} NGO(s) eligible (distance filter {'applied' if donation_lat else 'skipped'})")
    return state
