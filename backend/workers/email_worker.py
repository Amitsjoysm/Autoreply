"""Background workers for email processing"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import os
from datetime import datetime, timezone, timedelta

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

async def add_action(email_id: str, action: str, details: dict, status: str = "success"):
    """Add action to email history"""
    await db.emails.update_one(
        {"id": email_id},
        {
            "$push": {
                "action_history": {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "action": action,
                    "details": details,
                    "status": status
                }
            },
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )

async def process_email(email_id: str):
    """Process email with AI agents - Enhanced with status tracking and retry logic"""
    try:
        from services.email_service import EmailService
        ai_service = AIAgentService(db)
        calendar_service = CalendarService(db)
        email_service = EmailService(db)
        
        # Get email
        email_doc = await db.emails.find_one({"id": email_id})
        if not email_doc:
            return
        
        email = Email(**email_doc)
        
        if email.processed:
            return
        
        logger.info(f"Processing email {email.id}")
        
        # Get thread context
        thread_context = await email_service.get_thread_context(email)
        
        # Step 1: Classify intent
        await db.emails.update_one({"id": email_id}, {"$set": {"status": "classifying"}})
        await add_action(email_id, "classifying", {"step": "intent_detection"})
        
        intent_id, intent_confidence = await ai_service.classify_intent(email, email.user_id)
        
        # Get intent name
        intent_name = None
        if intent_id:
            intent_doc = await db.intents.find_one({"id": intent_id})
            if intent_doc:
                intent_name = intent_doc.get('name', 'Unknown')
        
        await add_action(email_id, "classified", {
            "intent_id": intent_id,
            "intent_name": intent_name,
            "confidence": intent_confidence
        })
        
        # Step 2: Detect meeting (only if intent is meeting-related)
        is_meeting = False
        meeting_confidence = 0.0
        meeting_details = None
        is_meeting_intent = False
        
        # Check if intent is meeting-related
        if intent_id:
            intent_doc = await db.intents.find_one({"id": intent_id})
            if intent_doc:
                is_meeting_intent = intent_doc.get('is_meeting_related', False)
        
        # Only activate meeting detection for meeting-related intents
        if is_meeting_intent:
            is_meeting, meeting_confidence, meeting_details = await ai_service.detect_meeting(email, thread_context)
            
            await add_action(email_id, "meeting_detection", {
                "detected": is_meeting,
                "confidence": meeting_confidence,
                "details": meeting_details if is_meeting else None
            })
        
        update_data = {
            "intent_detected": intent_id,
            "intent_name": intent_name,
            "intent_confidence": intent_confidence,
            "meeting_detected": is_meeting,
            "meeting_confidence": meeting_confidence,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Step 3: Enhanced meeting confirmation workflow
        event_created = None
        if is_meeting and meeting_confidence >= config.MEETING_CONFIDENCE_THRESHOLD and meeting_details:
            provider_doc = await db.calendar_providers.find_one({
                "user_id": email.user_id,
                "is_active": True
            })
            
            if provider_doc:
                from models.calendar import CalendarProvider
                provider = CalendarProvider(**provider_doc)
                
                # Check if meeting details are complete
                details_complete, missing_fields = await ai_service.check_meeting_details_complete(meeting_details)
                
                await add_action(email_id, "meeting_details_check", {
                    "complete": details_complete,
                    "missing_fields": missing_fields
                })
                
                # Check for conflicts
                conflicts = await calendar_service.check_conflicts(
                    provider.id,
                    meeting_details['start_time'],
                    meeting_details['end_time']
                )
                
                # Confidence-based approach:
                # High confidence (>0.8) + complete details + no conflicts = auto-create
                # Otherwise = send confirmation email
                should_auto_create = (
                    meeting_confidence > 0.8 and 
                    details_complete and 
                    not conflicts
                )
                
                if should_auto_create:
                    # Auto-create event
                    event_id = await calendar_service.create_event_google(provider, meeting_details)
                    
                    if event_id:
                        meeting_details['event_id'] = event_id
                        meeting_details['detected_from_email'] = True
                        meeting_details['confidence'] = meeting_confidence
                        meeting_details['meeting_confirmed'] = True
                        meeting_details['confirmation_sent'] = False
                        
                        event_created = await calendar_service.save_event(
                            email.user_id,
                            provider.id,
                            meeting_details,
                            email.id
                        )
                        
                        await add_action(email_id, "calendar_event_created", {
                            "event_id": event_id,
                            "title": meeting_details.get('title'),
                            "start_time": meeting_details.get('start_time'),
                            "auto_created": True
                        })
                        
                        logger.info(f"Auto-created calendar event for email {email.id}")
                        
                        # Send calendar event notification email
                        await send_calendar_notification(email, event_created, email_service)
                else:
                    # Send confirmation email
                    logger.info(f"Sending meeting confirmation for email {email.id}")
                    
                    # Generate alternatives if there are conflicts
                    alternatives = []
                    if conflicts:
                        alternatives = await calendar_service.suggest_alternative_times(
                            provider.id,
                            meeting_details['start_time'],
                            meeting_details['end_time']
                        )
                        
                        await add_action(email_id, "conflict_detected", {
                            "conflicts": len(conflicts),
                            "alternatives_suggested": len(alternatives)
                        })
                    
                    # Generate confirmation email
                    confirmation_email = await ai_service.generate_meeting_confirmation_email(
                        email, 
                        meeting_details, 
                        missing_fields
                    )
                    
                    # Add alternative times to confirmation email if conflicts exist
                    if alternatives:
                        alternatives_text = "\n\nI noticed there's a scheduling conflict. Here are some alternative times that work:\n"
                        for i, alt in enumerate(alternatives, 1):
                            alternatives_text += f"{i}. {alt['start_time']} to {alt['end_time']}"
                            if alt.get('note'):
                                alternatives_text += f" ({alt['note']})"
                            alternatives_text += "\n"
                        alternatives_text += "\nPlease let me know which time works best for you."
                        
                        confirmation_email += "\n" + alternatives_text
                    
                    # Send confirmation email
                    account = await email_service.get_account(email.email_account_id)
                    if account:
                        from models.email import EmailSend
                        
                        confirmation = EmailSend(
                            email_account_id=email.email_account_id,
                            to_email=[email.from_email],
                            subject=f"Re: {email.subject}",
                            body=confirmation_email
                        )
                        
                        sent = False
                        if account.account_type == 'oauth_gmail':
                            sent = await email_service.send_email_oauth_gmail(account, confirmation, email.thread_id)
                        else:
                            sent = await email_service.send_email_smtp(account, confirmation)
                        
                        if sent:
                            # Save pending event (not confirmed yet)
                            meeting_details['event_id'] = f"pending_{email.id}"
                            meeting_details['detected_from_email'] = True
                            meeting_details['confidence'] = meeting_confidence
                            meeting_details['meeting_confirmed'] = False
                            meeting_details['confirmation_sent'] = True
                            
                            event_created = await calendar_service.save_event(
                                email.user_id,
                                provider.id,
                                meeting_details,
                                email.id
                            )
                            
                            await add_action(email_id, "confirmation_email_sent", {
                                "reason": "low_confidence" if meeting_confidence <= 0.8 else ("incomplete_details" if not details_complete else "conflict"),
                                "missing_fields": missing_fields,
                                "has_conflicts": len(conflicts) > 0,
                                "alternatives_suggested": len(alternatives)
                            })
                            
                            logger.info(f"Sent meeting confirmation email for {email.id}")
        
        # Step 4: Generate draft with retry logic (max 2 attempts)
        await db.emails.update_one({"id": email_id}, {"$set": {"status": "drafting"}})
        
        draft = None
        total_tokens = 0
        max_retries = 2
        
        for attempt in range(max_retries + 1):
            await add_action(email_id, "drafting", {
                "attempt": attempt + 1,
                "max_attempts": max_retries + 1
            })
            
            draft, tokens = await ai_service.generate_draft(
                email, 
                email.user_id, 
                intent_id,
                thread_context,
                validation_issues=update_data.get('validation_issues') if attempt > 0 else None
            )
            total_tokens += tokens
            
            await add_action(email_id, "draft_generated", {
                "attempt": attempt + 1,
                "tokens": tokens,
                "draft_length": len(draft) if draft else 0
            })
            
            # Step 5: Validate draft
            await db.emails.update_one({"id": email_id}, {"$set": {"status": "validating"}})
            await add_action(email_id, "validating", {"attempt": attempt + 1})
            
            valid, issues = await ai_service.validate_draft(
                draft, 
                email, 
                email.user_id, 
                intent_id,
                thread_context
            )
            
            await add_action(email_id, "validated", {
                "valid": valid,
                "issues": issues,
                "attempt": attempt + 1
            })
            
            if valid:
                update_data['draft_generated'] = True
                update_data['draft_content'] = draft
                update_data['draft_validated'] = True
                update_data['validation_issues'] = []
                update_data['draft_retry_count'] = attempt
                update_data['status'] = 'draft_ready'
                break
            else:
                update_data['validation_issues'] = issues
                update_data['draft_retry_count'] = attempt
                
                if attempt < max_retries:
                    logger.info(f"Draft validation failed for email {email.id}, retrying (attempt {attempt + 1}/{max_retries})")
                    await add_action(email_id, "retry_draft", {
                        "reason": "validation_failed",
                        "issues": issues,
                        "attempt": attempt + 1
                    })
                else:
                    logger.warning(f"Draft validation failed after {max_retries} retries for email {email.id}, escalating")
                    update_data['status'] = 'escalated'
                    update_data['draft_generated'] = True
                    update_data['draft_content'] = draft
                    update_data['draft_validated'] = False
                    await add_action(email_id, "escalated", {
                        "reason": "validation_failed_max_retries",
                        "issues": issues,
                        "total_attempts": attempt + 1
                    }, "failed")
        
        update_data['tokens_used'] = total_tokens
        
        # Step 6: Auto-send if intent allows and draft is valid
        if intent_id and update_data.get('draft_validated'):
            intent_doc = await db.intents.find_one({"id": intent_id})
            if intent_doc and intent_doc.get('auto_send'):
                await db.emails.update_one({"id": email_id}, {"$set": {"status": "sending"}})
                await add_action(email_id, "sending", {"auto_send": True})
                
                account = await email_service.get_account(email.email_account_id)
                
                if account:
                    from models.email import EmailSend
                    
                    reply = EmailSend(
                        email_account_id=email.email_account_id,
                        to_email=[email.from_email],
                        subject=f"Re: {email.subject}",
                        body=draft
                    )
                    
                    sent = False
                    if account.account_type == 'oauth_gmail':
                        sent = await email_service.send_email_oauth_gmail(account, reply, email.thread_id)
                    else:
                        sent = await email_service.send_email_smtp(account, reply)
                    
                    if sent:
                        update_data['status'] = 'sent'
                        update_data['replied'] = True
                        update_data['reply_sent_at'] = datetime.now(timezone.utc).isoformat()
                        await add_action(email_id, "sent", {
                            "to": email.from_email,
                            "auto_send": True
                        })
                        logger.info(f"Auto-sent reply for email {email.id}")
                    else:
                        update_data['status'] = 'error'
                        update_data['error_message'] = "Failed to send email"
                        await add_action(email_id, "send_failed", {"error": "Failed to send"}, "failed")
        
        # Mark as processed
        update_data['processed'] = True
        
        # Update email in DB
        await db.emails.update_one({"id": email_id}, {"$set": update_data})
        
        # Track tokens for user
        if total_tokens > 0:
            await db.users.update_one(
                {"id": email.user_id},
                {"$inc": {"tokens_used": total_tokens}}
            )
        
        logger.info(f"Email {email.id} processed successfully with status: {update_data['status']}")
    except Exception as e:
        logger.error(f"Error processing email {email_id}: {e}")
        await db.emails.update_one(
            {"id": email_id},
            {"$set": {
                "processed": True,
                "status": "error",
                "error_message": str(e),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        await add_action(email_id, "error", {"message": str(e)}, "failed")

async def send_calendar_notification(email: Email, event, email_service):
    """Send email notification about created calendar event"""
    try:
        account = await email_service.get_account(email.email_account_id)
        if not account:
            return
        
        from models.email import EmailSend
        
        # Format event details
        event_body = f"""A calendar event has been created based on your email:

Event Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Title: {event.title}
Start: {event.start_time}
End: {event.end_time}
Location: {event.location or 'Not specified'}
Description: {event.description or 'No description'}
Attendees: {', '.join(event.attendees) if event.attendees else 'None'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This event has been added to your calendar. You will receive a reminder 1 hour before the meeting.

Best regards,
Your AI Email Assistant"""
        
        notification = EmailSend(
            email_account_id=email.email_account_id,
            to_email=[email.from_email],
            subject=f"Calendar Event Created: {event.title}",
            body=event_body
        )
        
        sent = False
        if account.account_type == 'oauth_gmail':
            sent = await email_service.send_email_oauth_gmail(account, notification, email.thread_id)
        else:
            sent = await email_service.send_email_smtp(account, notification)
        
        if sent:
            logger.info(f"Sent calendar notification for event {event.id}")
            await add_action(email.id, "calendar_notification_sent", {
                "event_id": event.id,
                "event_title": event.title
            })
    except Exception as e:
        logger.error(f"Error sending calendar notification: {e}")

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
    """Check and send calendar reminders with customizable timing"""
    try:
        now = datetime.now(timezone.utc)
        
        # Get events that need reminders (check various reminder times)
        # We check events starting within the next 2 hours
        check_until = (now + timedelta(hours=2)).isoformat()
        
        events = await db.calendar_events.find({
            "start_time": {"$gte": now.isoformat(), "$lte": check_until},
            "reminder_sent": False,
            "meeting_confirmed": True  # Only send reminders for confirmed meetings
        }).to_list(100)
        
        logger.info(f"Checking {len(events)} events for reminders")
        
        calendar_service = CalendarService(db)
        email_service = EmailService(db)
        
        from models.calendar import CalendarEvent
        from dateutil import parser
        
        for event_doc in events:
            event = CalendarEvent(**event_doc)
            
            # Calculate when reminder should be sent
            event_start = parser.isoparse(event.start_time)
            reminder_time = event_start - timedelta(minutes=event.reminder_minutes_before)
            
            # Check if it's time to send reminder (within 5 minutes window)
            time_diff = (reminder_time - now).total_seconds() / 60  # in minutes
            
            if -5 <= time_diff <= 5:  # Send if within 5 minutes of reminder time
                logger.info(f"Sending reminder for event {event.id} ({event.title})")
                await calendar_service.send_reminder(event, email_service, event.user_id)
                
                # Mark reminder as sent
                await db.calendar_events.update_one(
                    {"id": event.id},
                    {"$set": {
                        "reminder_sent": True,
                        "reminder_sent_at": now.isoformat()
                    }}
                )
        
        logger.info(f"Processed {len(events)} events for reminders")
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
