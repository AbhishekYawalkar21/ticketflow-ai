import re
from app.exceptions import ValidationError

class TicketValidator:
    @staticmethod
    def validate_subject(subject: str) -> str:
        """Validate ticket subject"""
        if not subject or len(subject.strip()) == 0:
            raise ValidationError("Subject cannot be empty")
        
        if len(subject) > 500:
            raise ValidationError("Subject must be less than 500 characters")
        
        return subject.strip()
    
    @staticmethod
    def validate_content(content: str) -> str:
        """Validate ticket content"""
        if not content or len(content.strip()) == 0:
            raise ValidationError("Content cannot be empty")
        
        if len(content) > 10000:
            raise ValidationError("Content must be less than 10000 characters")
        
        return content.strip()
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("Invalid email format")
        return email

class QueryValidator:
    @staticmethod
    def validate_pagination(skip: int, limit: int) -> tuple:
        """Validate pagination parameters"""
        if skip < 0:
            raise ValidationError("skip must be >= 0")
        if limit < 1 or limit > 100:
            raise ValidationError("limit must be between 1 and 100")
        return skip, limit