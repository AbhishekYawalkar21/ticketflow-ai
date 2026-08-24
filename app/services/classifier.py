import requests
import json
from app.config import settings
from typing import Dict, Optional
import logging
import re

logger = logging.getLogger(__name__)

class OllamaClassifier:
    """Local LLM-based ticket classifier using Ollama"""
    
    def __init__(self, model: str = None):
        self.model = model or settings.OLLAMA_MODEL
        self.base_url = settings.OLLAMA_BASE_URL
        self.api_url = f"{self.base_url}/api/generate"
    
    def classify_ticket(self, subject: str, content: str, language: str = "en") -> Dict:
        """
        Classify ticket using Ollama LLM
        
        Returns:
        {
            "category": str,
            "priority": str,
            "suggested_response": str,
            "confidence": float,
            "language": str
        }
        """
        
        # Multilingual prompt
        if language == "de":
            prompt = f"""
Klassifizieren Sie das folgende Support-Ticket:

BETREFF: {subject}
INHALT: {content}

Antworten Sie in JSON-Format:
{{
    "kategorie": "Technischer Support|Abrechnung|Allgemein|Feature-Anfrage",
    "priorität": "Niedrig|Mittel|Hoch|Dringend",
    "lösung": "Kurze vorgeschlagene Antwort",
    "sicherheit": 0.0-1.0
}}
"""
        else:
            prompt = f"""
Classify the following support ticket:

SUBJECT: {subject}
CONTENT: {content}

Respond in JSON format:
{{
    "category": "Technical Support|Billing|General|Feature Request",
    "priority": "Low|Medium|High|Urgent",
    "suggested_response": "Brief suggested response",
    "confidence": 0.0-1.0
}}
"""
        
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3
                },
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get("response", "")
            
            # Parse JSON from response
            try:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    
                    # Map German to English keys
                    if language == "de":
                        return {
                            "category": parsed.get("kategorie", "General"),
                            "priority": self._map_priority(parsed.get("priorität", "Mittel")),
                            "suggested_response": parsed.get("lösung", ""),
                            "confidence": float(parsed.get("sicherheit", 0.5)),
                            "language": language
                        }
                    else:
                        return {
                            "category": parsed.get("category", "General"),
                            "priority": self._map_priority(parsed.get("priority", "Medium")),
                            "suggested_response": parsed.get("suggested_response", ""),
                            "confidence": float(parsed.get("confidence", 0.5)),
                            "language": language
                        }
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse LLM response: {response_text}")
                return self._default_classification(language)
            
        except requests.RequestException as e:
            logger.error(f"Ollama API error: {str(e)}")
            return self._default_classification(language)
    
    def _map_priority(self, priority_str: str) -> str:
        """Map priority text to standard priority"""
        priority_map = {
            "Niedrig": "low", "Low": "low",
            "Mittel": "medium", "Medium": "medium",
            "Hoch": "high", "High": "high",
            "Dringend": "urgent", "Urgent": "urgent"
        }
        return priority_map.get(priority_str, "medium")
    
    def _default_classification(self, language: str) -> Dict:
        """Fallback classification"""
        return {
            "category": "General",
            "priority": "medium",
            "suggested_response": "We have received your ticket and will respond shortly.",
            "confidence": 0.3,
            "language": language
        }

# Singleton instance
classifier = OllamaClassifier()