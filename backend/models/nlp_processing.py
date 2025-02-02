from transformers import pipeline
from typing import List, Dict, Optional
import numpy as np
from .rag_database import RAGDatabase
from ..utils.config import MAX_SUMMARY_LENGTH, MIN_SUMMARY_LENGTH

class NLPProcessor:
    def __init__(self):
        # Initialize summarization pipeline
        self.summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            device=-1  # Use CPU. Change to 0 for GPU
        )
        
        # Initialize zero-shot classification for key points
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=-1
        )
        
        # Initialize RAG database connection
        self.db = RAGDatabase()
    
    def generate_summary(self, 
                        text: str,
                        note_id: Optional[int] = None,
                        max_length: int = MAX_SUMMARY_LENGTH,
                        min_length: int = MIN_SUMMARY_LENGTH) -> Dict:
        """Generate a concise summary of the text."""
        try:
            # Split long text into chunks if needed
            max_input_length = self.summarizer.tokenizer.model_max_length
            chunks = [text[i:i + max_input_length] for i in range(0, len(text), max_input_length)]
            
            # Generate summary for each chunk
            summaries = []
            for chunk in chunks:
                summary = self.summarizer(
                    chunk,
                    max_length=max_length // len(chunks),
                    min_length=min_length // len(chunks),
                    do_sample=False
                )[0]["summary_text"]
                summaries.append(summary)
            
            # Combine summaries
            final_summary = " ".join(summaries)
            
            # Extract key points
            key_points = self._extract_key_points(text)
            
            # Update database if note_id provided
            if note_id:
                self.db.update_summary(note_id, final_summary)
            
            return {
                "summary": final_summary,
                "key_points": key_points,
                "original_length": len(text.split()),
                "summary_length": len(final_summary.split())
            }
            
        except Exception as e:
            raise RuntimeError(f"Summarization failed: {str(e)}")
    
    def _extract_key_points(self, text: str, max_points: int = 5) -> List[str]:
        """Extract key points from text using zero-shot classification."""
        # Define candidate labels for classification
        labels = [
            "main point",
            "key detail",
            "important fact",
            "crucial information",
            "significant finding"
        ]
        
        # Split text into sentences
        sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 10]
        
        key_points = []
        for sentence in sentences:
            result = self.classifier(
                sentence,
                labels,
                multi_label=True
            )
            
            # If any label has high confidence, consider it a key point
            if max(result["scores"]) > 0.8:
                key_points.append(sentence)
            
            if len(key_points) >= max_points:
                break
        
        return key_points
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment and emotion in the text."""
        sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=-1
        )
        
        # Get overall sentiment
        sentiment = sentiment_analyzer(text)[0]
        
        return {
            "sentiment": sentiment["label"],
            "confidence": float(sentiment["score"])
        }
    
    def extract_topics(self, text: str, num_topics: int = 3) -> List[str]:
        """Extract main topics from the text."""
        # Define common topic categories
        topic_categories = [
            "technology", "science", "business", "health",
            "education", "politics", "environment", "society",
            "culture", "sports"
        ]
        
        result = self.classifier(
            text,
            topic_categories,
            multi_label=True
        )
        
        # Return top N topics with scores
        topics = []
        for label, score in zip(result["labels"], result["scores"]):
            if score > 0.3:  # Confidence threshold
                topics.append({
                    "topic": label,
                    "confidence": float(score)
                })
        
        return sorted(topics, key=lambda x: x["confidence"], reverse=True)[:num_topics]
    
    def generate_tags(self, text: str, max_tags: int = 5) -> List[str]:
        """Generate relevant tags for the content."""
        # Extract topics
        topics = self.extract_topics(text)
        
        # Get key points
        key_points = self._extract_key_points(text)
        
        # Combine and process to create tags
        tags = set()
        
        # Add topics as tags
        for topic in topics:
            tags.add(topic["topic"].lower())
        
        # Extract potential tags from key points
        if key_points:
            classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=-1
            )
            
            for point in key_points:
                result = classifier(
                    point,
                    candidate_labels=["concept", "term", "topic", "theme"],
                    multi_label=True
                )
                if max(result["scores"]) > 0.7:
                    # Add the first significant word as a tag
                    words = point.split()
                    if words:
                        tags.add(words[0].lower())
        
        return list(tags)[:max_tags]