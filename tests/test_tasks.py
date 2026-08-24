import pytest
from app.services.classifier import OllamaClassifier
from app.services.sentiment import SentimentAnalyzer
from app.services.multilingual import SentimentAnalyzerAdvanced

def test_sentiment_analyzer_english():
    """Test English sentiment analysis"""
    positive_text = "Great! Everything works perfectly!"
    result = SentimentAnalyzer.analyze(positive_text, "en")
    assert result > 0, "Should be positive"

def test_sentiment_analyzer_german():
    """Test German sentiment analysis"""
    negative_text = "Das ist ein großes Problem! Nichts funktioniert!"
    result = SentimentAnalyzerAdvanced.analyze_german(negative_text)
    assert result < 0, "Should be negative"

def test_classifier_fallback():
    """Test classifier fallback when Ollama is unavailable"""
    clf = OllamaClassifier()
    # This will fail gracefully if Ollama is not available
    result = clf._default_classification("en")
    assert result["category"] == "General"
    assert result["confidence"] == 0.3