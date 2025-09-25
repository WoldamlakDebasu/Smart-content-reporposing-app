#!/usr/bin/env python3

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Add src to path
sys.path.insert(0, 'src')

def test_huggingface_connection():
    """Test if Hugging Face API is working properly"""
    try:
        print("Testing Hugging Face API connection...")
        
        # Check if API key is loaded
        api_key = os.getenv('HUGGINGFACE_API_KEY')
        if not api_key:
            print("❌ HUGGINGFACE_API_KEY not found in environment")
            return False
        
        print(f"✅ API Key loaded: {api_key[:10]}...")
        
        # Test simple sentiment analysis
        try:
            print("🔄 Testing sentiment analysis...")
            
            headers = {"Authorization": f"Bearer {api_key}"}
            api_url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
            
            payload = {"inputs": "This is a great test of the API!"}
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Sentiment API Response: {result}")
                return True
            elif response.status_code == 503:
                print("⚠️ Model is loading, this is normal for first use")
                return True
            else:
                print(f"❌ API call failed: {response.status_code} - {response.text}")
                return False
                
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
        
        test_content = "This is a test article about artificial intelligence and machine learning."
        analysis = processor.analyze_content(test_content)
        print(f"✅ Local analysis completed: {analysis.get('main_theme', 'N/A')}")
        
        repurposed = processor.repurpose_content(test_content, analysis)
        print(f"✅ Local repurposing completed: {len(repurposed.get('social_posts', []))} social posts generated")
        
        return True
        
    except Exception as e:
        print(f"❌ Local processor error: {str(e)}")
        return False

def test_huggingface_processor():
    """Test the full Hugging Face processor"""
    try:
        print("\n🔄 Testing Hugging Face processor...")
        from src.services.huggingface_processor import HuggingFaceProcessor
        
        processor = HuggingFaceProcessor()
        print("✅ Hugging Face processor initialized")
        
        test_content = "This is an amazing article about artificial intelligence transforming business operations."
        analysis = processor.analyze_content(test_content)
        print(f"✅ HF analysis completed: Theme='{analysis.get('main_theme', 'N/A')}', Sentiment='{analysis.get('sentiment', 'N/A')}'")
        
        repurposed = processor.repurpose_content(test_content, analysis)
        print(f"✅ HF repurposing completed: {len(repurposed.get('social_posts', []))} social posts generated")
        
        return True
        
    except Exception as e:
        print(f"❌ Hugging Face processor error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Smart Content Repurposing Engine - Hugging Face Edition\n")
    
    hf_success = test_huggingface_connection()
    local_success = test_local_processor()
    processor_success = test_huggingface_processor()
    
    print(f"\n📊 Test Results:")
    print(f"Hugging Face API: {'✅ Working' if hf_success else '❌ Failed'}")
    print(f"Local AI: {'✅ Working' if local_success else '❌ Failed'}")
    print(f"HF Processor: {'✅ Working' if processor_success else '❌ Failed'}")
    
    if processor_success:
        print("\n🎉 Hugging Face integration is working! Your app should process content successfully.")
    elif local_success:
        print("\n⚠️ Hugging Face failed but local processing works. App will use fallback processing.")
    else:
        print("\n💥 Both Hugging Face and local processing failed. Check your setup.")
