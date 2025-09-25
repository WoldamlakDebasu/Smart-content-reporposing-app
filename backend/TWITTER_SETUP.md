# 🐦 Twitter API Integration Setup

## Quick Setup Guide

To enable **real Twitter posting** (not just demo mode), follow these steps:

### 1. Create Twitter Developer Account
1. Go to [https://developer.twitter.com](https://developer.twitter.com)
2. Sign in with your Twitter account
3. Apply for a developer account (usually approved instantly)

### 2. Create a New App
1. Go to the [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Click "Create App" or "New Project"
3. Fill in your app details:
   - **App Name**: "Smart Content Repurposing Engine"
   - **Description**: "AI-powered content repurposing and social media automation"
   - **Website**: Your website or `http://localhost:5173`

### 3. Get Your API Keys
1. In your app dashboard, go to "Keys and Tokens"
2. Copy the **Bearer Token** (starts with "AAAA...")
3. If needed, generate **Access Token** and **Access Token Secret**

### 4. Update Your .env File
Replace the placeholder in your `.env` file:

```bash
# Replace this line:
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here

# With your real token:
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAABcdefg1234567890...
```

### 5. Set Permissions
1. In your Twitter app settings, go to "App Permissions"
2. Set to **"Read and Write"** to allow posting tweets
3. Save changes

### 6. Test the Integration
1. Restart your backend server
2. Process some content in your app
3. Click "Distribute to Twitter" or "Distribute to All Platforms"
4. Check the backend logs for "🎉 REAL TWITTER POST CREATED!"
5. Check your Twitter account for the posted tweet!

## Current Status
- ✅ **Demo Mode**: Always works (simulated posting)
- 🔄 **Real Mode**: Activated when `TWITTER_BEARER_TOKEN` starts with "AAAA"

## Troubleshooting

### Common Issues:
1. **"Twitter API error: 401"** → Check your Bearer Token
2. **"Twitter API error: 403"** → Check app permissions (needs Read+Write)
3. **"Twitter API error: 429"** → Rate limit reached, wait 15 minutes

### Rate Limits:
- **Free Tier**: 1,500 tweets per month
- **Basic Tier**: 50,000 tweets per month ($100/month)

## Security Notes
- ✅ Never commit real API keys to version control
- ✅ Keep your Bearer Token secure
- ✅ Use environment variables only
- ✅ Regenerate tokens if compromised

---

**Once configured, your Smart Content Repurposing Engine will post real tweets to your Twitter account!** 🚀
