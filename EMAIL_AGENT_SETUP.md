# AI Company Email Agent - Setup Guide

## Overview
This email agent connects to your Gmail account and sends personalized emails with tracking to 20 AI companies. Each email is tailored based on the specific reasons for outreach provided.

## Files Created
- `ai_company_email_agent.py` - Main email agent script
- `requirements.txt` - Python dependencies
- `EMAIL_AGENT_SETUP.md` - This setup guide

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Gmail API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API
4. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
5. Select "Desktop app" as application type
6. Download the JSON file and rename it to `credentials.json`
7. Place `credentials.json` in the same directory as the email agent

### 3. Email Tracking Setup (Optional)
The agent includes email tracking functionality using a 1x1 tracking pixel. To use this:
- Set up a tracking server/domain
- Update the `tracking_base_url` in the EmailAgent class
- Or remove tracking functionality if not needed

### 4. Run the Email Agent
```bash
python ai_company_email_agent.py
```

## Features
- **Personalized Emails**: Each email is customized for the specific company
- **Email Tracking**: Includes tracking pixel for open tracking
- **Test Mode**: Run in test mode to preview emails without sending
- **Campaign Results**: Saves results to timestamped JSON file
- **Rate Limiting**: Includes delays between emails to avoid Gmail rate limits

## Email Content
Each email includes:
- Personalized subject line
- Company-specific reasoning for outreach
- DA-13 solution benefits
- Call to action for partnership discussion

## Safety Features
- Test mode for previewing emails
- Error handling and logging
- Campaign result tracking
- Gmail OAuth2 authentication

## Customization
- Modify `AI_COMPANIES` list to add/remove companies
- Update email templates in `create_personalized_email()`
- Change tracking URL in EmailAgent constructor
- Adjust delay timing in `send_campaign()`

## Troubleshooting
- **Authentication issues**: Ensure `credentials.json` is properly configured
- **Rate limiting**: Increase delay between emails if needed
- **Email delivery**: Check Gmail sending limits and spam filters
