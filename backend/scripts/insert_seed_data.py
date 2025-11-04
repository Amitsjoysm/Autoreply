#!/usr/bin/env python3
"""Insert seed data for intents and knowledge base for a specific user"""

import sys
import os
from pymongo import MongoClient
from datetime import datetime, timezone
import uuid

# Add backend to path
sys.path.insert(0, '/app/backend')

from config import config

def insert_seed_data(user_id: str):
    """
    Insert seed data for intents and knowledge base
    
    Args:
        user_id: User ID to create seed data for
    """
    client = MongoClient(config.MONGO_URL)
    db = client[config.DB_NAME]
    
    print(f"Inserting seed data for user: {user_id}")
    
    # Delete existing data
    print("\nDeleting existing intents and knowledge base...")
    deleted_intents = db.intents.delete_many({'user_id': user_id})
    deleted_kb = db.knowledge_base.delete_many({'user_id': user_id})
    print(f"  Deleted {deleted_intents.deleted_count} intents")
    print(f"  Deleted {deleted_kb.deleted_count} knowledge base entries")
    
    # Create intents
    print("\nCreating intents...")
    intents = [
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': 'Meeting Request',
            'description': 'Emails requesting to schedule a meeting or call',
            'prompt': 'This is a meeting request. Be professional and friendly. Suggest times if needed. Confirm availability.',
            'keywords': ['meeting', 'schedule', 'call', 'discuss', 'catch up', 'connect', 'meet', 'zoom', 'teams', 'conference'],
            'auto_send': True,
            'priority': 10,
            'is_default': False,
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': 'Support Request',
            'description': 'Customer support or help requests',
            'prompt': 'This is a support request. Be helpful and empathetic. Provide clear solutions. Offer additional assistance.',
            'keywords': ['help', 'issue', 'problem', 'error', 'bug', 'not working', 'trouble', 'support', 'assistance', 'fix'],
            'auto_send': True,
            'priority': 8,
            'is_default': False,
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': 'General Inquiry',
            'description': 'General questions or inquiries',
            'prompt': 'This is a general inquiry. Be informative and helpful. Use knowledge base to provide accurate information.',
            'keywords': ['question', 'inquiry', 'wondering', 'curious', 'information', 'details', 'know more', 'tell me', 'explain'],
            'auto_send': True,
            'priority': 5,
            'is_default': False,
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': 'Thank You',
            'description': 'Emails expressing gratitude',
            'prompt': 'This is a thank you email. Be warm and gracious. Express appreciation. Keep it brief.',
            'keywords': ['thank', 'thanks', 'appreciate', 'grateful', 'gratitude'],
            'auto_send': True,
            'priority': 4,
            'is_default': False,
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': 'Follow-up Request',
            'description': 'Requests for follow-up or updates',
            'prompt': 'This is a follow-up request. Provide status updates. Be transparent about progress.',
            'keywords': ['follow up', 'followup', 'update', 'status', 'progress', 'checking in', 'any news'],
            'auto_send': True,
            'priority': 6,
            'is_default': False,
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': 'Introduction',
            'description': 'Introduction or networking emails',
            'prompt': 'This is an introduction email. Be friendly and professional. Show interest. Suggest next steps.',
            'keywords': ['introduction', 'introduce', 'network', 'connect', 'reach out', 'heard about', 'recommended'],
            'auto_send': True,
            'priority': 7,
            'is_default': False,
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': 'Default Intent',
            'description': 'Default intent for emails that don\'t match other categories',
            'prompt': 'This email doesn\'t match any specific category. Respond professionally and helpfully. Use knowledge base if relevant.',
            'keywords': [],
            'auto_send': True,
            'priority': 1,
            'is_default': True,
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
    ]
    
    db.intents.insert_many(intents)
    print(f"  Created {len(intents)} intents")
    
    # Create knowledge base entries
    print("\nCreating knowledge base entries...")
    knowledge_base = [
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': 'Company Overview',
            'content': '''Our company is a leading provider of AI-powered email automation solutions. 
            We help businesses streamline their email communications with intelligent automation, 
            natural language processing, and smart scheduling. Our platform integrates seamlessly 
            with Gmail, Outlook, and other major email providers.''',
            'category': 'Company Information',
            'tags': ['company', 'overview', 'about'],
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': 'Product Features',
            'content': '''Key features of our platform:
            - AI-powered email responses with context awareness
            - Automatic intent detection and classification
            - Smart scheduling and calendar integration
            - Follow-up automation with customizable schedules
            - Multi-account support for Gmail and Outlook
            - Knowledge base integration for accurate responses
            - Meeting detection and calendar event creation
            - Thread-aware conversations
            - Customizable personas and signatures''',
            'category': 'Product',
            'tags': ['features', 'product', 'capabilities'],
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': 'Pricing Plans',
            'content': '''We offer flexible pricing plans:
            
            Starter Plan - $29/month:
            - 1 email account
            - 500 automated responses/month
            - Basic knowledge base
            - Email support
            
            Professional Plan - $79/month:
            - 3 email accounts
            - 2,000 automated responses/month
            - Advanced knowledge base
            - Calendar integration
            - Priority support
            
            Enterprise Plan - Custom pricing:
            - Unlimited email accounts
            - Unlimited automated responses
            - Custom integrations
            - Dedicated account manager
            - 24/7 support''',
            'category': 'Pricing',
            'tags': ['pricing', 'plans', 'cost'],
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': 'Getting Started Guide',
            'content': '''Getting started is easy:
            
            1. Connect Your Email: Add your Gmail or Outlook account using OAuth authentication
            2. Set Up Your Persona: Define your communication style and preferences
            3. Add Knowledge Base: Input information about your business, products, or services
            4. Configure Intents: Customize how different types of emails should be handled
            5. Enable Auto-Reply: Turn on automated responses for selected intent types
            6. Connect Calendar: Link your Google Calendar for meeting scheduling
            7. Start Receiving: Your AI assistant will automatically process incoming emails
            
            The system learns from your feedback and improves over time.''',
            'category': 'Documentation',
            'tags': ['getting started', 'setup', 'guide'],
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': 'Support and Contact',
            'content': '''We're here to help!
            
            Email Support: support@example.com
            Response Time: Within 24 hours
            
            Live Chat: Available on our website during business hours (9 AM - 6 PM EST)
            
            Phone Support: (555) 123-4567 (Professional and Enterprise plans only)
            
            Documentation: Visit docs.example.com for detailed guides and tutorials
            
            Community Forum: community.example.com for peer support and best practices
            
            For urgent issues, please mark your email with [URGENT] in the subject line.''',
            'category': 'Support',
            'tags': ['support', 'contact', 'help'],
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': 'Security and Privacy',
            'content': '''Your security and privacy are our top priorities:
            
            - All data is encrypted in transit (TLS 1.3) and at rest (AES-256)
            - OAuth authentication - we never store your email password
            - SOC 2 Type II compliant
            - GDPR and CCPA compliant
            - Regular security audits by third-party firms
            - Data is stored in secure data centers
            - You retain full ownership of your data
            - Easy data export and deletion options
            - Access logs and audit trails available
            - Optional two-factor authentication
            
            We never sell or share your data with third parties.''',
            'category': 'Security',
            'tags': ['security', 'privacy', 'compliance'],
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
    ]
    
    db.knowledge_base.insert_many(knowledge_base)
    print(f"  Created {len(knowledge_base)} knowledge base entries")
    
    print("\n✅ Seed data inserted successfully!")
    print(f"\nSummary:")
    print(f"  - {len(intents)} intents created")
    print(f"  - {len(knowledge_base)} knowledge base entries created")
    print(f"  - User ID: {user_id}")
    
    client.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python insert_seed_data.py <user_id>")
        sys.exit(1)
    
    user_id = sys.argv[1]
    insert_seed_data(user_id)
