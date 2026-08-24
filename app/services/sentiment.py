from textblob import TextBlob
from typing import float
import logging

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Simple sentiment analysis using TextBlob"""
    
    @staticmethod
    def analyze(text: str, language: str = "en") -> float:
        """
        Analyze sentiment of text
        Returns: float between -1.0 (negative) and 1.0 (positive)
        """
        try:
            if language == "de":
                # German sentiment heuristic
                negative_words = ["problem", "fehler", "nicht funktioniert", "schlecht", "enttäuscht"]
                positive_words = ["danke", "großartig", "ausgezeichnet", "perfekt", "zufrieden"]
                
                text_lower = text.lower()
                
                neg_count = sum(1 for word in negative_words if word in text_lower)
                pos_count = sum(1 for word in positive_words if word in text_lower)
                
                total = neg_count + pos_count
                if total == 0:
                    return 0.0
                
                return (pos_count - neg_count) / total
            else:
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                return float(polarity)
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return 0.0