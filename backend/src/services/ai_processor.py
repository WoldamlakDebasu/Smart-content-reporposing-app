import os
import openai
import json
import re
from typing import Dict, List, Any

class AIProcessor:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        )
        self.model = "gpt-4o-mini"  # Using the more cost-effective model
    
    def analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze content to extract themes, keywords, and insights"""
        try:
            prompt = f"""
            Analyze the following long-form content and extract key insights:

            Content:
            {content}

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
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert content analyst. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result = response.choices[0].message.content.strip()
            
            # Clean up the response to ensure it's valid JSON
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            
            return json.loads(result)
            
        except Exception as e:
            print(f"Error in content analysis: {str(e)}")
            # Return fallback analysis
            return {
                "main_theme": "Content Analysis",
                "key_topics": ["general", "information", "content"],
                "keywords": ["content", "information", "analysis"],
                "sentiment": "neutral",
                "tone": "professional",
                "target_audience": "General audience",
                "key_takeaways": ["Content contains valuable information"],
                "summary_short": "This content provides valuable information.",
                "summary_medium": "This content provides valuable information and insights for readers.",
                "summary_long": "This content provides valuable information and insights that can be useful for readers seeking to understand the topic better.",
                "suggested_formats": ["social_post", "email_snippet", "short_article"]
            }
    
    def repurpose_content(self, original_content: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate various repurposed content formats"""
        try:
            repurposed = {}
            
            # Generate social media posts
            repurposed['social_posts'] = self._generate_social_posts(original_content, analysis)
            
            # Generate email snippets
            repurposed['email_snippets'] = self._generate_email_snippets(original_content, analysis)
            
            # Generate short article
            repurposed['short_article'] = self._generate_short_article(original_content, analysis)
            
            # Generate infographic data
            repurposed['infographic_data'] = self._generate_infographic_data(original_content, analysis)
            
            return repurposed
            
        except Exception as e:
            print(f"Error in content repurposing: {str(e)}")
            return {
                'social_posts': [],
                'email_snippets': [],
                'short_article': {},
                'infographic_data': {}
            }
    
    def _generate_social_posts(self, content: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate social media posts for different platforms"""
        try:
            prompt = f"""
            Based on this content analysis, create social media posts for different platforms:
            
            Main Theme: {analysis.get('main_theme', '')}
            Key Topics: {', '.join(analysis.get('key_topics', []))}
            Keywords: {', '.join(analysis.get('keywords', []))}
            Tone: {analysis.get('tone', 'professional')}
            
            Original Content Summary: {analysis.get('summary_medium', '')}
            
            Create posts for:
            1. LinkedIn (professional, 1-2 paragraphs, include relevant hashtags)
            2. Twitter/X (concise, under 280 characters, include hashtags)
            3. Facebook (engaging, 1-2 paragraphs, conversational)
            4. Instagram (visual-focused caption, include hashtags and emojis)
            
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
                    {"role": "system", "content": "You are a social media expert. Create engaging posts. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            result = response.choices[0].message.content.strip()
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            
            posts_data = json.loads(result)
            
            # Convert to list format
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
    
    def _generate_email_snippets(self, content: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate email newsletter snippets"""
        try:
            prompt = f"""
            Create email newsletter snippets based on this content:
            
            Main Theme: {analysis.get('main_theme', '')}
            Key Takeaways: {', '.join(analysis.get('key_takeaways', []))}
            Tone: {analysis.get('tone', 'professional')}
            
            Create 2 different email snippets:
            1. Newsletter teaser (subject line + 2-3 sentences + CTA)
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
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an email marketing expert. Create compelling email content. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            result = response.choices[0].message.content.strip()
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            
            email_data = json.loads(result)
            
            # Convert to list format
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
    
    def _generate_short_article(self, content: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a short article based on the original content"""
        try:
            prompt = f"""
            Create a short article (300-500 words) based on this content analysis:
            
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
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a skilled content writer. Create engaging, well-structured articles. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6
            )
            
            result = response.choices[0].message.content.strip()
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
    
    def _generate_infographic_data(self, content: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data points suitable for infographics"""
        try:
            prompt = f"""
            Extract data points and statistics suitable for an infographic based on this analysis:
            
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
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data visualization expert. Create clear, engaging infographic content. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6
            )
            
            result = response.choices[0].message.content.strip()
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            
            return json.loads(result)
            
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

