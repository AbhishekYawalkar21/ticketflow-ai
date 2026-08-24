from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class TicketBase(BaseModel):
    subject: str
    content: str
    source: str = "api"
    language: str = "en"

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    assigned_to: Optional[str] = None

class ClassificationSchema(BaseModel):
    category: str
    confidence: float
    suggested_response: Optional[str] = None
    is_automated: bool = False

class InteractionSchema(BaseModel):
    message_type: str
    content: str
    sentiment: Optional[float] = None

class TicketResponse(TicketBase):
    id: int
    status: str
    priority: str
    category: Optional[str]
    sentiment: Optional[float]
    automation_score: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AnalyticsSchema(BaseModel):
    total_tickets: int
    automated_count: int
    automation_rate: float
    avg_resolution_time: float
    avg_sentiment: float
    date: datetime