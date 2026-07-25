import strawberry
from typing import Optional


@strawberry.type
class NGO:
    id: str
    name: str
    email: str
    city: str
    lat: Optional[float] = None
    lon: Optional[float] = None


@strawberry.input
class NGOInput:
    name: str
    email: str
    city: str


@strawberry.type
class Donation:
    id: str
    restaurantName: str
    restaurantEmail: str
    restaurantPhone: str
    foodType: str
    quantity: float
    preparationTime: str
    pickupAddress: str
    city: str
    notes: Optional[str] = None
    status: str
    assignedNGO: Optional[str] = None
    ngoEmail: Optional[str] = None
    aiReason: Optional[str] = None
    emailSubject: Optional[str] = None
    emailBody: Optional[str] = None
    emailSent: bool
    createdAt: str


@strawberry.input
class DonationInput:
    restaurantName: str
    restaurantEmail: str
    restaurantPhone: str
    foodType: str
    quantity: float
    preparationTime: str
    pickupAddress: str
    city: str
    notes: Optional[str] = None
    ngoEmail: Optional[str] = None
    ngoName: Optional[str] = None


@strawberry.type
class DonationResult:
    success: bool
    message: str
    donation: Optional[Donation] = None
