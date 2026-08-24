from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Ticket
from app.services.email_service import EmailService
from app.tasks import classify_ticket_async
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/email", tags=["email"])

@router.post("/sync")
async def sync_email_tickets(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Sync emails from inbox to tickets"""
    email_service = EmailService()
    
    if not email_service.email or not email_service.password:
        return {
            "error": "Email not configured",
            "message": "Set SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD in .env"
        }
    
    emails = await email_service.fetch_emails(limit=20)
    
    created_count = 0
    from sqlalchemy import select
    
    for e in emails:
        # Check if email already processed
        existing = await db.execute(
            select(Ticket).where(Ticket.subject == e['subject'])
        )
        
        if not existing.scalar_one_or_none():
            new_ticket = Ticket(
                source="email",
                subject=e['subject'],
                content=e['body'],
                language="en"
            )
            db.add(new_ticket)
            await db.commit()
            await db.refresh(new_ticket)
            
            # Queue classification
            background_tasks.add_task(classify_ticket_async.delay, new_ticket.id)
            created_count += 1
    
    return {
        "synced": created_count,
        "total_fetched": len(emails)
    }

@router.post("/send-response/{ticket_id}")
async def send_email_response(
    ticket_id: int,
    recipient_email: str,
    message_body: str,
    db: AsyncSession = Depends(get_db)
):
    """Send email response to customer"""
    from sqlalchemy import select
    
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        return {"error": "Ticket not found"}
    
    email_service = EmailService()
    success = await email_service.send_email(
        to=recipient_email,
        subject=f"Re: {ticket.subject}",
        body=message_body
    )
    
    if success:
        # Add interaction record
        from app.models import Interaction
        interaction = Interaction(
            ticket_id=ticket_id,
            message_type="agent",
            content=message_body,
            language=ticket.language
        )
        db.add(interaction)
        await db.commit()
        
        return {"success": True, "message": "Email sent"}
    else:
        return {"success": False, "error": "Failed to send email"}