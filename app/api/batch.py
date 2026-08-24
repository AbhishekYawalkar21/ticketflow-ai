from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.models import Ticket
from app.tasks import batch_classify_tickets
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/batch", tags=["batch"])

@router.post("/classify")
async def batch_classify(
    ticket_ids: List[int],
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Batch classify multiple tickets asynchronously"""
    if not ticket_ids:
        return {"error": "No ticket IDs provided"}
    
    if len(ticket_ids) > 100:
        return {"error": "Maximum 100 tickets per batch"}
    
    # Verify all tickets exist
    from sqlalchemy import select
    result = await db.execute(
        select(Ticket).where(Ticket.id.in_(ticket_ids))
    )
    tickets = result.scalars().all()
    
    if len(tickets) != len(ticket_ids):
        return {"error": "Some tickets not found"}
    
    # Queue batch job
    task_result = batch_classify_tickets.delay(ticket_ids)
    
    return {
        "batch_id": task_result.id,
        "total_tickets": len(ticket_ids),
        "status": "queued"
    }

@router.get("/classify/{batch_id}")
async def get_batch_status(batch_id: str):
    """Get batch classification status"""
    from celery.result import AsyncResult
    from app.tasks import app as celery_app
    
    result = AsyncResult(batch_id, app=celery_app)
    
    return {
        "batch_id": batch_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }