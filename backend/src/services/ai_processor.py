import os
import json
import re
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from datetime import datetime, timedelta
import hashlib

from src.models.content import Content, db
from src.services.local_ai_processor import LocalAIProcessor


class AIProcessor:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.local_processor = LocalAIProcessor()  
        
        if self.api_key and self.api_key != 'your_gemini_api_key_here':
            try:
                genai.configure(api_key=self.api_key)
                self.model = "gemini-pro"
                self.embedding_model = "models/embedding-001"
                self.use_gemini = True
                print("✅ Gemini API configured successfully")
            except Exception as e:
                print(f"⚠️ Gemini API configuration failed: {str(e)}")
                self.use_gemini = False
        else:
            print("⚠️ No valid Gemini API key found, using local processing")
            self.use_gemini = False
    
    def generate_content_summary(self, content: str) -> str:
        """Generate a concise summary for RAG context storage."""
        try:
            summary_prompt = f"""
            Create a concise 3-5 sentence summary of this content that captures the main theme, 
            key insights, and target audience. This will be used for content similarity matching.
            
            Content: {content[:1000]}...
            
            Summary:
            """
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(summary_prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return content[:200] + "..."

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
            
            # Use Gemini to find semantically similar content
            context_candidates = []
            for article in recent_articles:
                if article.original_content and len(article.original_content) > 100:
                    context_candidates.append({
                        'title': article.title,
                        'content': article.original_content[:800],
                        'created_at': article.created_at.strftime('%Y-%m-%d') if article.created_at else 'Unknown',
                        'id': article.id
                    })
            
            if not context_candidates:
                return ""
            
            # Use Gemini to rank relevance
            relevant_context = self._rank_context_relevance(current_content, context_candidates, limit)
            
            # Format context with metadata
            formatted_context = []
            for ctx in relevant_context:
                formatted_context.append(
                    f"[Previous Article - {ctx['created_at']}]\n"
                    f"Title: {ctx['title']}\n"
                    f"Content: {ctx['content']}\n"
                    f"---"
                )
            
            return "\n\n".join(formatted_context)
            
        except Exception as e:
            print(f"Error retrieving enhanced context: {str(e)}")
            # Fallback to simple retrieval
            return self._simple_context_retrieval(exclude_content_id, limit)
    
    def _rank_context_relevance(self, current_content: str, candidates: List[Dict], limit: int) -> List[Dict]:
        """Use Gemini to rank context relevance."""
        try:
            if len(candidates) <= limit:
                return candidates
            
            # Create a prompt for Gemini to rank relevance
            candidates_text = ""
            for i, candidate in enumerate(candidates):
                candidates_text += f"{i+1}. Title: {candidate['title']}\nContent: {candidate['content'][:300]}...\n\n"
            
            ranking_prompt = f"""
            You are a content similarity expert. Given the CURRENT CONTENT and a list of PREVIOUS ARTICLES, 
            rank the previous articles by their relevance and similarity to the current content.
            
            CURRENT CONTENT:
            {current_content[:500]}...
            
            PREVIOUS ARTICLES:
            {candidates_text}
            
            Return ONLY a JSON array of the top {limit} most relevant article numbers (1-{len(candidates)}) 
            in order of relevance (most relevant first).
            
            Example: [3, 1, 5]
            """
            
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(ranking_prompt)
            result = response.text.strip()
            
            # Parse the ranking
            if result.startswith('[') and result.endswith(']'):
                rankings = json.loads(result)
                relevant_articles = []
                for rank in rankings[:limit]:
                    if 1 <= rank <= len(candidates):
                        relevant_articles.append(candidates[rank - 1])
                return relevant_articles
            
        except Exception as e:
            print(f"Error in context ranking: {str(e)}")
        
        # Fallback: return first N candidates
        return candidates[:limit]
    
    def _simple_context_retrieval(self, exclude_content_id=None, limit=3):
        """Fallback simple context retrieval."""
        try:
            query = Content.query.order_by(Content.created_at.desc())
            if exclude_content_id:
                query = query.filter(Content.id != exclude_content_id)
            articles = query.limit(limit).all()
            context = "\n\n".join([
                f"Title: {a.title}\nContent: {a.original_content[:500]}..." 
                for a in articles if a.original_content
            ])
            return context
        except Exception as e:
            print(f"Error in simple context retrieval: {str(e)}")
            return ""

    def analyze_content(self, content: str, content_id=None) -> Dict[str, Any]:
        """Analyze content to extract themes, keywords, and insights, using enhanced RAG context."""
        
        # Try Gemini first if available, otherwise use local processing
        if not self.use_gemini:
            print("🔄 Using local AI processing for content analysis")
            return self.local_processor.analyze_content(content, content_id)
        
        try:
            # Use enhanced RAG context retrieval
            context = self.retrieve_context(content, exclude_content_id=content_id, limit=3)
            
            # Enhanced prompt with better RAG integration
            prompt = f"""
            You are an expert content analyst with access to previous content for context. 
            Analyze the MAIN CONTENT using insights from PREVIOUS ARTICLES to provide comprehensive analysis.

            PREVIOUS ARTICLES (for context and pattern recognition):
            {context}

            MAIN CONTENT (current analysis target):
            {content}

            ANALYSIS INSTRUCTIONS:
            1. Use previous articles to understand content patterns and themes
            2. Identify connections and differences with previous content
            3. Extract insights that build upon previous knowledge
            4. Suggest content formats that complement existing content

            Please provide a JSON response with the following structure:
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
            
            Ensure the response is valid JSON only, no additional text.
            """
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            result = response.text.strip()
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            return json.loads(result)
        except Exception as e:
            print(f"Gemini API error in content analysis: {str(e)}")
            print("🔄 Falling back to local AI processing")
            # Use local processor as fallback
            return self.local_processor.analyze_content(content, content_id)
    
    def _get_fallback_analysis(self, content: str) -> Dict[str, Any]:
        """Provide intelligent fallback analysis when API is unavailable."""
        words = content.lower().split()
        
        # Extract potential keywords (longer words, excluding common stop words)
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'a', 'an'}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words][:5]
        
        # Determine basic sentiment
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'positive', 'success', 'growth']
        negative_words = ['bad', 'terrible', 'awful', 'negative', 'problem', 'issue', 'failure', 'decline']
        
        sentiment = "neutral"
        if any(word in words for word in positive_words):
            sentiment = "positive"
        elif any(word in words for word in negative_words):
            sentiment = "negative"
        
        return {
            "main_theme": f"Analysis of {keywords[0] if keywords else 'content'}",
            "key_topics": keywords[:3] if len(keywords) >= 3 else ["content", "information", "analysis"],
            "keywords": keywords if keywords else ["content", "information", "analysis"],
            "sentiment": sentiment,
            "tone": "professional",
            "target_audience": "General audience interested in the topic",
            "key_takeaways": [f"Content discusses {keywords[0] if keywords else 'important topics'}", "Provides valuable insights", "Suitable for repurposing"],
            "summary_short": content[:100] + "..." if len(content) > 100 else content,
            "summary_medium": content[:200] + "..." if len(content) > 200 else content,
            "summary_long": content[:300] + "..." if len(content) > 300 else content,
            "suggested_formats": ["social_post", "email_snippet", "short_article", "infographic_data"]
        }
    
    def repurpose_content(self, original_content: str, analysis: Dict[str, Any], content_id=None) -> Dict[str, Any]:
        """Generate various repurposed content formats using enhanced RAG context."""
        
        # Use local processing if Gemini is not available
        if not self.use_gemini:
            print("🔄 Using local AI processing for content repurposing")
            return self.local_processor.repurpose_content(original_content, analysis, content_id)
        
        try:
            # Use enhanced RAG context for content generation
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
                'generation_timestamp': datetime.now().isoformat()
            }
            
            return repurposed
        except Exception as e:
            print(f"Gemini API error in content repurposing: {str(e)}")
            print("🔄 Falling back to local AI processing")
            # Use local processor as fallback
            return self.local_processor.repurpose_content(original_content, analysis, content_id)
    
    def _get_fallback_repurposed_content(self, content: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback repurposed content when API is unavailable."""
        theme = analysis.get('main_theme', 'content')
        keywords = analysis.get('keywords', ['content'])
        summary = analysis.get('summary_short', content[:100])
        
        return {
            'social_posts': [
                {
                    'platform': 'linkedin',
                    'text': f"Exploring insights on {theme}. {summary} #professional #{keywords[0] if keywords else 'content'}",
                    'hashtags': [keywords[0] if keywords else 'content', 'insights'],
                    'character_count': 150
                },
                {
                    'platform': 'twitter',
                    'text': f"Key insights on {theme}: {summary[:100]}... #{keywords[0] if keywords else 'content'}",
                    'hashtags': [keywords[0] if keywords else 'content'],
                    'character_count': 120
                },
                {
                    'platform': 'facebook',
                    'text': f"Sharing some thoughts on {theme}. {summary} What are your thoughts on this topic?",
                    'hashtags': [keywords[0] if keywords else 'content'],
                    'character_count': 180
                },
                {
                    'platform': 'instagram',
                    'text': f"✨ Diving into {theme} today! {summary} 📚 #{keywords[0] if keywords else 'content'} #insights",
                    'hashtags': [keywords[0] if keywords else 'content', 'insights'],
                    'character_count': 160
                }
            ],
            'email_snippets': [
                {
                    'type': 'newsletter_teaser',
                    'subject': f"New insights on {theme}",
                    'content': f"We've been exploring {theme} and wanted to share some key insights with you. {summary}",
                    'cta': 'Read More',
                    'word_count': 25
                }
            ],
            'short_article': {
                'headline': f"Understanding {theme}: Key Insights and Takeaways",
                'introduction': f"In today's rapidly evolving landscape, {theme} has become increasingly important. {summary}",
                'main_content': f"The key aspects of {theme} include several important considerations. {content[:300]}...",
                'conclusion': f"These insights about {theme} provide valuable understanding for moving forward.",
                'word_count': 300,
                'reading_time': '2 min read'
            },
            'infographic_data': {
                'title': f"Key Facts About {theme}",
                'statistics': [
                    {'label': 'Main Focus', 'value': theme, 'icon_suggestion': 'target'},
                    {'label': 'Key Topics', 'value': str(len(keywords)), 'icon_suggestion': 'list'}
                ],
                'sections': [
                    {'title': 'Overview', 'description': summary},
                    {'title': 'Key Points', 'description': f"Important aspects of {theme}"}
                ],
                'cta': 'Learn More',
                'image_description': f"Infographic showing key insights about {theme}",
                'image_url': None
            },
            'rag_metadata': {
                'context_used': False,
                'context_length': 0,
                'generation_timestamp': datetime.now().isoformat(),
                'fallback_used': True
            }
        }
    
    def _generate_social_posts(self, content: str, analysis: Dict[str, Any], context: str = "") -> List[Dict[str, Any]]:
        """Generate social media posts for different platforms using enhanced RAG context."""
        try:
            prompt = f"""
            You are an expert social media strategist and marketing specialist with access to previous content patterns and you have more than a decade of experience on marketing and lead generation. 
            Create platform-optimized social media posts that build upon previous content themes while highlighting new insights.

            PREVIOUS CONTENT PATTERNS (for consistency and evolution):
            {context}

            CURRENT CONTENT (to be repurposed):
            {content}

            CONTENT ANALYSIS:
            - Main Theme: {analysis.get('main_theme', '')}
            - Key Topics: {', '.join(analysis.get('key_topics', []))}
            - Keywords: {', '.join(analysis.get('keywords', []))}
            - Tone: {analysis.get('tone', 'professional')}
            - Target Audience: {analysis.get('target_audience', '')}
            - Content Summary: {analysis.get('summary_medium', '')}

            STRATEGY INSTRUCTIONS:
            1. Reference or build upon themes from previous content when relevant
            2. Maintain consistent brand voice across all posts
            3. Create posts that complement rather than duplicate previous content
            4. Use insights from previous content to enhance current messaging

            Create posts for:
            1. LinkedIn (professional, 3-4 paragraphs, include relevant hashtags)
            2. Twitter/X (concise, under 280 characters, include hashtags)
            3. Facebook (engaging, 3-4 paragraphs, conversational)
            4. Instagram (visual-focused caption, include hashtags and emojis)

            Respond with JSON only:
            {{
                "linkedin": {{"text": "post content", "hashtags": ["hashtag1", "hashtag2"]}},
                "twitter": {{"text": "post content", "hashtags": ["hashtag1", "hashtag2"]}},
                "facebook": {{"text": "post content", "hashtags": ["hashtag1", "hashtag2"]}},
                "instagram": {{"text": "post content", "hashtags": ["hashtag1", "hashtag2"]}}
            }}
            """
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            result = response.text.strip()
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
            print(f"Error generating social posts: {str(e)}")
            return [
                {
                    'platform': 'linkedin',
                    'text': f"Interesting insights on {analysis.get('main_theme', 'this topic')}. {analysis.get('summary_short', '')}",
                    'hashtags': analysis.get('keywords', [])[:3],
                    'character_count': 100
                }
            ]
    
    def _generate_email_snippets(self, content: str, analysis: Dict[str, Any], context: str = "") -> List[Dict[str, Any]]:
        """Generate email newsletter snippets using RAG context."""
        try:
            prompt = f"""
            You are an email marketing expert. Use the CONTEXT and MAIN CONTENT below to create compelling email newsletter snippets.

            CONTEXT (previous articles):
            {context}

            MAIN CONTENT (user upload):
            {content}

            Main Theme: {analysis.get('main_theme', '')}
            Key Takeaways: {', '.join(analysis.get('key_takeaways', []))}
            Tone: {analysis.get('tone', 'professional')}

            Create 2 different email snippets:
            1. Newsletter teaser (subject line + 3-4 sentences + CTA)
            2. Promotional email (subject line + engaging content + strong CTA)

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
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            result = response.text.strip()
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
            print(f"Error generating email snippets: {str(e)}")
            return [
                {
                    'type': 'newsletter_teaser',
                    'subject': f"New insights on {analysis.get('main_theme', 'this topic')}",
                    'content': analysis.get('summary_medium', 'Check out our latest content.'),
                    'cta': 'Read More',
                    'word_count': 20
                }
            ]
    
    def _generate_short_article(self, content: str, analysis: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """Generate a short article based on the original content and RAG context."""
        try:
            prompt = f"""
            You are an expert professional writer with more than a decade of experience. Use the CONTEXT and MAIN CONTENT below to create a short article (300-500 words) based on this content analysis.

            CONTEXT (previous articles):
            {context}

            MAIN CONTENT (user upload):
            {content}

            Main Theme: {analysis.get('main_theme', '')}
            Key Topics: {', '.join(analysis.get('key_topics', []))}
            Key Takeaways: {', '.join(analysis.get('key_takeaways', []))}
            Target Audience: {analysis.get('target_audience', '')}

            Structure:
            - Compelling headline
            - Engaging introduction (1-2 paragraphs)
            - Main content (2-3 paragraphs)
            - Conclusion with actionable insights

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
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            result = response.text.strip()
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            return json.loads(result)
        except Exception as e:
            print(f"Error generating short article: {str(e)}")
            return {
                'headline': f"Understanding {analysis.get('main_theme', 'This Topic')}",
                'introduction': analysis.get('summary_long', 'This article explores important concepts.'),
                'main_content': 'The main insights and key points are discussed in detail.',
                'conclusion': 'These insights provide valuable understanding for readers.',
                'word_count': 300,
                'reading_time': '2 min read'
            }
    
    def _generate_infographic_data(self, content: str, analysis: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """Generate data points suitable for infographics using RAG context."""
        try:
            prompt = f"""
            You are a data visualization expert. Use the CONTEXT and MAIN CONTENT below to extract data points and statistics suitable for an infographic.

            CONTEXT (previous articles):
            {context}

            MAIN CONTENT (user upload):
            {content}

            Main Theme: {analysis.get('main_theme', '')}
            Key Topics: {', '.join(analysis.get('key_topics', []))}
            Key Takeaways: {', '.join(analysis.get('key_takeaways', []))}

            Create infographic elements:
            - Title
            - 3-5 key statistics or data points
            - 3-4 main sections with brief descriptions
            - Call to action

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
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            result = response.text.strip()
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            infographic_data = json.loads(result)
            # Generate image description for infographic instead of actual image
            image_description = f"Infographic design suggestion: {infographic_data.get('title', 'Content Analysis')} with theme {analysis.get('main_theme', '')}. Include visual elements for statistics and key points."
            infographic_data['image_description'] = image_description
            infographic_data['image_url'] = None  # No image generation, just description
            return infographic_data
        except Exception as e:
            print(f"Error generating infographic data: {str(e)}")
            return {
                'title': f"Key Insights: {analysis.get('main_theme', 'Content Analysis')}",
                'statistics': [
                    {'label': 'Key Topics Covered', 'value': str(len(analysis.get('key_topics', []))), 'icon_suggestion': 'chart'},
                    {'label': 'Main Takeaways', 'value': str(len(analysis.get('key_takeaways', []))), 'icon_suggestion': 'lightbulb'}
                ],
                'sections': [
                    {'title': 'Main Theme', 'description': analysis.get('main_theme', 'Content analysis')},
                    {'title': 'Target Audience', 'description': analysis.get('target_audience', 'General audience')}
                ],
                'cta': 'Learn More'
            }


