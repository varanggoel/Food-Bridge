import strawberry
from datetime import datetime, timezone
from bson import ObjectId
from typing import List, Optional

from app.graphql.types import (
    NGO, NGOInput, Donation, DonationInput, DonationResult,
)
from app.services.mongodb import donations_collection, ngos_collection
from app.services.geocode import geocode_address
from app.services.email import send_email
from app.langgraph.graph import run_donation_workflow
from app.config import get_logger

logger = get_logger(__name__)


def _donation_doc_to_type(doc: dict) -> Donation:
    return Donation(
        id=str(doc["_id"]),
        restaurantName=doc["restaurantName"],
        restaurantEmail=doc["restaurantEmail"],
        restaurantPhone=doc["restaurantPhone"],
        foodType=doc["foodType"],
        quantity=doc["quantity"],
        preparationTime=doc["preparationTime"],
        pickupAddress=doc["pickupAddress"],
        city=doc["city"],
        notes=doc.get("notes"),
        status=doc["status"],
        assignedNGO=doc.get("assignedNGO"),
        ngoEmail=doc.get("ngoEmail"),
        aiReason=doc.get("aiReason"),
        emailSubject=doc.get("emailSubject"),
        emailBody=doc.get("emailBody"),
        emailSent=doc.get("emailSent", False),
        createdAt=doc["createdAt"].isoformat() if isinstance(doc["createdAt"], datetime) else doc["createdAt"],
    )


def _ngo_doc_to_type(doc: dict) -> NGO:
    return NGO(
        id=str(doc["_id"]),
        name=doc["name"],
        email=doc["email"],
        city=doc["city"],
        lat=doc.get("lat"),
        lon=doc.get("lon"),
    )


@strawberry.type
class Query:
    @strawberry.field
    async def donations(self) -> List[Donation]:
        cursor = donations_collection().find({}).sort("createdAt", -1)
        docs = await cursor.to_list(length=200)
        return [_donation_doc_to_type(d) for d in docs]

    @strawberry.field
    async def donation(self, id: str) -> Optional[Donation]:
        doc = await donations_collection().find_one({"_id": ObjectId(id)})
        return _donation_doc_to_type(doc) if doc else None

    @strawberry.field
    async def ngos(self) -> List[NGO]:
        cursor = ngos_collection().find({})
        docs = await cursor.to_list(length=200)
        return [_ngo_doc_to_type(d) for d in docs]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def createDonation(self, input: DonationInput) -> DonationResult:
        donation_dict = {
            "restaurantName": input.restaurantName,
            "restaurantEmail": input.restaurantEmail,
            "restaurantPhone": input.restaurantPhone,
            "foodType": input.foodType,
            "quantity": input.quantity,
            "preparationTime": input.preparationTime,
            "pickupAddress": input.pickupAddress,
            "city": input.city,
            "notes": input.notes,
        }

        # Store temporarily with pending status
        temp_doc = {
            **donation_dict,
            "status": "processing",
            "assignedNGO": None,
            "ngoEmail": None,
            "aiReason": None,
            "emailSubject": None,
            "emailBody": None,
            "emailSent": False,
            "createdAt": datetime.now(timezone.utc),
        }
        insert_result = await donations_collection().insert_one(temp_doc)
        donation_id = insert_result.inserted_id

        try:
            # Run LangGraph workflow
            final_state = await run_donation_workflow(donation_dict)
        except Exception as e:
            logger.error(f"LangGraph workflow failed: {e}")
            await donations_collection().update_one(
                {"_id": donation_id},
                {"$set": {"status": "error", "aiReason": f"Workflow error: {e}"}},
            )
            return DonationResult(success=False, message="AI workflow failed. Please try again.", donation=None)

        status = final_state.get("final_status", "rejected")
        reason = final_state.get("final_reason", "")
        selected_ngo = final_state.get("selected_ngo")
        email_subject = final_state.get("email_subject", "")
        email_body = final_state.get("email_body", "")

        email_sent = False
        ngo_email = None
        ngo_name = None

        # Email sending ONLY happens after the LangGraph workflow completes successfully
        if status == "accepted" and selected_ngo:
            ngo_name = selected_ngo["name"]
            ngo_email = selected_ngo["email"]
            email_sent = send_email(ngo_email, email_subject, email_body)

        update_fields = {
            "status": status,
            "assignedNGO": ngo_name,
            "ngoEmail": ngo_email,
            "aiReason": reason,
            "emailSubject": email_subject,
            "emailBody": email_body,
            "emailSent": email_sent,
        }
        await donations_collection().update_one({"_id": donation_id}, {"$set": update_fields})

        final_doc = await donations_collection().find_one({"_id": donation_id})
        return DonationResult(
            success=(status == "accepted"),
            message="Donation accepted and NGO notified." if status == "accepted" else f"Donation rejected: {reason}",
            donation=_donation_doc_to_type(final_doc),
        )

    @strawberry.mutation
    async def resendEmail(self, id: str) -> DonationResult:
        doc = await donations_collection().find_one({"_id": ObjectId(id)})
        if not doc:
            return DonationResult(success=False, message="Donation not found", donation=None)

        if doc.get("status") != "accepted" or not doc.get("ngoEmail"):
            return DonationResult(success=False, message="This donation has no assigned NGO email to resend to", donation=None)

        sent = send_email(doc["ngoEmail"], doc.get("emailSubject", ""), doc.get("emailBody", ""))
        await donations_collection().update_one({"_id": ObjectId(id)}, {"$set": {"emailSent": sent}})
        final_doc = await donations_collection().find_one({"_id": ObjectId(id)})

        return DonationResult(
            success=sent,
            message="Email resent successfully." if sent else "Failed to resend email.",
            donation=_donation_doc_to_type(final_doc),
        )

    @strawberry.mutation
    async def createNGO(self, input: NGOInput) -> NGO:
        coords = geocode_address(input.city, input.city)
        doc = {
            "name": input.name,
            "email": input.email,
            "city": input.city,
            "lat": coords[0] if coords else None,
            "lon": coords[1] if coords else None,
        }
        result = await ngos_collection().insert_one(doc)
        doc["_id"] = result.inserted_id
        return _ngo_doc_to_type(doc)

    @strawberry.mutation
    async def deleteNGO(self, id: str) -> bool:
        result = await ngos_collection().delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
