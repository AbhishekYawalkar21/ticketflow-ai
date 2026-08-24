from fastapi import APIRouter
from app.api import tickets, classifications, analytics, batch, health

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(tickets.router)
api_router.include_router(classifications.router)
api_router.include_router(analytics.router)
api_router.include_router(batch.router)
api_router.include_router(health.router)