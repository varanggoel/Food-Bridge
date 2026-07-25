from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.graphql.schema import schema
from app.services.mongodb import ping
from app.config import settings, get_logger

logger = get_logger(__name__)

app = FastAPI(title="FoodBridge India API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_ORIGIN,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    return {"status": "FoodBridge India API is running"}


@app.get("/health")
async def health():
    db_ok = await ping()
    return {"status": "ok" if db_ok else "degraded", "mongodb": db_ok}


@app.on_event("startup")
async def startup_event():
    logger.info("FoodBridge India backend starting up...")
    await ping()
