"""MongoDB connection and collection accessors."""
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings, get_logger

logger = get_logger(__name__)

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        if not settings.MONGODB_URI:
            raise RuntimeError("MONGODB_URI is not set in environment variables")
        _client = AsyncIOMotorClient(settings.MONGODB_URI)
        logger.info("MongoDB client initialized")
    return _client


def get_db():
    return get_client()["foodbridge"]


def donations_collection():
    return get_db()["donations"]


def ngos_collection():
    return get_db()["ngos"]


async def ping():
    try:
        await get_client().admin.command("ping")
        logger.info("MongoDB ping successful")
        return True
    except Exception as e:
        logger.error(f"MongoDB ping failed: {e}")
        return False
