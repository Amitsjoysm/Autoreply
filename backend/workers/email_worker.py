"""Background workers for email processing"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import os
from datetime import datetime, timezone

from config import config
from services.email_service import EmailService
from services.ai_agent_service import AIAgentService
from services.calendar_service import CalendarService
from models.email_account import EmailAccount
from models.email import Email

logger = logging.getLogger(__name__)

# Database connection
client = AsyncIOMotorClient(config.MONGO_URL)
db = client[config.DB_NAME]

async def poll_email_account(account_id: str):
    """Poll single email account for new emails"""
    try:
        email_service = EmailService(db)
        ai_service = AIAgentService(db)
        
        # Get account
        account = await email_service.get_account(account_id)
        if not account or not account.is_active:
            return
        
        logger.info(f"Polling account {account.email}")
        
        # Update sync status
        await db.email_accounts.update_one(
            {"id": account_id},
            {"$set": {"sync_status": "syncing"}}
        )
        
        # Fetch emails based on account type
        emails = []
        if account.account_type == 'oauth_gmail':
            emails = await email_service.fetch_emails_oauth_gmail(account)
        elif account.account_type in ['app_password_gmail', 'custom_smtp']:
            emails = await email_service.fetch_emails_imap(account)
        
        logger.info(f"Found {len(emails)} new emails for {account.email}")
        
        # Process each email
        for email_data in emails:
            # Check if email already exists
            existing = await db.emails.find_one({
                "email_account_id": account_id,
                "message_id": email_data['message_id']
            })
            
            if existing:
                continue
            
            # Save email
            email_obj = await email_service.save_email(
                account.user_id,
                account_id,
                email_data
            )
            
            # Process email asynchronously
            await process_email(email_obj.id)
        
        # Update sync status
        await db.email_accounts.update_one(
            {"id": account_id},
            {"$set": {
                "sync_status": "success",
                "last_sync": datetime.now(timezone.utc).isoformat(),
                "error_message": None
            }}
        )
    except Exception as e:
        logger.error(f"Error polling account {account_id}: {e}")
        await db.email_accounts.update_one(
            {"id": account_id},
            {"$set": {
                "sync_status": "error",
                "error_message": str(e)
            }}
        )

async def process_email(email_id: str):
    """Process email with AI agents"""
    try:
        ai_service = AIAgentService(db)
        calendar_service = CalendarService(db)
        
        # Get email
        email_doc = await db.emails.find_one({"id": email_id})
        if not email_doc:
            return
        
        email = Email(**email_doc)
        
        if email.processed:
            return
        
        logger.info(f"Processing email {email.id}")
        
        # Step 1: Classify intent
        intent_id, intent_confidence = await ai_service.classify_intent(email, email.user_id)
        
        # Step 2: Detect meeting
        is_meeting, meeting_confidence, meeting_details = await ai_service.detect_meeting(email)
        
        # Update email
        update_data = {
            "processed": True,
            "intent_detected": intent_id,
            "intent_confidence": intent_confidence,
            "meeting_detected": is_meeting,
            "meeting_confidence": meeting_confidence,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Step 3: If meeting detected, create calendar event
        if is_meeting and meeting_confidence >= config.MEETING_CONFIDENCE_THRESHOLD and meeting_details:
            # Get user's calendar provider
            provider_doc = await db.calendar_providers.find_one({
                "user_id": email.user_id,
                "is_active": True
            })
            
            if provider_doc:
                from models.calendar import CalendarProvider
                provider = CalendarProvider(**provider_doc)
                
                # Check conflicts
                conflicts = await calendar_service.check_conflicts(
                    provider.id,
                    meeting_details['start_time'],
                    meeting_details['end_time']
                )
                
                if not conflicts:
                    # Create event in Google Calendar
                    event_id = await calendar_service.create_event_google(provider, meeting_details)
                    
                    if event_id:
                        # Save event to DB
                        meeting_details['event_id'] = event_id
                        meeting_details['detected_from_email'] = True
                        meeting_details['confidence'] = meeting_confidence
                        
                        await calendar_service.save_event(
                            email.user_id,
                            provider.id,
                            meeting_details,
                            email.id
                        )
                        
                        logger.info(f"Created calendar event for email {email.id}")
        
        # Step 4: Generate draft
        draft, tokens = await ai_service.generate_draft(email, email.user_id, intent_id)
        
        update_data['draft_generated'] = True
        update_data['draft_content'] = draft
        update_data['tokens_used'] = tokens
        
        # Step 5: Validate draft
        valid, issues = await ai_service.validate_draft(draft, email, email.user_id, intent_id)
        
        update_data['draft_validated'] = valid
        update_data['validation_issues'] = issues
        
        if valid:
            update_data['status'] = 'draft_ready'
        else:
            update_data['status'] = 'escalated'
        
        # Step 6: Auto-send if intent allows
        if intent_id and valid:
            intent_doc = await db.intents.find_one({"id": intent_id})
            if intent_doc and intent_doc.get('auto_send'):
                # Auto-send reply
                from services.email_service import EmailService
                from models.email import EmailSend
                
                email_service = EmailService(db)
                account = await email_service.get_account(email.email_account_id)
                
                if account:
                    reply = EmailSend(
                        email_account_id=email.email_account_id,
                        to_email=[email.from_email],
                        subject=f"Re: {email.subject}",
                        body=draft
                    )
                    
                    sent = False
                    if account.account_type == 'oauth_gmail':
                        sent = await email_service.send_email_oauth_gmail(account, reply)
                    else:
                        sent = await email_service.send_email_smtp(account, reply)
                    
                    if sent:
                        update_data['status'] = 'sent'
                        update_data['replied'] = True
                        update_data['reply_sent_at'] = datetime.now(timezone.utc).isoformat()
                        logger.info(f"Auto-sent reply for email {email.id}")
        
        # Update email in DB
        await db.emails.update_one({"id": email_id}, {"$set": update_data})
        
        # Track tokens for user
        if tokens > 0:
            await db.users.update_one(
                {"id": email.user_id},
                {"$inc": {"tokens_used": tokens}}
            )
        
        logger.info(f"Email {email.id} processed successfully")
    except Exception as e:
        logger.error(f"Error processing email {email_id}: {e}")
        await db.emails.update_one(
            {"id": email_id},
            {"$set": {
                "processed": True,
                "status": "escalated",
                "error_message": str(e)
            }}
        )

async def poll_all_accounts():
    """Poll all active email accounts"""
    try:
        accounts = await db.email_accounts.find({"is_active": True}).to_list(1000)
        
        logger.info(f"Polling {len(accounts)} active accounts")
        
        tasks = [poll_email_account(account['id']) for account in accounts]
        await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        logger.error(f"Error polling all accounts: {e}")

async def check_follow_ups():
    """Check and send scheduled follow-ups"""
    try:
        now = datetime.now(timezone.utc).isoformat()
        
        # Get pending follow-ups
        follow_ups = await db.follow_ups.find({
            "status": "pending",
            "scheduled_at": {"$lte": now}
        }).to_list(100)
        
        logger.info(f"Found {len(follow_ups)} follow-ups to send")
        
        email_service = EmailService(db)
        
        for follow_up_doc in follow_ups:
            from models.follow_up import FollowUp
            from models.email import EmailSend
            
            follow_up = FollowUp(**follow_up_doc)
            
            # Get account
            account = await email_service.get_account(follow_up.email_account_id)
            if not account:
                continue
            
            # Get original email
            email_doc = await db.emails.find_one({"id": follow_up.email_id})
            if not email_doc:
                continue
            
            email = Email(**email_doc)
            
            # Send follow-up
            follow_up_email = EmailSend(
                email_account_id=follow_up.email_account_id,
                to_email=[email.from_email],
                subject=follow_up.subject,
                body=follow_up.body
            )
            
            sent = False
            if account.account_type == 'oauth_gmail':
                sent = await email_service.send_email_oauth_gmail(account, follow_up_email)
            else:
                sent = await email_service.send_email_smtp(account, follow_up_email)
            
            if sent:
                await db.follow_ups.update_one(
                    {"id": follow_up.id},
                    {"$set": {
                        "status": "sent",
                        "sent_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                logger.info(f"Sent follow-up {follow_up.id}")
    except Exception as e:
        logger.error(f"Error checking follow-ups: {e}")

async def check_reminders():
    """Check and send calendar reminders"""
    try:
        from datetime import timedelta
        
        now = datetime.now(timezone.utc)
        reminder_time = (now + timedelta(hours=1)).isoformat()
        
        # Get events starting in ~1 hour that haven't had reminders sent
        events = await db.calendar_events.find({
            "start_time": {"$gte": now.isoformat(), "$lte": reminder_time},
            "reminder_sent": False
        }).to_list(100)
        
        logger.info(f"Found {len(events)} events needing reminders")
        
        calendar_service = CalendarService(db)
        email_service = EmailService(db)
        
        from models.calendar import CalendarEvent
        
        for event_doc in events:
            event = CalendarEvent(**event_doc)
            await calendar_service.send_reminder(event, email_service, event.user_id)
    except Exception as e:
        logger.error(f"Error checking reminders: {e}")

# Main worker loop
async def run_worker():
    """Main worker loop"""
    logger.info("Starting email worker...")
    
    poll_counter = 0
    follow_up_counter = 0
    reminder_counter = 0
    
    while True:
        try:
            # Poll emails every 60 seconds
            if poll_counter % config.EMAIL_POLL_INTERVAL == 0:
                await poll_all_accounts()
                poll_counter = 0
            
            # Check follow-ups every 5 minutes
            if follow_up_counter % config.FOLLOW_UP_CHECK_INTERVAL == 0:
                await check_follow_ups()
                follow_up_counter = 0
            
            # Check reminders every hour
            if reminder_counter % config.REMINDER_CHECK_INTERVAL == 0:
                await check_reminders()
                reminder_counter = 0
            
            await asyncio.sleep(1)
            poll_counter += 1
            follow_up_counter += 1
            reminder_counter += 1
        except Exception as e:
            logger.error(f"Worker error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(run_worker())
