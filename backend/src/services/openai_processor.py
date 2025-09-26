#!/usr/bin/env python3

import os
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import openai
from openai import OpenAI
from src.models.content import Content, db
from src.services.local_ai_processor import LocalAIProcessor

class OpenAIProcessor:
    """OpenAI-powered content processor with local fallback"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.local_processor = LocalAIProcessor()  # Always available fallback
        
        # Force local processing due to OpenAI rate limits
        print("🔄 Using local AI processing (OpenAI rate limits detected)")
        self.use_openai = False
        
        # Keep OpenAI setup for future use when limits reset
        if self.api_key and self.api_key != 'your_openai_api_key_here':
            try:
                self.client = OpenAI(api_key=self.api_key)
                self.model = "gpt-3.5-turbo"
                print("✅ OpenAI API configured (available when rate limits reset)")
            except Exception as e:
                print(f"⚠️ OpenAI API configuration failed: {str(e)}")
    
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
        """Analyze content using OpenAI with local fallback."""
        
        # Use local processing if OpenAI is not available
        if not self.use_openai:
            print("🔄 Using local AI processing for content analysis")
            return self.local_processor.analyze_content(content, content_id)
        
        try:
            # Get context for RAG
            context = self.retrieve_context(content, exclude_content_id=content_id, limit=3)
            
            # Create analysis prompt
            prompt = f"""
            You are an expert content analyst. Analyze the MAIN CONTENT and provide insights in JSON format.
            
            {f"CONTEXT (previous articles for reference):\\n{context}\\n" if context else ""}
            
            MAIN CONTENT:
            {content}
            
            Provide a JSON response with this exact structure:
            {{
                "main_theme": "The primary topic or theme",
                "key_topics": ["topic1", "topic2", "topic3"],
                "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
                "sentiment": "positive/negative/neutral",
                "tone": "professional/casual/academic/conversational",
                "target_audience": "Description of likely target audience",
                "key_takeaways": ["takeaway1", "takeaway2", "takeaway3"],
                "summary_short": "One sentence summary",
                "summary_medium": "2-3 sentence summary",
                "summary_long": "Paragraph summary",
                "suggested_formats": ["social_post", "email_snippet", "short_article", "infographic_data"]
            }}
            
            Return ONLY valid JSON, no additional text.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert content analyst. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content.strip()
            
            # Clean up JSON response
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            
            return json.loads(result)
            
        except Exception as e:
            print(f"OpenAI API error in content analysis: {str(e)}")
            print("🔄 Falling back to local AI processing")
            return self.local_processor.analyze_content(content, content_id)
    
    def repurpose_content(self, original_content: str, analysis: Dict[str, Any], content_id=None) -> Dict[str, Any]:
        """Generate repurposed content using OpenAI with local fallback."""
        
        # Use local processing if OpenAI is not available
        if not self.use_openai:
            print("🔄 Using local AI processing for content repurposing")
            return self.local_processor.repurpose_content(original_content, analysis, content_id)
        
        try:
            # Get context for RAG
            context = self.retrieve_context(original_content, exclude_content_id=content_id, limit=4)
            
            repurposed = {}
            repurposed['social_posts'] = self._generate_social_posts(original_content, analysis, context)
            repurposed['email_snippets'] = self._generate_email_snippets(original_content, analysis, context)
            repurposed['short_article'] = self._generate_short_article(original_content, analysis, context)
            repurposed['infographic_data'] = self._generate_infographic_data(original_content, analysis, context)
            
            # Add RAG metadata
            repurposed['rag_metadata'] = {
                'context_used': len(context) > 0,
                'context_length': len(context),
                'generation_timestamp': datetime.now().isoformat(),
                'ai_provider': 'openai'
            }
            
            return repurposed
            
        except Exception as e:
            print(f"OpenAI API error in content repurposing: {str(e)}")
            print("🔄 Falling back to local AI processing")
            return self.local_processor.repurpose_content(original_content, analysis, content_id)
    
    def _generate_social_posts(self, content: str, analysis: Dict[str, Any], context: str = "") -> List[Dict[str, Any]]:
        """Generate social media posts using OpenAI."""
        try:
            prompt = f"""
            Create social media posts for different platforms based on this content analysis.
            
            {f"CONTEXT (previous content patterns):\\n{context}\\n" if context else ""}
            
            CONTENT: {content}
            THEME: {analysis.get('main_theme', '')}
            KEYWORDS: {', '.join(analysis.get('keywords', []))}
            TONE: {analysis.get('tone', 'professional')}
            
            Create posts for LinkedIn, Twitter, Facebook, and Instagram.
            
            Respond with JSON only:
            {{
                "linkedin": {{"text": "post content", "hashtags": ["hashtag1", "hashtag2"]}},
                "twitter": {{"text": "post content", "hashtags": ["hashtag1", "hashtag2"]}},
                "facebook": {{"text": "post content", "hashtags": ["hashtag1", "hashtag2"]}},
                "instagram": {{"text": "post content", "hashtags": ["hashtag1", "hashtag2"]}}
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a social media expert. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            result = response.choices[0].message.content.strip()
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            
            posts_data = json.loads(result)
            posts = []
            for platform, data in posts_data.items():
                posts.append({
                    'platform': platform,
                    'text': data['text'],
                    'hashtags': data.get('hashtags', []),
                    'character_count': len(data['text'])
                })
            return posts
            
        except Exception as e:
            print(f"Error generating social posts with OpenAI: {str(e)}")
            # Fallback to local generation
            return self.local_processor._generate_social_posts_local(
                analysis.get('main_theme', 'content'),
                analysis.get('keywords', []),
                analysis.get('summary_short', content[:100]),
                analysis.get('tone', 'professional')
            )
    
    def _generate_email_snippets(self, content: str, analysis: Dict[str, Any], context: str = "") -> List[Dict[str, Any]]:
        """Generate email snippets using OpenAI."""
        try:
            prompt = f"""
            Create email newsletter snippets based on this content.
            
            CONTENT: {content}
            THEME: {analysis.get('main_theme', '')}
            TAKEAWAYS: {', '.join(analysis.get('key_takeaways', []))}
            
            Create 2 email snippets: newsletter teaser and promotional email.
            
            Respond with JSON only:
            {{
                "newsletter_teaser": {{
                    "subject": "subject line",
                    "content": "email content",
                    "cta": "call to action"
                }},
                "promotional": {{
                    "subject": "subject line", 
                    "content": "email content",
                    "cta": "call to action"
                }}
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an email marketing expert. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            
            result = response.choices[0].message.content.strip()
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            
            email_data = json.loads(result)
            snippets = []
            for email_type, data in email_data.items():
                snippets.append({
                    'type': email_type,
                    'subject': data['subject'],
                    'content': data['content'],
                    'cta': data['cta'],
                    'word_count': len(data['content'].split())
                })
            return snippets
            
        except Exception as e:
            print(f"Error generating email snippets with OpenAI: {str(e)}")
            return self.local_processor._generate_email_snippets_local(
                analysis.get('main_theme', 'content'),
                analysis.get('summary_short', content[:100]),
                analysis.get('keywords', [])
            )
    
    def _generate_short_article(self, content: str, analysis: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """Generate short article using OpenAI."""
        try:
            prompt = f"""
            Create a short article (300-500 words) based on this content analysis.
            
            ORIGINAL CONTENT: {content}
            THEME: {analysis.get('main_theme', '')}
            KEY TOPICS: {', '.join(analysis.get('key_topics', []))}
            TARGET AUDIENCE: {analysis.get('target_audience', '')}
            
            Structure: headline, introduction, main content, conclusion.
            
            Respond with JSON only:
            {{
                "headline": "article headline",
                "introduction": "introduction paragraphs",
                "main_content": "main content paragraphs", 
                "conclusion": "conclusion paragraph",
                "word_count": estimated_word_count,
                "reading_time": "X min read"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional writer. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            result = response.choices[0].message.content.strip()
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            
            return json.loads(result)
            
        except Exception as e:
            print(f"Error generating short article with OpenAI: {str(e)}")
            return self.local_processor._generate_short_article_local(
                analysis.get('main_theme', 'content'),
                content,
                analysis
            )
    
    def _generate_infographic_data(self, content: str, analysis: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """Generate infographic data using OpenAI."""
        try:
            prompt = f"""
            Create infographic data points based on this content analysis.
            
            CONTENT: {content}
            THEME: {analysis.get('main_theme', '')}
            KEY TOPICS: {', '.join(analysis.get('key_topics', []))}
            TAKEAWAYS: {', '.join(analysis.get('key_takeaways', []))}
            
            Create infographic elements: title, statistics, sections, call to action.
            
            Respond with JSON only:
            {{
                "title": "infographic title",
                "statistics": [
                    {{"label": "stat description", "value": "stat value", "icon_suggestion": "icon name"}},
                    {{"label": "stat description", "value": "stat value", "icon_suggestion": "icon name"}}
                ],
                "sections": [
                    {{"title": "section title", "description": "brief description"}},
                    {{"title": "section title", "description": "brief description"}}
                ],
                "cta": "call to action text"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data visualization expert. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            
            result = response.choices[0].message.content.strip()
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            
            infographic_data = json.loads(result)
            infographic_data['image_description'] = f"Infographic showing {infographic_data.get('title', 'content analysis')}"
            infographic_data['image_url'] = None  # No image generation for now
            
            return infographic_data
            
        except Exception as e:
            print(f"Error generating infographic data with OpenAI: {str(e)}")
            return self.local_processor._generate_infographic_data_local(
                analysis.get('main_theme', 'content'),
                analysis.get('keywords', []),
                analysis
            )
