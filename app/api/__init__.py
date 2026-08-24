from fastapi import APIRouter
from app.api import tickets, classifications, analytics, batch, health, email_integration

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(tickets.router)
api_router.include_router(classifications.router)
api_router.include_router(analytics.router)
api_router.include_router(batch.router)
api_router.include_router(health.router)
api_router.include_router(email_integration.router)