import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.graphql.resolvers import Mutation
from app.graphql.types import DonationInput


def test_create_donation_uses_provided_ngo_email():
    async def run_test():
        mutation = Mutation()
        donation_input = DonationInput(
            restaurantName="Test Restaurant",
            restaurantEmail="restaurant@example.com",
            restaurantPhone="1234567890",
            foodType="Rice",
            quantity=10,
            preparationTime="2026-07-25T18:00",
            pickupAddress="Main Street",
            city="Delhi",
            ngoEmail="ngo@example.com",
        )

        insert_result = SimpleNamespace(inserted_id="donation-1")
        fake_doc = {
            "_id": "donation-1",
            "restaurantName": donation_input.restaurantName,
            "restaurantEmail": donation_input.restaurantEmail,
            "restaurantPhone": donation_input.restaurantPhone,
            "foodType": donation_input.foodType,
            "quantity": donation_input.quantity,
            "preparationTime": donation_input.preparationTime,
            "pickupAddress": donation_input.pickupAddress,
            "city": donation_input.city,
            "status": "accepted",
            "assignedNGO": "Test NGO",
            "ngoEmail": donation_input.ngoEmail,
            "aiReason": "",
            "emailSubject": "Test Subject",
            "emailBody": "Test Body",
            "emailSent": True,
            "createdAt": "2026-07-25T18:00:00+00:00",
        }

        collection = SimpleNamespace(
            insert_one=AsyncMock(return_value=insert_result),
            update_one=AsyncMock(return_value=None),
            find_one=AsyncMock(return_value=fake_doc),
        )

        with patch("app.graphql.resolvers.donations_collection", return_value=collection), patch(
            "app.graphql.resolvers.run_donation_workflow",
            new=AsyncMock(
                return_value={
                    "final_status": "accepted",
                    "final_reason": "",
                    "selected_ngo": {"name": "Test NGO", "email": "ai-ngo@example.com"},
                    "email_subject": "Test Subject",
                    "email_body": "Test Body",
                }
            ),
        ), patch("app.graphql.resolvers.send_email", return_value=True) as send_email_mock:
            result = await mutation.createDonation(donation_input)

        assert result.success is True
        assert send_email_mock.call_args.args[0] == "ngo@example.com"

    asyncio.run(run_test())
