#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Add src to path
sys.path.insert(0, 'src')

from src.services.ai_processor import AIProcessor

def test_gemini_connection():
    """Test if Gemini API is working properly"""
    try:
        print("Testing Gemini API connection...")
        
        # Check if API key is loaded
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment")
            return False
        
        print(f"✅ API Key loaded: {api_key[:10]}...")
        
        # Initialize AI processor
        processor = AIProcessor()
        print("✅ AI Processor initialized successfully")
        
        # Test content analysis
        test_content = "This is a test article about artificial intelligence and machine learning."
        print("🔄 Testing content analysis...")
        
        analysis = processor.analyze_content(test_content)
        print("✅ Content analysis completed")
        print(f"Main theme: {analysis.get('main_theme', 'N/A')}")
        print(f"Keywords: {analysis.get('keywords', [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gemini_connection()
    if success:
        print("\n🎉 Gemini API connection test passed!")
    else:
        print("\n💥 Gemini API connection test failed!")
