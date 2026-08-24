import asyncio
from celery import shared_task, group
from app.worker import app as celery_app
from app.services.classifier import classifier
from app.services.sentiment import SentimentAnalyzer
from app.services.multilingual import SentimentAnalyzerAdvanced, LanguageDetector
from app.database import AsyncSessionLocal
from app.models import Ticket, Classification
from sqlalchemy import select
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def classify_ticket_async(self, ticket_id: int):
    """
    Async task: Classify ticket using Ollama LLM
    """
    try:
        # Fetch ticket from DB
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ticket = loop.run_until_complete(_get_ticket(ticket_id))
        
        if not ticket:
            logger.error(f"Ticket {ticket_id} not found")
            return {"error": "Ticket not found"}
        
        # Detect language if not set
        if not ticket.language or ticket.language == "en":
            detected_lang = LanguageDetector.detect_language(ticket.subject + " " + ticket.content)
            language = detected_lang
        else:
            language = ticket.language
        
        # Classify using Ollama
        classification_result = classifier.classify_ticket(
            subject=ticket.subject,
            content=ticket.content,
            language=language
        )
        
        # Analyze sentiment
        sentiment = SentimentAnalyzerAdvanced.analyze(
            ticket.content,
            language=language
        )
        
        # Save classification to DB
        loop.run_until_complete(_save_classification(
            ticket_id=ticket_id,
            classification_result=classification_result,
            sentiment=sentiment
        ))
        
        logger.info(f"Classification completed for ticket {ticket_id}")
        
        return {
            "ticket_id": ticket_id,
            "status": "completed",
            "result": classification_result,
            "sentiment": sentiment
        }
        
    except Exception as e:
        logger.error(f"Classification task failed: {str(e)}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

@celery_app.task(bind=True)
def batch_classify_tickets(self, ticket_ids: list):
    """
    Batch classify multiple tickets
    """
    # Use Celery group for parallel processing
    job = group(classify_ticket_async.s(ticket_id) for ticket_id in ticket_ids)
    result = job.apply_async()
    
    return {
        "total": len(ticket_ids),
        "group_id": result.id,
        "status": "processing"
    }

@celery_app.task
def generate_daily_report():
    """
    Generate daily analytics report
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(_generate_analytics_report())
    return result

# Helper async functions
async def _get_ticket(ticket_id: int):
    """Fetch ticket from database"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Ticket).where(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()

async def _save_classification(ticket_id: int, classification_result: dict, sentiment: float):
    """Save classification result to database"""
    async with AsyncSessionLocal() as session:
        ticket = await session.execute(
            select(Ticket).where(Ticket.id == ticket_id)
        )
        ticket = ticket.scalar_one()
        
        # Update ticket
        ticket.sentiment = sentiment
        ticket.category = classification_result.get("category", "General")
        ticket.priority = classification_result.get("priority", "medium")
        ticket.automation_score = classification_result.get("confidence", 0.0) * 100
        
        # Create classification record
        classification = Classification(
            ticket_id=ticket_id,
            category=classification_result.get("category", "General"),
            confidence=classification_result.get("confidence", 0.0),
            suggested_response=classification_result.get("suggested_response", ""),
            language=ticket.language,
            is_automated=True
        )
        
        session.add(classification)
        await session.commit()

async def _generate_analytics_report():
    """Generate analytics report"""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import func
        
        total = await session.execute(select(func.count(Ticket.id)))
        total_count = total.scalar()
        
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "total_tickets": total_count
        }