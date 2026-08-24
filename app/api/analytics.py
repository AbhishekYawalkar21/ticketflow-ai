from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Ticket, AnalyticsMetric
from app.schemas import AnalyticsSchema

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/metrics")
async def get_metrics(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics metrics for last N days"""
    date_from = datetime.utcnow() - timedelta(days=days)
    
    # Total tickets
    total_result = await db.execute(
        select(func.count(Ticket.id)).where(Ticket.created_at >= date_from)
    )
    total_tickets = total_result.scalar() or 0
    
    # Automated tickets
    automated_result = await db.execute(
        select(func.count(Ticket.id)).where(
            (Ticket.created_at >= date_from) &
            (Ticket.automation_score >= 70)
        )
    )
    automated_count = automated_result.scalar() or 0
    
    # Average sentiment
    sentiment_result = await db.execute(
        select(func.avg(Ticket.sentiment)).where(Ticket.created_at >= date_from)
    )
    avg_sentiment = sentiment_result.scalar() or 0.0
    
    # Average resolution time
    resolution_result = await db.execute(
        select(func.avg(
            (Ticket.resolved_at - Ticket.created_at).cast(type_=float)
        )).where(
            (Ticket.created_at >= date_from) &
            (Ticket.resolved_at.isnot(None))
        )
    )
    avg_resolution_time = (resolution_result.scalar() or 0) / 60
    
    automation_rate = (automated_count / total_tickets * 100) if total_tickets > 0 else 0
    
    return {
        "total_tickets": total_tickets,
        "automated_count": automated_count,
        "automation_rate": round(automation_rate, 2),
        "avg_resolution_time": round(avg_resolution_time, 2),
        "avg_sentiment": round(float(avg_sentiment), 3),
        "period_days": days
    }

@router.get("/dashboard")
async def get_dashboard_data(
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive dashboard data"""
    # Status breakdown
    status_result = await db.execute(
        select(Ticket.status, func.count(Ticket.id))
        .group_by(Ticket.status)
    )
    status_breakdown = {row[0]: row[1] for row in status_result}
    
    # Priority breakdown
    priority_result = await db.execute(
        select(Ticket.priority, func.count(Ticket.id))
        .group_by(Ticket.priority)
    )
    priority_breakdown = {row[0]: row[1] for row in priority_result}
    
    # Category breakdown
    category_result = await db.execute(
        select(Ticket.category, func.count(Ticket.id))
        .where(Ticket.category.isnot(None))
        .group_by(Ticket.category)
    )
    category_breakdown = {row[0]: row[1] for row in category_result}
    
    metrics = await get_metrics(days=7, db=db)
    
    return {
        "status": status_breakdown,
        "priority": priority_breakdown,
        "categories": category_breakdown,
        "metrics": metrics
    }