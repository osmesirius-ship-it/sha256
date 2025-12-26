# -*- coding: utf-8 -*-
"""
AI Company Email Agent
Connects to Gmail and sends personalized emails with tracking to AI companies
"""

import base64
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import uuid
from datetime import datetime
import time

# AI Companies data
AI_COMPANIES = [
    {
        "company": "OpenAI",
        "why": "Leading AI research company with strong API ecosystem",
        "angle": "DA-13 could enhance their reasoning capabilities and governance"
    },
    {
        "company": "Anthropic",
        "why": "Focus on AI safety and constitutional AI",
        "angle": "Governance layer aligns with their safety mission"
    },
    {
        "company": "Google DeepMind",
        "why": "Advanced AI research with real-world applications",
        "angle": "Reasoning QA could improve their model reliability"
    },
    {
        "company": "Microsoft",
        "why": "Major AI investments through Azure and OpenAI partnership",
        "angle": "Enterprise-grade governance for their AI offerings"
    },
    {
        "company": "NVIDIA",
        "why": "Hardware leader in AI computing",
        "angle": "Reasoning layer could optimize their AI chip performance"
    },
    {
        "company": "Meta AI",
        "why": "Large-scale AI research and open-source contributions",
        "angle": "Governance for their open AI models"
    },
    {
        "company": "Amazon (AWS)",
        "why": "Leading cloud AI services provider",
        "angle": "Enhanced reasoning for AWS AI services"
    },
    {
        "company": "IBM",
        "why": "Enterprise AI and Watson platform",
        "angle": "Governance layer for enterprise AI deployments"
    },
    {
        "company": "Salesforce",
        "why": "AI-powered CRM solutions",
        "angle": "Reasoning capabilities for customer service AI"
    },
    {
        "company": "Oracle",
        "why": "Enterprise software and cloud AI",
        "angle": "Governance for business AI applications"
    },
    {
        "company": "Hugging Face",
        "why": "Leading AI model hub and open-source community",
        "angle": "Governance for distributed AI models"
    },
    {
        "company": "Cohere",
        "why": "Enterprise-focused AI language models",
        "angle": "Enhanced reasoning for business applications"
    },
    {
        "company": "Mistral AI",
        "why": "European AI champion with efficient models",
        "angle": "Governance for their AI model ecosystem"
    },
    {
        "company": "Stability AI",
        "why": "Generative AI and image models",
        "angle": "Reasoning layer for creative AI applications"
    },
    {
        "company": "Inflection AI",
        "why": "Personal AI and conversational agents",
        "angle": "Enhanced reasoning for personal AI assistants"
    },
    {
        "company": "Adept",
        "why": "AI agents that can use software tools",
        "angle": "Reasoning capabilities for AI agents"
    },
    {
        "company": "Character.AI",
        "why": "Conversational AI and entertainment",
        "angle": "Governance for AI character interactions"
    },
    {
        "company": "Runway",
        "why": "AI-powered video generation and editing",
        "angle": "Reasoning for creative AI workflows"
    },
    {
        "company": "Midjourney",
        "why": "AI image generation platform",
        "angle": "Enhanced reasoning for creative AI prompts"
    },
    {
        "company": "ElevenLabs",
        "why": "AI voice synthesis and cloning",
        "angle": "Governance for voice AI applications"
    }
]

# Gmail API scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

class EmailAgent:
    def __init__(self, credentials_file="credentials.json"):
        self.credentials_file = credentials_file
        self.service = None
        self.tracking_base_url = "https://your-tracking-domain.com/track"  # Replace with actual tracking URL
        
    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        
        self.service = build("gmail", "v1", credentials=creds)
        print("Successfully authenticated with Gmail")
        
    def create_tracking_pixel(self, email_id, recipient):
        """Create a tracking pixel URL for email open tracking"""
        tracking_id = str(uuid.uuid4())
        tracking_url = f"{self.tracking_base_url}/open?email_id={email_id}&recipient={recipient}&tracking_id={tracking_id}"
        
        # Create 1x1 transparent pixel
        pixel_html = f'<img src="{tracking_url}" width="1" height="1" style="display:none;" alt="" />'
        return pixel_html, tracking_id
        
    def create_personalized_email(self, company_data, sender_email):
        """Create personalized email content for each company"""
        company = company_data["company"]
        why = company_data["why"]
        angle = company_data["angle"]
        
        subject = f"Partnership Opportunity: DA-13 Reasoning & Governance Layer for {company}"
        
        body = f"""
Dear {company} Team,

I hope this email finds you well. I am reaching out to explore a potential partnership opportunity that aligns perfectly with your work in artificial intelligence.

{why} is exactly why I believe our DA-13 (Reasoning QA / Governance Layer) could be transformative for your organization. {angle}

Our DA-13 solution provides:
- Advanced reasoning capabilities for AI systems
- Comprehensive governance and oversight mechanisms
- Enhanced reliability and trustworthiness in AI outputs
- Scalable architecture for enterprise deployments

Given your leadership in the AI space, I believe there is significant potential for collaboration. I would welcome the opportunity to discuss how our reasoning and governance layer could complement your existing initiatives.

Would you be available for a brief call next week to explore this further?

Best regards,
[Your Name]
[Your Title]
[Your Contact Information]
"""
        
        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = "contact@" + company.lower().replace(" ", "").replace("(", "").replace(")", "") + ".com"
        
        # Add HTML version with tracking pixel
        email_id = str(uuid.uuid4())
        tracking_pixel, tracking_id = self.create_tracking_pixel(email_id, message["To"])
        
        html_body = f"""
<html>
<body>
{body.replace(chr(10), "<br>")}
<br><br>
{tracking_pixel}
</body>
</html>
"""
        
        # Attach both plain text and HTML versions
        message.attach(MIMEText(body, "plain"))
        message.attach(MIMEText(html_body, "html"))
        
        return message, tracking_id
        
    def send_email(self, message):
        """Send email via Gmail API"""
        try:
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            send_message = self.service.users().messages().send(
                userId="me", body={"raw": raw_message}
            ).execute()
            
            print(f"Email sent successfully. Message ID: {send_message['id']}")
            return send_message["id"]
        except Exception as e:
            print(f"Error sending email: {e}")
            return None
            
    def send_campaign(self, sender_email, test_mode=True):
        """Send emails to all AI companies"""
        if not self.service:
            self.authenticate()
            
        results = []
        
        for i, company in enumerate(AI_COMPANIES, 1):
            print(f"\nProcessing {i}/{len(AI_COMPANIES)}: {company['company']}")
            
            try:
                # Create personalized email
                message, tracking_id = self.create_personalized_email(company, sender_email)
                
                if test_mode:
                    print(f"TEST MODE - Would send to: {message['To']}")
                    print(f"Subject: {message['Subject']}")
                    print(f"Tracking ID: {tracking_id}")
                    results.append({
                        "company": company["company"],
                        "status": "test_mode",
                        "tracking_id": tracking_id,
                        "recipient": message["To"]
                    })
                else:
                    # Send actual email
                    message_id = self.send_email(message)
                    if message_id:
                        results.append({
                            "company": company["company"],
                            "status": "sent",
                            "message_id": message_id,
                            "tracking_id": tracking_id,
                            "recipient": message["To"]
                        })
                    else:
                        results.append({
                            "company": company["company"],
                            "status": "failed",
                            "tracking_id": tracking_id,
                            "recipient": message["To"]
                        })
                
                # Add delay between emails to avoid rate limiting
                if not test_mode:
                    time.sleep(2)
                    
            except Exception as e:
                print(f"Error processing {company['company']}: {e}")
                results.append({
                    "company": company["company"],
                    "status": "error",
                    "error": str(e)
                })
        
        # Save campaign results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"email_campaign_results_{timestamp}.json"
        
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
            
        print(f"\nCampaign completed. Results saved to {results_file}")
        return results

def main():
    """Main function to run the email agent"""
    print("AI Company Email Agent")
    print("=" * 50)
    
    # Check if credentials file exists
    if not os.path.exists("credentials.json"):
        print("Error: credentials.json file not found!")
        print("Please download Gmail API credentials from Google Cloud Console")
        print("and save them as credentials.json in this directory.")
        return
    
    # Create email agent
    agent = EmailAgent()
    
    # Get sender email
    sender_email = input("Enter your email address: ").strip()
    
    # Ask if test mode
    test_mode = input("Run in test mode? (y/n): ").strip().lower() == "y"
    
    if test_mode:
        print("\nRunning in TEST MODE - no emails will be sent")
    
    # Send campaign
    results = agent.send_campaign(sender_email, test_mode)
    
    # Print summary
    print("\nCampaign Summary:")
    print("=" * 50)
    
    sent_count = len([r for r in results if r["status"] == "sent"])
    test_count = len([r for r in results if r["status"] == "test_mode"])
    failed_count = len([r for r in results if r["status"] in ["failed", "error"]])
    
    print(f"Emails sent: {sent_count}")
    print(f"Test mode emails: {test_count}")
    print(f"Failed emails: {failed_count}")
    print(f"Total companies: {len(results)}")

if __name__ == "__main__":
    main()
