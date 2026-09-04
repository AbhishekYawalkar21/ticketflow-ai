from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models import Ticket, Classification
from app.schemas import ClassificationSchema
from app.tasks import classify_ticket_async

router = APIRouter()

@router.post("/{ticket_id}/classify")
async def trigger_classification(
    ticket_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Trigger async classification task for a ticket"""
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Send to Celery task queue
    task = classify_ticket_async.delay(ticket_id)
    
    return {
        "ticket_id": ticket_id,
        "task_id": task.id,
        "status": "queued"
    }

@router.get("/tasks/{task_id}")
async def get_classification_status(task_id: str):
    """Check classification task status"""
    from celery.result import AsyncResult
    from app.tasks import app as celery_app
    
    result = AsyncResult(task_id, app=celery_app)
    
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }

@router.get("/{ticket_id}", response_model=List[ClassificationSchema])
async def get_ticket_classifications(
    ticket_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all classifications for a ticket"""
    result = await db.execute(
        select(Classification).where(Classification.ticket_id == ticket_id)
    )
    return result.scalars().all()