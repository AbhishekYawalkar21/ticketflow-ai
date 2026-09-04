from fastapi import APIRouter
from app.api import tickets, classifications, analytics, batch, health, email_integration

api_router = APIRouter()

api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(classifications.router, prefix="/classifications", tags=["classifications"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(batch.router, prefix="/batch", tags=["batch"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(email_integration.router, prefix="/email", tags=["email"])