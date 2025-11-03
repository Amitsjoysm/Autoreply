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
        
        intent_id, intent_confidence, intent_doc = await ai_service.classify_intent(email, email.user_id)
        
        # Get intent name
        intent_name = None
        auto_send_enabled = False
        if intent_id and intent_doc:
            intent_name = intent_doc.get('name', 'Unknown')
            auto_send_enabled = intent_doc.get('auto_send', False)
            logger.info(f"Intent matched for email {email.id}: {intent_name} (confidence: {intent_confidence}, auto_send: {auto_send_enabled})")
        else:
            logger.info(f"No intent matched for email {email.id} (subject: {email.subject})")
        
        await add_action(email_id, "classified", {
            "intent_id": intent_id,
            "intent_name": intent_name,
            "confidence": intent_confidence
        })
        
        # Step 2: Detect meeting
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
        
        # Step 3: If meeting detected, create calendar event and send notification
        event_created = None
        has_conflict = False
        conflict_details = []
        
        if is_meeting and meeting_confidence >= config.MEETING_CONFIDENCE_THRESHOLD and meeting_details:
            provider_doc = await db.calendar_providers.find_one({
                "user_id": email.user_id,
                "is_active": True
            })
            
            if provider_doc:
                from models.calendar import CalendarProvider
                provider = CalendarProvider(**provider_doc)
                
                # Check for conflicts
                conflicts = await calendar_service.check_conflicts(
                    provider.id,
                    meeting_details['start_time'],
                    meeting_details['end_time']
                )
                
                if conflicts:
                    # Log conflicts but still create event (user can decide later)
                    has_conflict = True
                    conflict_details = [
                        {
                            "title": c.title,
                            "start_time": c.start_time,
                            "end_time": c.end_time
                        } for c in conflicts
                    ]
                    
                    await add_action(email_id, "calendar_conflicts_detected", {
                        "conflicts": conflict_details,
                        "message": "Meeting conflicts detected. Event will be created for review."
                    })
                    
                    logger.warning(f"Meeting conflicts detected for email {email.id}: {len(conflicts)} conflicts")
                    
                    # Store conflict info in meeting details
                    meeting_details['has_conflicts'] = True
                    meeting_details['conflicts'] = conflict_details
                
                # Create event even if there are conflicts (user can resolve)
                event_result = await calendar_service.create_event_google(provider, meeting_details)
                
                if event_result and event_result.get('event_id'):
                    # Update meeting details with Google Calendar info
                    meeting_details['event_id'] = event_result['event_id']
                    meeting_details['meet_link'] = event_result.get('meet_link')
                    meeting_details['html_link'] = event_result.get('html_link')
                    meeting_details['detected_from_email'] = True
                    meeting_details['confidence'] = meeting_confidence
                    
                    event_created = await calendar_service.save_event(
                        email.user_id,
                        provider.id,
                        meeting_details,
                        email.id,
                        email.thread_id  # Pass thread_id for reminder sending
                    )
                    
                    # Store event for draft generation (convert to dict for MongoDB compatibility)
                    update_data['calendar_event'] = event_created.model_dump() if hasattr(event_created, 'model_dump') else event_created
                    
                    await add_action(email_id, "calendar_event_created", {
                        "event_id": event_result['event_id'],
                        "title": meeting_details.get('title'),
                        "start_time": meeting_details.get('start_time'),
                        "meet_link": event_result.get('meet_link'),
                        "has_conflicts": has_conflict
                    })
                    
                    logger.info(f"Created calendar event for email {email.id} with Meet link: {event_result.get('meet_link')}")
                else:
                    await add_action(email_id, "calendar_event_creation_failed", {
                        "message": "Failed to create event in Google Calendar"
                    }, "failed")
        
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
                validation_issues=update_data.get('validation_issues') if attempt > 0 else None,
                calendar_event=update_data.get('calendar_event')
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
                logger.info(f"Auto-send conditions met for email {email.id}. Sending reply...")
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
                        
                        # Create automatic follow-ups for sent emails based on account settings
                        if account.follow_up_enabled:
                            from models.follow_up import FollowUp
                            
                            # Create multiple follow-ups based on account settings
                            follow_ups_created = []
                            for i in range(account.follow_up_count):
                                days_offset = account.follow_up_days * (i + 1)
                                follow_up_date = datetime.now(timezone.utc) + timedelta(days=days_offset)
                                
                                # Customize message based on follow-up number
                                if i == 0:
                                    body = f"Just following up on my previous email regarding: {email.subject}\n\nLet me know if you have any questions.\n\n{account.signature if account.signature else 'Best regards'}"
                                elif i == 1:
                                    body = f"I wanted to circle back on my email about: {email.subject}\n\nHave you had a chance to review it?\n\n{account.signature if account.signature else 'Best regards'}"
                                else:
                                    body = f"Final follow-up regarding: {email.subject}\n\nPlease let me know if you need any additional information.\n\n{account.signature if account.signature else 'Best regards'}"
                                
                                follow_up = FollowUp(
                                    user_id=email.user_id,
                                    email_id=email.id,
                                    email_account_id=email.email_account_id,
                                    thread_id=email.thread_id,  # Store thread_id for same conversation
                                    scheduled_at=follow_up_date.isoformat(),
                                    subject=f"Follow-up #{i+1}: {email.subject}",
                                    body=body
                                )
                                
                                await db.follow_ups.insert_one(follow_up.model_dump())
                                follow_ups_created.append({
                                    "number": i + 1,
                                    "scheduled_at": follow_up_date.isoformat(),
                                    "days_from_now": days_offset
                                })
                            
                            await add_action(email_id, "follow_ups_scheduled", {
                                "follow_ups": follow_ups_created,
                                "total_count": len(follow_ups_created)
                            })
                            logger.info(f"Scheduled {len(follow_ups_created)} follow-ups for email {email.id}")
                        else:
                            logger.info(f"Follow-ups disabled for account {account.email}")
                    else:
                        update_data['status'] = 'error'
                        update_data['error_message'] = "Failed to send email"
                        await add_action(email_id, "send_failed", {"error": "Failed to send"}, "failed")
                        logger.error(f"Failed to send email {email.id}")
            else:
                logger.info(f"Auto-send not triggered for email {email.id}: intent has auto_send=False")
        else:
            reason = []
            if not intent_id:
                reason.append("no intent matched")
            if not update_data.get('draft_validated'):
                reason.append("draft not validated")
            logger.info(f"Auto-send skipped for email {email.id}: {', '.join(reason)}")
        
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

async def send_calendar_notification(email: Email, event, email_service, has_conflict=False, conflict_details=None):
    """Send email notification about created calendar event"""
    try:
        account = await email_service.get_account(email.email_account_id)
        if not account:
            return
        
        from models.email import EmailSend
        
        # Build conflict warning if applicable
        conflict_warning = ""
        if has_conflict and conflict_details:
            conflict_warning = f"""

⚠️  SCHEDULING CONFLICT DETECTED  ⚠️

The following existing event(s) conflict with this meeting:
"""
            for conflict in conflict_details:
                conflict_warning += f"""
• {conflict['title']}
  Time: {conflict['start_time']} to {conflict['end_time']}
"""
            conflict_warning += """
Please review and reschedule if needed.
"""
        
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
{conflict_warning}

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
                # Send in same thread if thread_id exists
                sent = await email_service.send_email_oauth_gmail(account, follow_up_email, follow_up.thread_id)
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
