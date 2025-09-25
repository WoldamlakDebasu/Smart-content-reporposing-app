#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Add src to path
sys.path.insert(0, 'src')

def test_openai_connection():
    """Test if OpenAI API is working properly"""
    try:
        print("Testing OpenAI API connection...")
        
        # Check if API key is loaded
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY not found in environment")
            return False
        
        print(f"✅ API Key loaded: {api_key[:10]}...")
        
        # Test OpenAI import
        try:
            from openai import OpenAI
            print("✅ OpenAI library imported successfully")
        except ImportError as e:
            print(f"❌ OpenAI import failed: {str(e)}")
            return False
        
        # Initialize OpenAI client
        try:
            client = OpenAI(api_key=api_key)
            print("✅ OpenAI client initialized successfully")
        except Exception as e:
            print(f"❌ OpenAI client initialization failed: {str(e)}")
            return False
        
        # Test simple API call
        try:
            print("🔄 Testing simple API call...")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'Hello, API test successful!'"}
                ],
                max_tokens=20
            )
            
            result = response.choices[0].message.content
            print(f"✅ API Response: {result}")
            return True
            
        except Exception as e:
            print(f"❌ API call failed: {str(e)}")
            return False
        
    except Exception as e:
        print(f"❌ General error: {str(e)}")
        return False

def test_local_processor():
    """Test if local processor works"""
    try:
        print("\n🔄 Testing local AI processor...")
        from src.services.local_ai_processor import LocalAIProcessor
        
        processor = LocalAIProcessor()
        print("✅ Local processor initialized")
        
        test_content = "This is a test article about artificial intelligence."
        analysis = processor.analyze_content(test_content)
        print(f"✅ Local analysis completed: {analysis.get('main_theme', 'N/A')}")
        
        repurposed = processor.repurpose_content(test_content, analysis)
        print(f"✅ Local repurposing completed: {len(repurposed.get('social_posts', []))} social posts generated")
        
        return True
        
    except Exception as e:
        print(f"❌ Local processor error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Smart Content Repurposing Engine Components\n")
    
    openai_success = test_openai_connection()
    local_success = test_local_processor()
    
    print(f"\n📊 Test Results:")
    print(f"OpenAI API: {'✅ Working' if openai_success else '❌ Failed'}")
    print(f"Local AI: {'✅ Working' if local_success else '❌ Failed'}")
    
    if openai_success:
        print("\n🎉 OpenAI integration is working! Your app should process content successfully.")
    elif local_success:
        print("\n⚠️ OpenAI failed but local processing works. App will use fallback processing.")
    else:
        print("\n💥 Both OpenAI and local processing failed. Check your setup.")
