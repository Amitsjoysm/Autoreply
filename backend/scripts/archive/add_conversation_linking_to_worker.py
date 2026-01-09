#!/usr/bin/env python3
"""
Integration guide for adding intelligent conversation linking to email worker

This script provides the code changes needed to integrate cross-thread
conversation tracking into the existing email processing workflow.
"""

integration_guide = """
=============================================================================
INTELLIGENT CROSS-THREAD CONVERSATION TRACKING - INTEGRATION GUIDE
=============================================================================

WHAT THIS SOLVES:
-----------------
1. Users reply in different email threads (not using "Reply" button)
2. System loses conversation context
3. Follow-ups get duplicated
4. AI responses don't reference previous discussions

SOLUTION OVERVIEW:
------------------
1. Group all emails by sender email address (conversation_group_id)
2. Use AI to detect if new thread is related to previous conversations
3. Aggregate context from ALL related emails for better AI responses
4. Cancel follow-ups across ALL threads when ANY reply is received
5. Track conversation statistics (total emails, unique threads, etc.)

HOW IT WORKS:
-------------

┌─────────────────────────────────────────────────────────────┐
│  User sends initial email (Thread A)                        │
│  Subject: "Question about your product"                     │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  System processes email                                     │
│  - Creates conversation_group_id (hash of user + sender)    │
│  - Generates reply with context                             │
│  - Creates follow-ups                                       │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  User starts NEW EMAIL instead of replying (Thread B) ❌    │
│  Subject: "Follow-up on my previous question"               │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Enhanced Processing (NEW!) ✅                              │
│  1. Link to same conversation_group_id                      │
│  2. AI checks similarity with Thread A (85% match)          │
│  3. Retrieve full context from Thread A                     │
│  4. Cancel ALL pending follow-ups (Thread A + B)            │
│  5. Generate reply with complete conversation history       │
└─────────────────────────────────────────────────────────────┘


INTEGRATION STEPS:
==================

STEP 1: Import the new services
--------------------------------
Add to top of workers/email_worker.py:

```python
from services.conversation_linking_service import ConversationLinkingService
from services.enhanced_email_processor import EnhancedEmailProcessor
```


STEP 2: Initialize services in process_email()
-----------------------------------------------
Add after existing service initialization:

```python
async def process_email(email_id: str):
    # ... existing code ...
    ai_service = AIAgentService(db)
    email_service = EmailService(db)
    
    # NEW: Add conversation intelligence
    enhanced_processor = EnhancedEmailProcessor(db)
    
    # Get email
    email_doc = await db.emails.find_one({"id": email_id})
    if not email_doc:
        return
    
    email = Email(**email_doc)
```


STEP 3: Process with conversation context
------------------------------------------
Add BEFORE intent classification:

```python
    # NEW: Process with conversation intelligence
    conversation_result = await enhanced_processor.process_email_with_conversation_context(email)
    
    logger.info(
        f"Conversation analysis for {email.from_email}: "
        f"continuation={conversation_result['is_continuation']}, "
        f"previous_emails={conversation_result['previous_emails_count']}, "
        f"threads={conversation_result['unique_threads']}, "
        f"followups_cancelled={conversation_result['followups_cancelled']}"
    )
    
    # Add to action history
    await add_action(email_id, "conversation_analyzed", {
        "conversation_group_id": conversation_result['conversation_group_id'],
        "is_continuation": conversation_result['is_continuation'],
        "similarity_score": conversation_result['similarity_score'],
        "previous_emails": conversation_result['previous_emails_count'],
        "unique_threads": conversation_result['unique_threads'],
        "context": conversation_result['related_context']
    })
    
    # ... continue with intent classification ...
```


STEP 4: Use enhanced draft generation
--------------------------------------
Replace existing draft generation call with:

```python
    # OLD:
    # draft = await ai_service.generate_draft(
    #     email=email,
    #     user_id=email.user_id,
    #     intent_doc=intent_doc,
    #     thread_context=thread_context,
    #     calendar_event=calendar_event
    # )
    
    # NEW: Use enhanced draft generation with full conversation context
    draft = await enhanced_processor.generate_draft_with_full_context(
        email=email,
        intent_doc=intent_doc,
        calendar_event=calendar_event,
        validation_issues=validation_issues  # If in retry loop
    )
```


STEP 5: Smart follow-up creation
---------------------------------
Replace follow-up creation logic:

```python
    # OLD:
    # if not is_simple_ack and not is_time_based_followup:
    #     await create_standard_followups(email, intent_doc, auto_send_enabled)
    
    # NEW: Check if follow-ups should be created
    should_create = await enhanced_processor.should_create_followups(email)
    
    if should_create and not is_simple_ack and not is_time_based_followup:
        await create_standard_followups(email, intent_doc, auto_send_enabled)
        logger.info(f"Created follow-ups for new conversation from {email.from_email}")
    elif not should_create:
        logger.info(f"Skipped follow-up creation - this is a reply in the conversation")
        await add_action(email_id, "followup_skipped", {
            "reason": "Detected as reply in ongoing conversation"
        })
```


STEP 6: Update Email model (optional but recommended)
-----------------------------------------------------
Add these fields to models/email.py:

```python
class Email(BaseModel):
    # ... existing fields ...
    
    # Conversation Intelligence Fields
    conversation_group_id: Optional[str] = None  # Groups all emails from same sender
    is_conversation_continuation: bool = False  # Is this a reply in different thread?
    conversation_similarity_score: float = 0.0  # AI confidence score
    total_conversation_emails: int = 1  # Total emails in this conversation
    conversation_thread_count: int = 1  # Number of different threads
```


DATABASE MIGRATION (Optional):
------------------------------
Add conversation_group_id to existing emails:

```python
# Run this once to migrate existing data
from services.conversation_linking_service import ConversationLinkingService

async def migrate_existing_emails():
    conversation_service = ConversationLinkingService(db)
    
    # Get all emails
    emails = await db.emails.find({}).to_list(10000)
    
    for email in emails:
        if not email.get('conversation_group_id'):
            conversation_group_id = conversation_service.generate_conversation_group_id(
                email['user_id'],
                email['from_email']
            )
            
            await db.emails.update_one(
                {"id": email['id']},
                {"$set": {"conversation_group_id": conversation_group_id}}
            )
    
    print(f"✅ Migrated {len(emails)} emails with conversation IDs")
```


TESTING THE FEATURE:
====================

Test Scenario 1: Basic Conversation Linking
-------------------------------------------
1. Send email from alice@example.com (Subject: "Question about pricing")
2. System replies and creates follow-ups
3. Send NEW email from alice@example.com (Subject: "Thanks! One more thing...")
4. ✅ System should:
   - Detect as continuation (check conversation_similarity_score)
   - Cancel previous follow-ups
   - Include context from first email in reply
   - NOT create duplicate follow-ups

Test Scenario 2: Unrelated New Topic
------------------------------------
1. Send email from bob@example.com (Subject: "Product inquiry")
2. System replies
3. Send NEW email from bob@example.com (Subject: "Job application")
4. ✅ System should:
   - Detect as NEW conversation (similarity_score < 0.7)
   - Create new follow-ups
   - Not cancel previous follow-ups

Test Scenario 3: Multiple Thread Replies
-----------------------------------------
1. Send 3 emails from carol@example.com in different threads
2. Each about the same project
3. ✅ System should:
   - Link all to same conversation_group_id
   - Show conversation_thread_count = 3
   - Cancel follow-ups when ANY reply received
   - Use context from all 3 threads in responses


MONITORING AND LOGS:
====================

Key log messages to watch:
--------------------------
✓ "Conversation analysis for alice@example.com: continuation=True, previous_emails=2, threads=2"
✓ "Cancelled 3 pending follow-ups across 2 threads for alice@example.com"
✓ "Retrieved cross-thread context for email abc123 from alice@example.com"
✓ "Not creating follow-ups for email xyz789 - appears to be a reply (confidence: 0.85)"

Database queries to check:
--------------------------
# Check conversation grouping
db.emails.aggregate([
    {$group: {
        _id: "$conversation_group_id",
        count: {$sum: 1},
        senders: {$addToSet: "$from_email"},
        threads: {$addToSet: "$thread_id"}
    }}
])

# Check follow-up cancellations
db.follow_ups.find({
    status: "cancelled",
    cancellation_reason: /Reply received/
})


BENEFITS:
=========
✅ No lost context when users reply in different threads
✅ Intelligent follow-up management (no duplicates)
✅ Better AI responses with full conversation history
✅ Automatic conversation grouping
✅ Works across multiple email threads seamlessly
✅ Reduces support tickets about "duplicate emails"
✅ Improves customer experience with coherent responses


CONFIGURATION:
==============

Similarity threshold (in conversation_linking_service.py):
self.similarity_threshold = 0.7  # Adjust from 0.0 to 1.0
  - Higher = stricter matching (fewer false positives)
  - Lower = looser matching (catches more related emails)
  - Recommended: 0.6-0.8

Context window (max emails in history):
max_emails = 5  # Last N emails to include in context
  - Trade-off between context richness and token usage
  - Recommended: 5-10 emails


FALLBACK BEHAVIOR:
==================
If AI service is unavailable, the system falls back to:
- Basic keyword matching (30% overlap threshold)
- Still links emails by sender
- Still cancels follow-ups
- Reduced confidence scores (capped at 0.6)


=============================================================================
For questions or issues, check the logs or review:
- /app/backend/services/conversation_linking_service.py
- /app/backend/services/enhanced_email_processor.py
=============================================================================
"""

print(integration_guide)
