#!/usr/bin/env python3

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

def detailed_api_test():
    """Detailed test of Hugging Face API with full logging"""
    
    print("=" * 60)
    print("🔍 DETAILED HUGGING FACE API STATUS CHECK")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    if not api_key:
        print("❌ HUGGINGFACE_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:15]}...{api_key[-10:]}")
    print(f"🔑 Key format: {'✅ Valid HF format' if api_key.startswith('hf_') else '❌ Invalid format'}")
    
    # Test API endpoint
    headers = {"Authorization": f"Bearer {api_key}"}
    api_url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
    
    print(f"\n🌐 Testing API endpoint:")
    print(f"   URL: {api_url}")
    print(f"   Headers: Authorization: Bearer {api_key[:10]}...")
    
    # Test payload
    test_payload = {"inputs": "This is an amazing test of the Hugging Face API! It should work perfectly."}
    print(f"   Payload: {test_payload}")
    
    try:
        print("\n🔄 Sending API request...")
        response = requests.post(api_url, headers=headers, json=test_payload, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📝 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS! API Response:")
            print(json.dumps(result, indent=2))
            
            # Parse sentiment
            if isinstance(result, list) and len(result) > 0:
                top_sentiment = max(result[0], key=lambda x: x['score'])
                print(f"\n🎯 Parsed Sentiment: {top_sentiment['label']} (confidence: {top_sentiment['score']:.3f})")
            
            return True
            
        elif response.status_code == 503:
            print("⚠️ Model is loading (503 Service Unavailable)")
            print("   This is normal for first-time use. Model will be ready in ~20 seconds.")
            print(f"   Response: {response.text}")
            return "loading"
            
        elif response.status_code == 401:
            print("❌ Authentication failed (401 Unauthorized)")
            print("   Check if your API key is valid and has the right permissions")
            print(f"   Response: {response.text}")
            return False
            
        elif response.status_code == 429:
            print("⚠️ Rate limit exceeded (429 Too Many Requests)")
            print("   Wait a moment before trying again")
            print(f"   Response: {response.text}")
            return "rate_limited"
            
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 30 seconds")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - check your internet connection")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_local_fallback():
    """Test if local processing works as fallback"""
    print("\n" + "=" * 60)
    print("🔍 TESTING LOCAL AI FALLBACK")
    print("=" * 60)
    
    try:
        import sys
        sys.path.insert(0, 'src')
        from src.services.local_ai_processor import LocalAIProcessor
        
        processor = LocalAIProcessor()
        print("✅ Local processor initialized successfully")
        
        test_content = "This is a comprehensive test of our local AI processing capabilities for sentiment analysis and content generation."
        
        print(f"\n🔄 Testing content analysis...")
        analysis = processor.analyze_content(test_content)
        print(f"✅ Analysis completed:")
        print(f"   Theme: {analysis.get('main_theme', 'N/A')}")
        print(f"   Sentiment: {analysis.get('sentiment', 'N/A')}")
        print(f"   Keywords: {analysis.get('keywords', [])[:3]}")
        
        print(f"\n🔄 Testing content repurposing...")
        repurposed = processor.repurpose_content(test_content, analysis)
        print(f"✅ Repurposing completed:")
        print(f"   Social posts: {len(repurposed.get('social_posts', []))}")
        print(f"   Email snippets: {len(repurposed.get('email_snippets', []))}")
        print(f"   Articles: {'✅' if repurposed.get('short_article') else '❌'}")
        print(f"   Infographics: {'✅' if repurposed.get('infographic_data') else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Local processor error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 COMPREHENSIVE API STATUS CHECK")
    print("=" * 60)
    
    # Test Hugging Face API
    hf_result = detailed_api_test()
    
    # Test local fallback
    local_result = test_local_fallback()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    if hf_result == True:
        print("🎉 Hugging Face API: ✅ WORKING PERFECTLY")
        print("   Your app will use HF for sentiment analysis")
    elif hf_result == "loading":
        print("⏳ Hugging Face API: 🔄 MODEL LOADING")
        print("   Wait 20 seconds and try again")
    elif hf_result == "rate_limited":
        print("⚠️ Hugging Face API: 🚫 RATE LIMITED")
        print("   Using local processing as fallback")
    else:
        print("❌ Hugging Face API: 💥 NOT WORKING")
        print("   Using local processing as fallback")
    
    if local_result:
        print("🎉 Local AI Fallback: ✅ WORKING PERFECTLY")
        print("   Your app will always complete processing")
    else:
        print("❌ Local AI Fallback: 💥 FAILED")
        print("   This needs to be fixed")
    
    print("\n" + "=" * 60)
    if hf_result == True and local_result:
        print("🚀 OVERALL STATUS: ✅ EXCELLENT - Both systems working!")
    elif local_result:
        print("🛡️ OVERALL STATUS: ✅ GOOD - Local fallback ensures reliability")
    else:
        print("💥 OVERALL STATUS: ❌ CRITICAL - Both systems failed")
    print("=" * 60)
