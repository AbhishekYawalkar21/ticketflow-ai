from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Float, Enum, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketLanguage(str, enum.Enum):
    GERMAN = "de"
    ENGLISH = "en"

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, nullable=True)
    source = Column(String, default="api")  # api, email
    subject = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    language = Column(String, default="en")
    
    # Classification
    category = Column(String, nullable=True)
    priority = Column(String, default="medium")
    sentiment = Column(Float, nullable=True)
    
    # Status tracking
    status = Column(String, default="open")
    automation_score = Column(Float, default=0.0)
    assigned_to = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relations
    classifications = relationship("Classification", back_populates="ticket", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="ticket", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Ticket {self.id}: {self.subject[:50]}>"

class Classification(Base):
    __tablename__ = "classifications"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, index=True)
    
    category = Column(String, nullable=False)
    confidence = Column(Float, default=0.0)
    suggested_response = Column(Text, nullable=True)
    
    language = Column(String, default="en")
    is_automated = Column(Boolean, default=False)
    automation_rule = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ticket = relationship("Ticket", back_populates="classifications")

class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, index=True)
    
    message_type = Column(String)  # customer, agent, system
    content = Column(Text, nullable=False)
    language = Column(String, default="en")
    sentiment = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ticket = relationship("Ticket", back_populates="interactions")

class AnalyticsMetric(Base):
    __tablename__ = "analytics_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    total_tickets = Column(Integer, default=0)
    automated_count = Column(Integer, default=0)
    avg_resolution_time = Column(Float, default=0.0)
    avg_sentiment = Column(Float, default=0.0)
    
    date = Column(DateTime, default=datetime.utcnow, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)