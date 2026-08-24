from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List
from app.database import get_db
from app.models import Ticket, Classification, Interaction
from app.schemas import (
    TicketCreate, TicketResponse, TicketUpdate, 
    ClassificationSchema, InteractionSchema
)
from datetime import datetime

router = APIRouter(prefix="/api/v1/tickets", tags=["tickets"])

@router.post("", response_model=TicketResponse, status_code=201)
async def create_ticket(
    ticket: TicketCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new support ticket"""
    new_ticket = Ticket(
        subject=ticket.subject,
        content=ticket.content,
        source=ticket.source,
        language=ticket.language
    )
    db.add(new_ticket)
    await db.commit()
    await db.refresh(new_ticket)
    return new_ticket

@router.get("", response_model=List[TicketResponse])
async def list_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: str = Query(None),
    priority: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List tickets with filtering"""
    query = select(Ticket)
    
    if status:
        query = query.where(Ticket.status == status)
    if priority:
        query = query.where(Ticket.priority == priority)
    
    query = query.order_by(desc(Ticket.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get single ticket with full details"""
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return ticket

@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    update: TicketUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update ticket status, priority, or assignment"""
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    update_data = update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(ticket, key, value)
    
    ticket.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(ticket)
    return ticket

@router.delete("/{ticket_id}", status_code=204)
async def delete_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a ticket"""
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    await db.delete(ticket)
    await db.commit()

@router.post("/{ticket_id}/interactions", response_model=InteractionSchema)
async def add_interaction(
    ticket_id: int,
    interaction: InteractionSchema,
    db: AsyncSession = Depends(get_db)
):
    """Add message/interaction to ticket"""
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    new_interaction = Interaction(
        ticket_id=ticket_id,
        message_type=interaction.message_type,
        content=interaction.content,
        sentiment=interaction.sentiment,
        language=ticket.language
    )
    db.add(new_interaction)
    await db.commit()
    await db.refresh(new_interaction)
    return new_interaction

@router.get("/{ticket_id}/interactions", response_model=List[InteractionSchema])
async def get_interactions(
    ticket_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all interactions for a ticket"""
    result = await db.execute(
        select(Interaction)
        .where(Interaction.ticket_id == ticket_id)
        .order_by(Interaction.created_at)
    )
    return result.scalars().all()