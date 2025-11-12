"""
Create comprehensive seed data for intents and knowledge base
User: amits.joys@gmail.com
"""

import asyncio
import sys
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from config import config
from models.intent import Intent
from models.knowledge_base import KnowledgeBase
from datetime import datetime, timezone

async def create_seed_data():
    """Create seed data for the user"""
    
    # Connect to database
    client = AsyncIOMotorClient(config.MONGO_URL)
    db = client[config.DB_NAME]
    
    # Get user ID for amits.joys@gmail.com
    user_doc = await db.users.find_one({"email": "amits.joys@gmail.com"})
    if not user_doc:
        print("❌ User amits.joys@gmail.com not found")
        return
    
    user_id = user_doc['id']
    print(f"✅ Found user: {user_doc['email']} (ID: {user_id})")
    
    # Delete existing intents and KB for this user
    await db.intents.delete_many({"user_id": user_id})
    await db.knowledge_base.delete_many({"user_id": user_id})
    print("🗑️  Cleared existing intents and knowledge base")
    
    # Create Intents
    intents = [
        Intent(
            user_id=user_id,
            name="Meeting Request",
            description="Handle meeting scheduling requests",
            prompt="""When responding to meeting requests:
1. Acknowledge the meeting request positively
2. If a calendar event was created, include ALL event details:
   - Meeting date and time with timezone
   - Google Meet joining link (if available)
   - Calendar view link (if available)
3. Be professional and enthusiastic
4. Keep response concise and action-oriented""",
            keywords=["meeting", "schedule", "meet", "call", "zoom", "google meet", "appointment", "discuss", "catch up"],
            auto_send=True,
            priority=10,
            is_inbound_lead=False,
            is_default=False
        ),
        Intent(
            user_id=user_id,
            name="Meeting Reschedule",
            description="Handle meeting reschedule requests",
            prompt="""When responding to meeting reschedule requests:
1. Acknowledge the request to reschedule
2. Show understanding and flexibility
3. If a new calendar event was created, include ALL new event details
4. Confirm the changes have been made in the calendar""",
            keywords=["reschedule", "change meeting", "move meeting", "different time", "postpone", "delay"],
            auto_send=True,
            priority=9,
            is_inbound_lead=False,
            is_default=False
        ),
        Intent(
            user_id=user_id,
            name="Support Request",
            description="Handle customer support inquiries",
            prompt="""When responding to support requests:
1. Acknowledge the issue with empathy
2. Use knowledge base to provide relevant solutions
3. Offer to help further if needed
4. Be patient and understanding
5. Include specific steps or documentation links when applicable""",
            keywords=["help", "issue", "problem", "error", "bug", "not working", "can't", "unable", "trouble", "support"],
            auto_send=True,
            priority=8,
            is_inbound_lead=False,
            is_default=False
        ),
        Intent(
            user_id=user_id,
            name="General Inquiry",
            description="Handle general questions and information requests",
            prompt="""When responding to general inquiries:
1. Answer the question clearly and concisely
2. Use knowledge base information to ensure accuracy
3. Offer additional relevant information if helpful
4. Be friendly and professional
5. Invite follow-up questions""",
            keywords=["question", "inquiry", "information", "details", "know more", "tell me", "what is", "how does", "curious", "interested"],
            auto_send=True,
            priority=5,
            is_inbound_lead=False,
            is_default=False
        ),
        Intent(
            user_id=user_id,
            name="Pricing Request",
            description="Handle pricing and plan inquiries",
            prompt="""When responding to pricing inquiries:
1. Provide clear pricing information from knowledge base
2. Explain the value of each plan
3. Highlight features that match their needs
4. Offer to schedule a call if they need more details
5. Make it easy to take the next step""",
            keywords=["pricing", "cost", "price", "plan", "subscription", "payment", "how much", "fee", "charge"],
            auto_send=True,
            priority=7,
            is_inbound_lead=True,
            is_default=False
        ),
        Intent(
            user_id=user_id,
            name="Thank You / Acknowledgment",
            description="Handle thank you messages and acknowledgments",
            prompt="""When responding to thank you messages:
1. Acknowledge their thanks warmly
2. Express that you're happy to help
3. Keep response brief and genuine
4. Leave door open for future assistance
5. Be warm but professional""",
            keywords=["thank", "thanks", "appreciate", "grateful", "helpful"],
            auto_send=True,
            priority=4,
            is_inbound_lead=False,
            is_default=False
        ),
        Intent(
            user_id=user_id,
            name="Demo Request",
            description="Handle product demo and trial requests",
            prompt="""When responding to demo requests:
1. Express enthusiasm about showing the product
2. If meeting scheduled, include all calendar event details
3. Offer to answer any pre-demo questions
4. Be excited and welcoming""",
            keywords=["demo", "demonstration", "trial", "test", "try", "show me", "walkthrough"],
            auto_send=True,
            priority=8,
            is_inbound_lead=True,
            is_default=False
        ),
        Intent(
            user_id=user_id,
            name="Default Response",
            description="Default intent for emails that don't match any specific category",
            prompt="""When responding to emails that don't match any specific category:
1. Acknowledge receipt of their email
2. Use knowledge base to provide relevant information if possible
3. Be helpful and professional
4. Ask clarifying questions if needed to better assist them
5. Ensure response is grounded in knowledge base - DO NOT hallucinate information""",
            keywords=[],  # No keywords - this catches all unmatched emails
            auto_send=True,
            priority=1,  # Lowest priority - only used if no other intent matches
            is_inbound_lead=False,
            is_default=True  # This is the default intent
        )
    ]
    
    # Insert intents
    for intent in intents:
        await db.intents.insert_one(intent.model_dump())
    
    print(f"✅ Created {len(intents)} intents")
    
    # Create Knowledge Base entries
    knowledge_base = [
        KnowledgeBase(
            user_id=user_id,
            title="Company Overview",
            content="""We are a leading email automation platform that helps businesses manage customer communications efficiently. 
Our platform uses AI to automatically respond to emails, schedule meetings, and maintain customer relationships. 
Founded in 2024, we serve businesses of all sizes from startups to enterprises.
Our mission is to make email communication effortless and productive.""",
            category="Company Information",
            tags=["company", "about", "overview"]
        ),
        KnowledgeBase(
            user_id=user_id,
            title="Product Features",
            content="""Key Features:
• AI-Powered Email Responses: Automatically generate contextual replies using advanced AI
• Intent Classification: Intelligently categorize incoming emails for proper handling
• Meeting Scheduling: Detect meeting requests and create calendar events automatically
• Google Calendar Integration: Seamless integration with Google Calendar and Meet
• Knowledge Base Integration: AI uses your knowledge base to provide accurate responses
• Auto-Send Capabilities: Automatically send approved responses based on intent rules
• Follow-up Management: Create and track follow-up emails automatically
• Thread Management: Maintain conversation context across email threads
• Draft Validation: AI validates drafts for quality before sending
• Custom Personas: Configure AI to match your communication style""",
            category="Product",
            tags=["features", "capabilities", "product"]
        ),
        KnowledgeBase(
            user_id=user_id,
            title="Meeting and Calendar Features",
            content="""Meeting Management Capabilities:
• Automatic Meeting Detection: AI detects meeting requests in emails
• Google Calendar Integration: Creates events directly in Google Calendar
• Google Meet Links: Automatically generates Google Meet links for virtual meetings
• Calendar Conflict Detection: Checks for scheduling conflicts
• Meeting Confirmation: Sends automatic confirmation with all meeting details
• Event Details in Replies: Includes date, time, timezone, and joining links in responses
• Meeting Reminders: Sends reminders 1 hour before meetings
• Reschedule Support: Handles meeting reschedule requests automatically
• Attendee Management: Tracks and manages meeting attendees
• Thread-Based Communication: All meeting communication stays in same email thread""",
            category="Meetings",
            tags=["meetings", "calendar", "scheduling", "google meet"]
        ),
        KnowledgeBase(
            user_id=user_id,
            title="Pricing Information",
            content="""Pricing Plans:
• Free Plan: $0/month - 50 emails/month, basic features, 1 email account
• Starter Plan: $29/month - 500 emails/month, all core features, 3 email accounts, basic support
• Professional Plan: $79/month - 2,000 emails/month, advanced AI, 10 email accounts, priority support, custom intents
• Enterprise Plan: Custom pricing - Unlimited emails, dedicated support, custom integrations, SLA guarantee

All plans include:
- AI-powered email responses
- Calendar integration
- Knowledge base
- Basic analytics
- 14-day free trial available""",
            category="Pricing",
            tags=["pricing", "plans", "cost", "subscription"]
        ),
        KnowledgeBase(
            user_id=user_id,
            title="Getting Started Guide",
            content="""Getting Started Steps:
1. Create Account: Sign up with your email address
2. Connect Email: Link your Gmail or other email account via OAuth
3. Connect Calendar: Link Google Calendar for meeting automation
4. Configure Intents: Set up intent categories for email classification
5. Add Knowledge Base: Add company information for AI to reference
6. Set Persona: Configure your communication style and preferences
7. Test System: Send test emails to verify automation
8. Enable Auto-Send: Turn on automatic sending for approved intents
9. Monitor Performance: Track response rates and quality

Support Resources:
- Documentation: Full guides and tutorials available
- Video Tutorials: Step-by-step video walkthroughs
- Live Chat Support: Available on Professional and Enterprise plans
- Email Support: support@example.com (response within 24 hours)""",
            category="Documentation",
            tags=["getting started", "onboarding", "setup", "guide"]
        ),
        KnowledgeBase(
            user_id=user_id,
            title="Support and Contact",
            content="""Support Channels:
• Email Support: support@example.com (24-hour response time)
• Live Chat: Available 9 AM - 5 PM EST (Professional/Enterprise plans)
• Help Center: help.example.com - Comprehensive documentation
• Video Tutorials: youtube.com/ourplatform - Step-by-step guides
• Community Forum: community.example.com - User discussions

Common Issues and Solutions:
1. OAuth Connection Issues: Ensure browser allows third-party cookies
2. Calendar Events Not Creating: Verify Google Calendar permissions
3. AI Not Responding: Check intent configuration and auto-send settings
4. Email Not Syncing: Verify email account credentials and IMAP settings

Response Times:
- Free Plan: Email support within 48 hours
- Starter Plan: Email support within 24 hours
- Professional Plan: Priority support within 12 hours + live chat
- Enterprise Plan: Dedicated support within 4 hours + phone support""",
            category="Support",
            tags=["support", "help", "contact", "issues"]
        ),
        KnowledgeBase(
            user_id=user_id,
            title="Security and Privacy",
            content="""Security Measures:
• Data Encryption: All data encrypted in transit (TLS) and at rest (AES-256)
• OAuth Authentication: Secure OAuth 2.0 for email and calendar access
• No Password Storage: We never store your email passwords
• Token Refresh: Automatic token refresh for continuous secure access
• Data Privacy: Your emails and data are never shared with third parties
• GDPR Compliant: Full GDPR compliance for EU customers
• SOC 2 Certified: Annual SOC 2 Type II audits
• Data Retention: Customize data retention policies
• Access Controls: Role-based access control for team accounts
• Audit Logs: Complete audit trail of all system activities

Privacy Commitments:
- Your data is yours - we never sell or share it
- AI processing happens securely in isolated environments
- You can export or delete your data at any time
- We comply with all major privacy regulations (GDPR, CCPA, etc.)""",
            category="Security",
            tags=["security", "privacy", "compliance", "gdpr"]
        ),
        KnowledgeBase(
            user_id=user_id,
            title="Integration and API",
            content="""Available Integrations:
• Gmail (OAuth): Full integration with Gmail API
• Google Calendar: Calendar event creation and management
• Microsoft 365: Outlook and Office 365 email support
• Custom SMTP/IMAP: Connect any email provider
• Webhooks: Real-time notifications for events
• Zapier: Connect with 3,000+ apps

API Access:
• REST API: Full REST API for custom integrations
• Webhooks: Real-time event notifications
• API Documentation: api-docs.example.com
• Rate Limits: Varies by plan (Starter: 1,000/hour, Pro: 10,000/hour)
• Authentication: API key and OAuth 2.0 support

Developer Resources:
- SDKs available for Python, JavaScript, and Ruby
- Postman collection for API testing
- Developer community and forums
- Technical support for Enterprise customers""",
            category="Integrations",
            tags=["integrations", "api", "developers", "webhooks"]
        )
    ]
    
    # Insert knowledge base
    for kb in knowledge_base:
        await db.knowledge_base.insert_one(kb.model_dump())
    
    print(f"✅ Created {len(knowledge_base)} knowledge base entries")
    
    # Display summary
    print("\n" + "="*70)
    print("📊 SEED DATA SUMMARY")
    print("="*70)
    print(f"\n👤 User: {user_doc['email']} (ID: {user_id})")
    print(f"\n📋 INTENTS ({len(intents)}):")
    for intent in intents:
        auto_send_icon = "✅" if intent.auto_send else "❌"
        lead_icon = "🎯" if intent.is_inbound_lead else "  "
        default_icon = "⭐" if intent.is_default else "  "
        print(f"  {default_icon}{lead_icon} {intent.name} (Priority: {intent.priority}, Auto-send: {auto_send_icon})")
        if intent.keywords:
            print(f"      Keywords: {', '.join(intent.keywords[:5])}...")
    
    print(f"\n📚 KNOWLEDGE BASE ({len(knowledge_base)}):")
    for kb in knowledge_base:
        print(f"   • {kb.title} ({kb.category})")
    
    print("\n" + "="*70)
    print("✅ Seed data created successfully!")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(create_seed_data())
