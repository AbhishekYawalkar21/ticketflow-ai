from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class LanguageDetector:
    """Detect language from text"""
    
    @staticmethod
    def detect_language(text: str) -> str:
        """
        Simple language detection (German vs English)
        """
        german_words = ["der", "die", "und", "in", "zu", "ist", "das", "mit", "nicht"]
        english_words = ["the", "is", "and", "a", "in", "to", "be", "of", "that"]
        
        text_lower = text.lower()
        
        german_count = sum(1 for word in german_words if f" {word} " in f" {text_lower} ")
        english_count = sum(1 for word in english_words if f" {word} " in f" {text_lower} ")
        
        if german_count > english_count:
            return "de"
        return "en"

class MultilingualPrompts:
    """Language-specific prompts for LLM"""
    
    @staticmethod
    def get_classification_prompt(subject: str, content: str, language: str = "en") -> str:
        if language == "de":
            return f"""
Du bist ein Support-Ticket-Klassifizierer. Analysiere das folgende Ticket:

BETREFF: {subject}
INHALT: {content}

Antworte ausschließlich mit JSON:
{{
    "kategorie": "Technisch|Abrechnung|Allgemein|Feature-Anfrage",
    "priorität": "Niedrig|Mittel|Hoch|Dringend",
    "lösung": "Kurze Antwort auf Deutsch",
    "sicherheit": 0.9
}}
"""
        else:
            return f"""
You are a support ticket classifier. Analyze the following ticket:

SUBJECT: {subject}
CONTENT: {content}

Respond with ONLY this JSON format:
{{
    "category": "Technical|Billing|General|Feature Request",
    "priority": "Low|Medium|High|Urgent",
    "suggested_response": "Brief response in English",
    "confidence": 0.9
}}
"""

class SentimentAnalyzerAdvanced:
    """Improved multilingual sentiment analysis"""
    
    @staticmethod
    def analyze_german(text: str) -> float:
        """Sentiment analysis for German text"""
        positive_words = {
            "danke": 0.8, "dank": 0.8, "großartig": 0.9, "ausgezeichnet": 0.95,
            "perfekt": 0.9, "toll": 0.85, "super": 0.85, "hervorragend": 0.9,
            "zufrieden": 0.85, "glücklich": 0.85, "empfehle": 0.8, "freut": 0.8
        }
        
        negative_words = {
            "problem": -0.7, "fehler": -0.75, "nicht funktioniert": -0.85,
            "schlecht": -0.8, "enttäuscht": -0.85, "frustriert": -0.8,
            "beschwerde": -0.75, "schrecklich": -0.9, "furchtbar": -0.9,
            "unzufrieden": -0.85, "vergeblich": -0.75, "beendigung": -0.8
        }
        
        text_lower = text.lower()
        
        sentiment_score = 0
        word_count = 0
        
        for word, score in positive_words.items():
            if word in text_lower:
                sentiment_score += score
                word_count += 1
        
        for word, score in negative_words.items():
            if word in text_lower:
                sentiment_score += score
                word_count += 1
        
        if word_count == 0:
            return 0.0
        
        return min(1.0, max(-1.0, sentiment_score / word_count))
    
    @staticmethod
    def analyze_english(text: str) -> float:
        """Sentiment analysis for English text"""
        from textblob import TextBlob
        blob = TextBlob(text)
        return float(blob.sentiment.polarity)
    
    @classmethod
    def analyze(cls, text: str, language: str = "en") -> float:
        if language == "de":
            return cls.analyze_german(text)
        return cls.analyze_english(text)