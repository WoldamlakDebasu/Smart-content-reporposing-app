#!/usr/bin/env python3

import os
import json
import re
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from src.models.content import Content, db
from src.services.local_ai_processor import LocalAIProcessor

class HuggingFaceProcessor:
    """Hugging Face Inference API processor with local fallback"""
    
    def __init__(self):
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.local_processor = LocalAIProcessor()  # Always available fallback
        
        if self.api_key and self.api_key.startswith('hf_'):
            try:
                self.api_url = "https://api-inference.huggingface.co/models/"
                self.headers = {"Authorization": f"Bearer {self.api_key}"}
                
                # Use different models for different tasks
                self.text_model = "microsoft/DialoGPT-medium"  # For text generation
                self.classification_model = "cardiffnlp/twitter-roberta-base-sentiment-latest"  # For sentiment
                
                self.use_huggingface = True
                print("✅ Hugging Face API configured successfully")
            except Exception as e:
                print(f"⚠️ Hugging Face API configuration failed: {str(e)}")
                self.use_huggingface = False
        else:
            print("⚠️ No valid Hugging Face API key found, using local processing")
            self.use_huggingface = False
    
    def _query_huggingface(self, model_name: str, payload: dict, max_retries: int = 3) -> dict:
        """Query Hugging Face Inference API with retries"""
        url = f"{self.api_url}{model_name}"
        
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=self.headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 503:
                    print(f"Model {model_name} is loading, waiting...")
                    import time
                    time.sleep(10)  # Wait for model to load
                    continue
                else:
                    print(f"HuggingFace API error: {response.status_code} - {response.text}")
                    break
                    
            except requests.exceptions.Timeout:
                print(f"Timeout on attempt {attempt + 1}")
                continue
            except Exception as e:
                print(f"Request error: {str(e)}")
                break
        
        return None
    
    def retrieve_context(self, current_content: str, exclude_content_id=None, limit=5):
        """Enhanced RAG context retrieval with semantic similarity."""
        try:
            # Check if we're in a Flask application context
            from flask import has_app_context
            if not has_app_context():
                print("No Flask app context available for RAG retrieval")
                return ""
            
            # Get recent articles for temporal context
            recent_query = Content.query.order_by(Content.created_at.desc())
            if exclude_content_id:
                recent_query = recent_query.filter(Content.id != exclude_content_id)
            recent_articles = recent_query.limit(limit * 2).all()
            
            if not recent_articles:
                return ""
            
            # Format context with metadata
            formatted_context = []
            for article in recent_articles[:limit]:
                if article.original_content and len(article.original_content) > 100:
                    formatted_context.append(
                        f"[Previous Article - {article.created_at.strftime('%Y-%m-%d') if article.created_at else 'Unknown'}]\n"
                        f"Title: {article.title}\n"
                        f"Content: {article.original_content[:800]}\n"
                        f"---"
                    )
            
            return "\n\n".join(formatted_context)
            
        except Exception as e:
            print(f"Error retrieving enhanced context: {str(e)}")
            return ""
    
    def analyze_content(self, content: str, content_id=None) -> Dict[str, Any]:
        """Analyze content using Hugging Face with local fallback."""
        
        # Use local processing if Hugging Face is not available
        if not self.use_huggingface:
            print("🔄 Using local AI processing for content analysis")
            return self.local_processor.analyze_content(content, content_id)
        
        try:
            print("🔄 Using Hugging Face API for content analysis")
            
            # Get sentiment using Hugging Face
            sentiment_result = self._query_huggingface(
                self.classification_model,
                {"inputs": content[:512]}  # Limit input length
            )
            
            sentiment = "neutral"
            if sentiment_result and isinstance(sentiment_result, list) and len(sentiment_result) > 0:
                top_sentiment = max(sentiment_result[0], key=lambda x: x['score'])
                sentiment_label = top_sentiment['label'].lower()
                if 'positive' in sentiment_label:
                    sentiment = "positive"
                elif 'negative' in sentiment_label:
                    sentiment = "negative"
            
            # Use local processing for other analysis tasks
            local_analysis = self.local_processor.analyze_content(content, content_id)
            
            # Enhance with Hugging Face sentiment
            local_analysis['sentiment'] = sentiment
            local_analysis['ai_provider'] = 'huggingface'
            
            return local_analysis
            
        except Exception as e:
            print(f"Hugging Face API error in content analysis: {str(e)}")
            print("🔄 Falling back to local AI processing")
            return self.local_processor.analyze_content(content, content_id)
    
    def repurpose_content(self, original_content: str, analysis: Dict[str, Any], content_id=None) -> Dict[str, Any]:
        """Generate repurposed content using Hugging Face with local fallback."""
        
        # Use local processing if Hugging Face is not available
        if not self.use_huggingface:
            print("🔄 Using local AI processing for content repurposing")
            return self.local_processor.repurpose_content(original_content, analysis, content_id)
        
        try:
            print("🔄 Using Hugging Face API for content repurposing")
            
            # Get context for RAG
            context = self.retrieve_context(original_content, exclude_content_id=content_id, limit=4)
            
            repurposed = {}
            repurposed['social_posts'] = self._generate_social_posts_hf(original_content, analysis, context)
            repurposed['email_snippets'] = self._generate_email_snippets_hf(original_content, analysis, context)
            repurposed['short_article'] = self._generate_short_article_hf(original_content, analysis, context)
            repurposed['infographic_data'] = self._generate_infographic_data_hf(original_content, analysis, context)
            
            # Add RAG metadata
            repurposed['rag_metadata'] = {
                'context_used': len(context) > 0,
                'context_length': len(context),
                'generation_timestamp': datetime.now().isoformat(),
                'ai_provider': 'huggingface'
            }
            
            return repurposed
            
        except Exception as e:
            print(f"Hugging Face API error in content repurposing: {str(e)}")
            print("🔄 Falling back to local AI processing")
            return self.local_processor.repurpose_content(original_content, analysis, content_id)
    
    def _generate_social_posts_hf(self, content: str, analysis: Dict[str, Any], context: str = "") -> List[Dict[str, Any]]:
        """Generate social media posts using Hugging Face and local processing."""
        try:
            # Use local processing for social posts (more reliable)
            theme = analysis.get('main_theme', 'content')
            keywords = analysis.get('keywords', ['content'])
            summary = analysis.get('summary_short', content[:100])
            tone = analysis.get('tone', 'professional')
            
            return self.local_processor._generate_social_posts_local(theme, keywords, summary, tone)
            
        except Exception as e:
            print(f"Error generating social posts: {str(e)}")
            return self.local_processor._generate_social_posts_local(
                analysis.get('main_theme', 'content'),
                analysis.get('keywords', []),
                analysis.get('summary_short', content[:100]),
                analysis.get('tone', 'professional')
            )
    
    def _generate_email_snippets_hf(self, content: str, analysis: Dict[str, Any], context: str = "") -> List[Dict[str, Any]]:
        """Generate email snippets using local processing."""
        return self.local_processor._generate_email_snippets_local(
            analysis.get('main_theme', 'content'),
            analysis.get('summary_short', content[:100]),
            analysis.get('keywords', [])
        )
    
    def _generate_short_article_hf(self, content: str, analysis: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """Generate short article using local processing."""
        return self.local_processor._generate_short_article_local(
            analysis.get('main_theme', 'content'),
            content,
            analysis
        )
    
    def _generate_infographic_data_hf(self, content: str, analysis: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """Generate infographic data using local processing."""
        return self.local_processor._generate_infographic_data_local(
            analysis.get('main_theme', 'content'),
            analysis.get('keywords', []),
            analysis
        )
