import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
import email
from typing import List, Dict
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Email (SMTP/IMAP) integration"""
    
    def __init__(self, smtp_host: str = None, smtp_port: int = None, 
                 email_addr: str = None, password: str = None):
        self.smtp_host = smtp_host or settings.SMTP_SERVER
        self.smtp_port = smtp_port or settings.SMTP_PORT
        self.email = email_addr or settings.SMTP_USER
        self.password = password or settings.SMTP_PASSWORD
    
    async def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email via SMTP"""
        if not self.email or not self.password:
            logger.warning("Email credentials not configured")
            return False
        
        try:
            async with aiosmtplib.SMTP(hostname=self.smtp_host, port=self.smtp_port) as smtp:
                await smtp.login(self.email, self.password)
                
                message = MIMEText(body)
                message['Subject'] = subject
                message['From'] = self.email
                message['To'] = to
                
                await smtp.send_message(message)
                logger.info(f"Email sent to {to}")
                return True
        except Exception as e:
            logger.error(f"Email send error: {str(e)}")
            return False
    
    async def fetch_emails(self, limit: int = 10) -> List[Dict]:
        """Fetch emails from IMAP"""
        if not self.email or not self.password:
            logger.warning("Email credentials not configured")
            return []
        
        try:
            imap = imaplib.IMAP4_SSL(self.smtp_host)
            imap.login(self.email, self.password)
            imap.select('INBOX')
            
            # Fetch recent emails
            status, messages = imap.search(None, 'RECENT')
            message_ids = messages[0].split()[-limit:]
            
            emails = []
            for msg_id in message_ids:
                status, msg_data = imap.fetch(msg_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        emails.append({
                            "from": msg.get("From"),
                            "subject": msg.get("Subject"),
                            "body": self._get_email_body(msg),
                            "timestamp": msg.get("Date")
                        })
            
            imap.close()
            imap.logout()
            return emails
        except Exception as e:
            logger.error(f"IMAP fetch error: {str(e)}")
            return []
    
    @staticmethod
    def _get_email_body(msg) -> str:
        """Extract text body from email message"""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body += part.get_payload()
        else:
            body = msg.get_payload()
        return body