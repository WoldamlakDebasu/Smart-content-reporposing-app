#!/usr/bin/env python3

import re
import json
from typing import Dict, List, Any
from datetime import datetime
import nltk
from collections import Counter

class LocalAIProcessor:
    """Local AI processor that works without external APIs"""
    
    def __init__(self):
        # Download required NLTK data if not present
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
    
    def analyze_content(self, content: str, content_id=None) -> Dict[str, Any]:
        """Analyze content using local NLP techniques"""
        
        # Basic text processing
        sentences = nltk.sent_tokenize(content)
        words = nltk.word_tokenize(content.lower())
        
        # Remove stopwords and punctuation
        from nltk.corpus import stopwords
        stop_words = set(stopwords.words('english'))
        filtered_words = [word for word in words if word.isalnum() and word not in stop_words and len(word) > 2]
        
        # Extract keywords (most frequent meaningful words)
        word_freq = Counter(filtered_words)
        keywords = [word for word, freq in word_freq.most_common(10)]
        
        # Determine sentiment
        positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'positive', 'success', 'growth', 'innovative', 'effective', 'beneficial', 'valuable', 'important', 'significant'}
        negative_words = {'bad', 'terrible', 'awful', 'negative', 'problem', 'issue', 'failure', 'decline', 'poor', 'difficult', 'challenging', 'concerning'}
        
        pos_count = sum(1 for word in filtered_words if word in positive_words)
        neg_count = sum(1 for word in filtered_words if word in negative_words)
        
        if pos_count > neg_count:
            sentiment = "positive"
        elif neg_count > pos_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Determine tone based on content characteristics
        formal_indicators = {'therefore', 'however', 'furthermore', 'consequently', 'analysis', 'research', 'study', 'data'}
        casual_indicators = {'really', 'pretty', 'quite', 'totally', 'awesome', 'cool', 'hey', 'wow'}
        
        formal_count = sum(1 for word in filtered_words if word in formal_indicators)
        casual_count = sum(1 for word in filtered_words if word in casual_indicators)
        
        if formal_count > casual_count:
            tone = "professional"
        elif casual_count > formal_count:
            tone = "casual"
        else:
            tone = "conversational"
        
        # Generate main theme from most common keywords
        main_theme = f"Analysis of {keywords[0]}" if keywords else "Content Analysis"
        
        # Create summaries
        summary_short = sentences[0] if sentences else content[:100]
        summary_medium = '. '.join(sentences[:2]) if len(sentences) >= 2 else summary_short
        summary_long = '. '.join(sentences[:3]) if len(sentences) >= 3 else summary_medium
        
        return {
            "main_theme": main_theme,
            "key_topics": keywords[:5],
            "keywords": keywords[:8],
            "sentiment": sentiment,
            "tone": tone,
            "target_audience": self._determine_audience(keywords, tone),
            "key_takeaways": self._extract_takeaways(sentences, keywords),
            "summary_short": summary_short,
            "summary_medium": summary_medium,
            "summary_long": summary_long,
            "suggested_formats": ["social_post", "email_snippet", "short_article", "infographic_data"]
        }
    
    def _determine_audience(self, keywords: List[str], tone: str) -> str:
        """Determine target audience based on keywords and tone"""
        business_terms = {'business', 'company', 'market', 'strategy', 'revenue', 'profit', 'management'}
        tech_terms = {'technology', 'software', 'digital', 'ai', 'data', 'system', 'platform'}
        general_terms = {'people', 'community', 'society', 'public', 'everyone'}
        
        if any(term in keywords for term in business_terms):
            return "Business professionals and entrepreneurs"
        elif any(term in keywords for term in tech_terms):
            return "Technology enthusiasts and professionals"
        elif tone == "professional":
            return "Professional audience seeking insights"
        else:
            return "General audience interested in the topic"
    
    def _extract_takeaways(self, sentences: List[str], keywords: List[str]) -> List[str]:
        """Extract key takeaways from content"""
        takeaways = []
        
        # Look for sentences with key indicators
        takeaway_indicators = ['important', 'key', 'essential', 'crucial', 'significant', 'main', 'primary']
        
        for sentence in sentences[:5]:  # Check first 5 sentences
            if any(indicator in sentence.lower() for indicator in takeaway_indicators):
                takeaways.append(sentence.strip())
        
        # If no specific takeaways found, create generic ones
        if not takeaways:
            if keywords:
                takeaways = [
                    f"Key insights about {keywords[0]}",
                    f"Important considerations regarding {keywords[1] if len(keywords) > 1 else 'the topic'}",
                    "Valuable information for decision making"
                ]
            else:
                takeaways = [
                    "Content provides valuable insights",
                    "Important information for readers",
                    "Useful for understanding the topic"
                ]
        
        return takeaways[:3]  # Return max 3 takeaways
    
    def repurpose_content(self, original_content: str, analysis: Dict[str, Any], content_id=None) -> Dict[str, Any]:
        """Generate repurposed content using local processing"""
        
        theme = analysis.get('main_theme', 'content')
        keywords = analysis.get('keywords', ['content'])
        summary = analysis.get('summary_short', original_content[:100])
        tone = analysis.get('tone', 'professional')
        
        return {
            'social_posts': self._generate_social_posts_local(theme, keywords, summary, tone),
            'email_snippets': self._generate_email_snippets_local(theme, summary, keywords),
            'short_article': self._generate_short_article_local(theme, original_content, analysis),
            'infographic_data': self._generate_infographic_data_local(theme, keywords, analysis),
            'rag_metadata': {
                'context_used': False,
                'context_length': 0,
                'generation_timestamp': datetime.now().isoformat(),
                'local_processing': True
            }
        }
    
    def _generate_social_posts_local(self, theme: str, keywords: List[str], summary: str, tone: str) -> List[Dict[str, Any]]:
        """Generate social media posts locally"""
        hashtag = keywords[0] if keywords else 'content'
        
        posts = [
            {
                'platform': 'linkedin',
                'text': f"Exploring {theme.lower()}. {summary} Key insights that matter for professionals. #{hashtag} #insights #professional",
                'hashtags': [hashtag, 'insights', 'professional'],
                'character_count': len(f"Exploring {theme.lower()}. {summary} Key insights that matter for professionals.")
            },
            {
                'platform': 'twitter',
                'text': f"💡 {theme}: {summary[:100]}{'...' if len(summary) > 100 else ''} #{hashtag} #insights",
                'hashtags': [hashtag, 'insights'],
                'character_count': len(f"💡 {theme}: {summary[:100]}{'...' if len(summary) > 100 else ''}")
            },
            {
                'platform': 'facebook',
                'text': f"Sharing some thoughts on {theme.lower()}. {summary} What's your take on this? Let's discuss! 💬",
                'hashtags': [hashtag],
                'character_count': len(f"Sharing some thoughts on {theme.lower()}. {summary} What's your take on this? Let's discuss!")
            },
            {
                'platform': 'instagram',
                'text': f"✨ Deep dive into {theme.lower()} today! 📚\n\n{summary}\n\n#{hashtag} #insights #learning #growth",
                'hashtags': [hashtag, 'insights', 'learning', 'growth'],
                'character_count': len(f"✨ Deep dive into {theme.lower()} today! 📚 {summary}")
            }
        ]
        
        return posts
    
    def _generate_email_snippets_local(self, theme: str, summary: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """Generate email snippets locally"""
        return [
            {
                'type': 'newsletter_teaser',
                'subject': f"New insights on {theme.lower()}",
                'content': f"We've been exploring {theme.lower()} and wanted to share some key insights with you.\n\n{summary}\n\nThis analysis reveals important considerations that could impact your approach to this topic.",
                'cta': 'Read Full Analysis',
                'word_count': len(f"We've been exploring {theme.lower()} and wanted to share some key insights with you. {summary}".split())
            },
            {
                'type': 'promotional',
                'subject': f"Don't miss: Key findings about {theme.lower()}",
                'content': f"Our latest analysis on {theme.lower()} is now available.\n\n{summary}\n\nDiscover actionable insights that can help you make informed decisions.",
                'cta': 'Get Full Report',
                'word_count': len(f"Our latest analysis on {theme.lower()} is now available. {summary}".split())
            }
        ]
    
    def _generate_short_article_local(self, theme: str, content: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate short article locally"""
        keywords = analysis.get('keywords', [])
        takeaways = analysis.get('key_takeaways', [])
        
        return {
            'headline': f"Understanding {theme}: Key Insights and Implications",
            'introduction': f"In today's rapidly evolving landscape, {theme.lower()} has become increasingly important. Our analysis reveals several key considerations that deserve attention.",
            'main_content': f"The examination of {theme.lower()} shows that {', '.join(keywords[:3])} are central themes. {takeaways[0] if takeaways else 'The content provides valuable insights.'} This analysis helps us understand the broader implications and potential applications.",
            'conclusion': f"These insights about {theme.lower()} provide a foundation for informed decision-making. Understanding these key aspects can help guide future strategies and approaches.",
            'word_count': 250,
            'reading_time': '2 min read'
        }
    
    def _generate_infographic_data_local(self, theme: str, keywords: List[str], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate infographic data locally"""
        return {
            'title': f"Key Insights: {theme}",
            'statistics': [
                {'label': 'Main Focus', 'value': theme, 'icon_suggestion': 'target'},
                {'label': 'Key Topics', 'value': str(len(keywords)), 'icon_suggestion': 'list'},
                {'label': 'Sentiment', 'value': analysis.get('sentiment', 'neutral').title(), 'icon_suggestion': 'heart'}
            ],
            'sections': [
                {'title': 'Overview', 'description': analysis.get('summary_short', 'Key insights and analysis')},
                {'title': 'Key Topics', 'description': f"Focus areas: {', '.join(keywords[:3])}"},
                {'title': 'Target Audience', 'description': analysis.get('target_audience', 'General audience')}
            ],
            'cta': 'Learn More',
            'image_description': f"Infographic displaying key insights and statistics about {theme}",
            'image_url': None
        }
