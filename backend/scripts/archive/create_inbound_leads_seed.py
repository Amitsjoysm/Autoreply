#!/usr/bin/env python3
"""
Create seed data for Inbound Leads
"""
import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "email_assistant_db"
USER_EMAIL = "amits.joys@gmail.com"


def get_timestamp(days_ago: int = 0, hours_ago: int = 0):
    """Get ISO timestamp for a specific time in the past"""
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=hours_ago)
    return dt.isoformat()


async def create_inbound_leads_seed():
    """Create comprehensive seed data for inbound leads"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🚀 Creating inbound leads seed data...")
    print("=" * 60)
    
    # Get user
    user = await db.users.find_one({"email": USER_EMAIL})
    if not user:
        print(f"❌ User {USER_EMAIL} not found. Please create user first.")
        client.close()
        return
    
    user_id = user['id']
    print(f"✅ Found user: {USER_EMAIL} (ID: {user_id})")
    
    # Get some intents for reference
    intents = await db.intents.find({"user_id": user_id}).to_list(10)
    meeting_intent = next((i for i in intents if "meeting" in i['name'].lower()), None)
    general_intent = next((i for i in intents if "general" in i['name'].lower()), None)
    support_intent = next((i for i in intents if "support" in i['name'].lower()), None)
    
    # Clear existing leads for this user
    deleted = await db.inbound_leads.delete_many({"user_id": user_id})
    print(f"✅ Cleared {deleted.deleted_count} existing leads")
    
    # ============ CREATE DIVERSE INBOUND LEADS ============
    
    leads = []
    
    # LEAD 1: High-priority, qualified lead with meeting scheduled
    lead1_id = str(uuid.uuid4())
    initial_email1_id = str(uuid.uuid4())
    leads.append({
        "id": lead1_id,
        "user_id": user_id,
        "lead_name": "Sarah Johnson",
        "lead_email": "sarah.johnson@techcorp.com",
        "company_name": "TechCorp Solutions",
        "address": "123 Business Park, San Francisco, CA 94105",
        "phone": "+1 (415) 555-0123",
        "job_title": "VP of Engineering",
        "company_size": "200-500 employees",
        "industry": "Technology",
        "specific_interests": "AI-powered email automation for engineering team, integration with existing tools",
        "requirements": "Need solution for 50+ engineers, must integrate with Slack and Jira, budget: $5000-10000/month",
        "source": "email",
        "stage": "qualified",
        "stage_changed_at": get_timestamp(days_ago=1),
        "stage_history": [
            {
                "stage": "new",
                "changed_at": get_timestamp(days_ago=7),
                "performed_by": "system",
                "reason": "Lead created from initial email"
            },
            {
                "stage": "contacted",
                "changed_at": get_timestamp(days_ago=6),
                "performed_by": "system",
                "reason": "Auto-reply sent with product information"
            },
            {
                "stage": "qualified",
                "changed_at": get_timestamp(days_ago=1),
                "performed_by": user_id,
                "reason": "Budget confirmed, decision-maker identified, timeline established"
            }
        ],
        "score": 85,
        "priority": "high",
        "initial_email_id": initial_email1_id,
        "thread_id": f"thread-{lead1_id}",
        "email_ids": [initial_email1_id, str(uuid.uuid4()), str(uuid.uuid4())],
        "intent_id": meeting_intent['id'] if meeting_intent else None,
        "intent_name": "Meeting Request",
        "emails_received": 3,
        "emails_sent": 3,
        "last_contact_at": get_timestamp(days_ago=1),
        "last_reply_at": get_timestamp(days_ago=1, hours_ago=2),
        "response_time_avg": 1.5,
        "meeting_scheduled": True,
        "meeting_date": get_timestamp(days_ago=-3),  # 3 days in future
        "calendar_event_id": str(uuid.uuid4()),
        "activities": [
            {
                "timestamp": get_timestamp(days_ago=7),
                "activity_type": "email_received",
                "description": "Initial inquiry email received",
                "details": {"subject": "Interested in AI Email Assistant"},
                "performed_by": "system"
            },
            {
                "timestamp": get_timestamp(days_ago=6, hours_ago=23),
                "activity_type": "email_sent",
                "description": "Auto-reply sent with product overview",
                "details": {"intent": "General Inquiry"},
                "performed_by": "system"
            },
            {
                "timestamp": get_timestamp(days_ago=5),
                "activity_type": "email_received",
                "description": "Follow-up with detailed requirements",
                "details": {"keywords": ["budget", "team size", "integrations"]},
                "performed_by": "system"
            },
            {
                "timestamp": get_timestamp(days_ago=1),
                "activity_type": "stage_changed",
                "description": "Lead qualified - meets all criteria",
                "details": {"from": "contacted", "to": "qualified"},
                "performed_by": user_id
            },
            {
                "timestamp": get_timestamp(days_ago=1),
                "activity_type": "meeting_scheduled",
                "description": "Demo meeting scheduled for next week",
                "details": {"meeting_date": get_timestamp(days_ago=-3)},
                "performed_by": "system"
            }
        ],
        "is_active": True,
        "conversion_date": None,
        "lost_reason": None,
        "notes": "Very engaged prospect. VP of Engineering with decision-making authority. Budget confirmed. Demo scheduled for next week.",
        "created_at": get_timestamp(days_ago=7),
        "updated_at": get_timestamp(days_ago=1)
    })
    
    # LEAD 2: New lead, high urgency
    lead2_id = str(uuid.uuid4())
    initial_email2_id = str(uuid.uuid4())
    leads.append({
        "id": lead2_id,
        "user_id": user_id,
        "lead_name": "Michael Chen",
        "lead_email": "m.chen@startupxyz.io",
        "company_name": "StartupXYZ",
        "phone": "+1 (650) 555-0198",
        "job_title": "Founder & CEO",
        "company_size": "10-50 employees",
        "industry": "SaaS",
        "specific_interests": "Quick setup for small team, affordable pricing",
        "requirements": "Need immediate solution, team of 15, launch in 2 weeks",
        "source": "email",
        "stage": "new",
        "stage_changed_at": get_timestamp(hours_ago=4),
        "stage_history": [
            {
                "stage": "new",
                "changed_at": get_timestamp(hours_ago=4),
                "performed_by": "system",
                "reason": "Lead created from initial email"
            }
        ],
        "score": 70,
        "priority": "urgent",
        "initial_email_id": initial_email2_id,
        "thread_id": f"thread-{lead2_id}",
        "email_ids": [initial_email2_id],
        "intent_id": general_intent['id'] if general_intent else None,
        "intent_name": "General Inquiry",
        "emails_received": 1,
        "emails_sent": 1,
        "last_contact_at": get_timestamp(hours_ago=4),
        "last_reply_at": get_timestamp(hours_ago=3),
        "response_time_avg": 1.0,
        "meeting_scheduled": False,
        "activities": [
            {
                "timestamp": get_timestamp(hours_ago=4),
                "activity_type": "email_received",
                "description": "Urgent inquiry - need solution ASAP",
                "details": {"subject": "URGENT: Email automation needed", "keywords": ["urgent", "immediate"]},
                "performed_by": "system"
            },
            {
                "timestamp": get_timestamp(hours_ago=3),
                "activity_type": "email_sent",
                "description": "Auto-reply with quick start guide",
                "details": {"intent": "General Inquiry"},
                "performed_by": "system"
            }
        ],
        "is_active": True,
        "notes": "Urgent lead - startup founder, needs quick decision. Timeline: 2 weeks.",
        "created_at": get_timestamp(hours_ago=4),
        "updated_at": get_timestamp(hours_ago=3)
    })
    
    # LEAD 3: Contacted, medium priority
    lead3_id = str(uuid.uuid4())
    initial_email3_id = str(uuid.uuid4())
    leads.append({
        "id": lead3_id,
        "user_id": user_id,
        "lead_name": "Emily Rodriguez",
        "lead_email": "emily.r@marketingpros.com",
        "company_name": "Marketing Pros Agency",
        "phone": "+1 (213) 555-0167",
        "job_title": "Director of Operations",
        "company_size": "50-200 employees",
        "industry": "Marketing & Advertising",
        "specific_interests": "Managing client emails efficiently, campaign automation",
        "requirements": "Need for marketing team of 30, integration with HubSpot",
        "source": "email",
        "stage": "contacted",
        "stage_changed_at": get_timestamp(days_ago=3),
        "stage_history": [
            {
                "stage": "new",
                "changed_at": get_timestamp(days_ago=4),
                "performed_by": "system",
                "reason": "Lead created from initial email"
            },
            {
                "stage": "contacted",
                "changed_at": get_timestamp(days_ago=3),
                "performed_by": "system",
                "reason": "Auto-reply sent with product information"
            }
        ],
        "score": 65,
        "priority": "medium",
        "initial_email_id": initial_email3_id,
        "thread_id": f"thread-{lead3_id}",
        "email_ids": [initial_email3_id, str(uuid.uuid4())],
        "intent_id": general_intent['id'] if general_intent else None,
        "intent_name": "General Inquiry",
        "emails_received": 2,
        "emails_sent": 2,
        "last_contact_at": get_timestamp(days_ago=3),
        "last_reply_at": get_timestamp(days_ago=2),
        "response_time_avg": 6.0,
        "meeting_scheduled": False,
        "activities": [
            {
                "timestamp": get_timestamp(days_ago=4),
                "activity_type": "email_received",
                "description": "Initial inquiry about product",
                "details": {"subject": "Email automation for marketing team"},
                "performed_by": "system"
            },
            {
                "timestamp": get_timestamp(days_ago=3),
                "activity_type": "email_sent",
                "description": "Product information and pricing sent",
                "details": {"intent": "General Inquiry"},
                "performed_by": "system"
            },
            {
                "timestamp": get_timestamp(days_ago=2),
                "activity_type": "email_received",
                "description": "Follow-up with questions about integrations",
                "details": {"keywords": ["HubSpot", "integrations", "pricing"]},
                "performed_by": "system"
            }
        ],
        "is_active": True,
        "notes": "Interested in solution for marketing team. Asked about HubSpot integration. Waiting for reply.",
        "created_at": get_timestamp(days_ago=4),
        "updated_at": get_timestamp(days_ago=2)
    })
    
    # LEAD 4: Lost lead (competitor chosen)
    lead4_id = str(uuid.uuid4())
    initial_email4_id = str(uuid.uuid4())
    leads.append({
        "id": lead4_id,
        "user_id": user_id,
        "lead_name": "David Park",
        "lead_email": "david.park@financegroup.com",
        "company_name": "Finance Group LLC",
        "job_title": "IT Manager",
        "company_size": "500-1000 employees",
        "industry": "Finance",
        "specific_interests": "Email automation with compliance features",
        "requirements": "Enterprise-grade security, HIPAA compliance",
        "source": "email",
        "stage": "lost",
        "stage_changed_at": get_timestamp(days_ago=2),
        "stage_history": [
            {
                "stage": "new",
                "changed_at": get_timestamp(days_ago=14),
                "performed_by": "system",
                "reason": "Lead created from initial email"
            },
            {
                "stage": "contacted",
                "changed_at": get_timestamp(days_ago=13),
                "performed_by": "system",
                "reason": "Auto-reply sent"
            },
            {
                "stage": "qualified",
                "changed_at": get_timestamp(days_ago=10),
                "performed_by": user_id,
                "reason": "Budget confirmed, requirements match"
            },
            {
                "stage": "lost",
                "changed_at": get_timestamp(days_ago=2),
                "performed_by": user_id,
                "reason": "Chose competitor with existing enterprise contract"
            }
        ],
        "score": 45,
        "priority": "low",
        "initial_email_id": initial_email4_id,
        "thread_id": f"thread-{lead4_id}",
        "email_ids": [initial_email4_id, str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())],
        "intent_id": general_intent['id'] if general_intent else None,
        "intent_name": "General Inquiry",
        "emails_received": 4,
        "emails_sent": 4,
        "last_contact_at": get_timestamp(days_ago=2),
        "last_reply_at": get_timestamp(days_ago=2),
        "response_time_avg": 12.0,
        "meeting_scheduled": False,
        "activities": [
            {
                "timestamp": get_timestamp(days_ago=14),
                "activity_type": "email_received",
                "description": "Initial inquiry",
                "details": {"subject": "Email automation inquiry"},
                "performed_by": "system"
            },
            {
                "timestamp": get_timestamp(days_ago=10),
                "activity_type": "stage_changed",
                "description": "Lead qualified",
                "details": {"from": "contacted", "to": "qualified"},
                "performed_by": user_id
            },
            {
                "timestamp": get_timestamp(days_ago=2),
                "activity_type": "stage_changed",
                "description": "Lead marked as lost",
                "details": {"from": "qualified", "to": "lost", "reason": "Competitor chosen"},
                "performed_by": user_id
            }
        ],
        "is_active": False,
        "lost_reason": "Selected competitor with existing enterprise contract. Price was not the issue.",
        "notes": "Good engagement but lost to competitor. Keep for future opportunities.",
        "created_at": get_timestamp(days_ago=14),
        "updated_at": get_timestamp(days_ago=2)
    })
    
    # LEAD 5: Converted lead (success!)
    lead5_id = str(uuid.uuid4())
    initial_email5_id = str(uuid.uuid4())
    leads.append({
        "id": lead5_id,
        "user_id": user_id,
        "lead_name": "Lisa Anderson",
        "lead_email": "l.anderson@consultingfirm.com",
        "company_name": "Anderson Consulting",
        "address": "456 Corporate Drive, Boston, MA 02108",
        "phone": "+1 (617) 555-0145",
        "job_title": "Managing Partner",
        "company_size": "50-200 employees",
        "industry": "Consulting",
        "specific_interests": "Email automation for consulting team, time tracking integration",
        "requirements": "Solution for 40 consultants, mobile app access, budget approved",
        "source": "email",
        "stage": "converted",
        "stage_changed_at": get_timestamp(days_ago=1),
        "stage_history": [
            {
                "stage": "new",
                "changed_at": get_timestamp(days_ago=21),
                "performed_by": "system",
                "reason": "Lead created from initial email"
            },
            {
                "stage": "contacted",
                "changed_at": get_timestamp(days_ago=20),
                "performed_by": "system",
                "reason": "Auto-reply sent"
            },
            {
                "stage": "qualified",
                "changed_at": get_timestamp(days_ago=15),
                "performed_by": user_id,
                "reason": "Budget confirmed, decision-maker engaged"
            },
            {
                "stage": "converted",
                "changed_at": get_timestamp(days_ago=1),
                "performed_by": user_id,
                "reason": "Contract signed, onboarding started"
            }
        ],
        "score": 95,
        "priority": "high",
        "initial_email_id": initial_email5_id,
        "thread_id": f"thread-{lead5_id}",
        "email_ids": [initial_email5_id, str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())],
        "intent_id": meeting_intent['id'] if meeting_intent else None,
        "intent_name": "Meeting Request",
        "emails_received": 5,
        "emails_sent": 5,
        "last_contact_at": get_timestamp(days_ago=1),
        "last_reply_at": get_timestamp(days_ago=1, hours_ago=2),
        "response_time_avg": 2.0,
        "meeting_scheduled": True,
        "meeting_date": get_timestamp(days_ago=7),
        "calendar_event_id": str(uuid.uuid4()),
        "activities": [
            {
                "timestamp": get_timestamp(days_ago=21),
                "activity_type": "email_received",
                "description": "Initial inquiry",
                "details": {"subject": "Email automation for consulting firm"},
                "performed_by": "system"
            },
            {
                "timestamp": get_timestamp(days_ago=15),
                "activity_type": "stage_changed",
                "description": "Lead qualified",
                "details": {"from": "contacted", "to": "qualified"},
                "performed_by": user_id
            },
            {
                "timestamp": get_timestamp(days_ago=14),
                "activity_type": "meeting_scheduled",
                "description": "Demo meeting scheduled",
                "details": {"meeting_date": get_timestamp(days_ago=7)},
                "performed_by": "system"
            },
            {
                "timestamp": get_timestamp(days_ago=7),
                "activity_type": "manual_update",
                "description": "Demo completed successfully",
                "details": {"outcome": "Very positive, ready to proceed"},
                "performed_by": user_id
            },
            {
                "timestamp": get_timestamp(days_ago=1),
                "activity_type": "stage_changed",
                "description": "Lead converted to customer",
                "details": {"from": "qualified", "to": "converted"},
                "performed_by": user_id
            }
        ],
        "is_active": True,
        "conversion_date": get_timestamp(days_ago=1),
        "notes": "Excellent customer! Contract signed for Business Plan ($99/month). Onboarding in progress. 40 users.",
        "created_at": get_timestamp(days_ago=21),
        "updated_at": get_timestamp(days_ago=1)
    })
    
    # LEAD 6: New lead from support request
    lead6_id = str(uuid.uuid4())
    initial_email6_id = str(uuid.uuid4())
    leads.append({
        "id": lead6_id,
        "user_id": user_id,
        "lead_name": "James Wilson",
        "lead_email": "james@smallbiz.net",
        "company_name": "Small Business Inc",
        "phone": "+1 (555) 123-4567",
        "job_title": "Owner",
        "company_size": "1-10 employees",
        "industry": "Retail",
        "specific_interests": "Simple email automation, easy setup",
        "requirements": "Small team (5 people), limited budget",
        "source": "email",
        "stage": "new",
        "stage_changed_at": get_timestamp(hours_ago=12),
        "stage_history": [
            {
                "stage": "new",
                "changed_at": get_timestamp(hours_ago=12),
                "performed_by": "system",
                "reason": "Lead created from support inquiry"
            }
        ],
        "score": 40,
        "priority": "low",
        "initial_email_id": initial_email6_id,
        "thread_id": f"thread-{lead6_id}",
        "email_ids": [initial_email6_id],
        "intent_id": support_intent['id'] if support_intent else None,
        "intent_name": "Support Request",
        "emails_received": 1,
        "emails_sent": 1,
        "last_contact_at": get_timestamp(hours_ago=12),
        "last_reply_at": get_timestamp(hours_ago=11),
        "response_time_avg": 1.0,
        "meeting_scheduled": False,
        "activities": [
            {
                "timestamp": get_timestamp(hours_ago=12),
                "activity_type": "email_received",
                "description": "Question about pricing for small team",
                "details": {"subject": "Pricing for small business"},
                "performed_by": "system"
            },
            {
                "timestamp": get_timestamp(hours_ago=11),
                "activity_type": "email_sent",
                "description": "Pricing info sent with Free Plan recommendation",
                "details": {"intent": "Support Request"},
                "performed_by": "system"
            }
        ],
        "is_active": True,
        "notes": "Small business owner, budget-conscious. Recommended Free Plan to start.",
        "created_at": get_timestamp(hours_ago=12),
        "updated_at": get_timestamp(hours_ago=11)
    })
    
    # Insert all leads
    await db.inbound_leads.insert_many(leads)
    print(f"✅ Created {len(leads)} inbound leads")
    
    # Print summary
    print("\n" + "=" * 60)
    print("✅ INBOUND LEADS SEED DATA COMPLETE!")
    print("=" * 60)
    print(f"\n📊 Summary by Stage:")
    
    stage_counts = {}
    for lead in leads:
        stage = lead['stage']
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
    
    for stage, count in sorted(stage_counts.items()):
        print(f"   - {stage.upper()}: {count} leads")
    
    print(f"\n📊 Summary by Priority:")
    priority_counts = {}
    for lead in leads:
        priority = lead['priority']
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    for priority, count in sorted(priority_counts.items()):
        print(f"   - {priority.upper()}: {count} leads")
    
    print(f"\n📧 Lead Details:")
    for lead in leads:
        print(f"\n   {lead['lead_name']} ({lead['company_name']})")
        print(f"      Email: {lead['lead_email']}")
        print(f"      Stage: {lead['stage']} | Priority: {lead['priority']} | Score: {lead['score']}")
        print(f"      Emails: {lead['emails_received']} received, {lead['emails_sent']} sent")
        if lead['meeting_scheduled']:
            print(f"      Meeting: Scheduled ✅")
        print(f"      Activities: {len(lead['activities'])} tracked")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(create_inbound_leads_seed())
