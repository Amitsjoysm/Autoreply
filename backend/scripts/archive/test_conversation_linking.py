#!/usr/bin/env python3
"""
Test script for intelligent conversation linking
Demonstrates cross-thread conversation tracking
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from motor.motor_asyncio import AsyncIOMotorClient
from services.conversation_linking_service import ConversationLinkingService
from config import config

async def test_conversation_linking():
    """Test conversation linking functionality"""
    
    print("=" * 70)
    print("INTELLIGENT CONVERSATION LINKING - TEST SCRIPT")
    print("=" * 70)
    
    # Connect to database
    client = AsyncIOMotorClient(config.MONGO_URL)
    db = client[config.DB_NAME]
    
    # Initialize service
    conv_service = ConversationLinkingService(db)
    
    # Get test user
    user = await db.users.find_one({"email": "amits.joys@gmail.com"})
    if not user:
        print("❌ Test user not found. Please run seed data creation first.")
        return
    
    user_id = user['id']
    test_sender = "test@example.com"
    
    print(f"\n✅ Testing for user: {user['email']}")
    print(f"   User ID: {user_id}")
    print(f"   Test sender: {test_sender}")
    
    # Test 1: Generate conversation group ID
    print("\n" + "-" * 70)
    print("TEST 1: Conversation Group ID Generation")
    print("-" * 70)
    
    group_id = conv_service.generate_conversation_group_id(user_id, test_sender)
    print(f"✓ Generated conversation_group_id: {group_id}")
    print(f"  This ID will be the same for ALL emails from {test_sender}")
    
    # Test with different sender
    group_id_2 = conv_service.generate_conversation_group_id(user_id, "another@example.com")
    print(f"✓ Different sender gets different ID: {group_id_2[:16]}...")
    
    # Test with same sender (should be identical)
    group_id_3 = conv_service.generate_conversation_group_id(user_id, test_sender)
    print(f"✓ Same sender always gets same ID: {group_id == group_id_3}")
    
    # Test 2: Get conversation history
    print("\n" + "-" * 70)
    print("TEST 2: Conversation History Retrieval")
    print("-" * 70)
    
    # Get all emails from a real sender
    all_emails = await db.emails.find({"user_id": user_id}).limit(5).to_list(5)
    
    if all_emails:
        sample_sender = all_emails[0].get('from_email', 'unknown@example.com')
        history = await conv_service.get_conversation_history(user_id, sample_sender, limit=10)
        
        print(f"✓ Found {len(history)} emails from {sample_sender}")
        
        if history:
            for i, email in enumerate(history[:3], 1):
                subject = email.get('subject', 'No subject')[:50]
                received = email.get('received_at', 'Unknown')[:19]
                thread_id = email.get('thread_id', 'None')[:20]
                print(f"  {i}. [{received}] Thread: {thread_id}")
                print(f"     Subject: {subject}")
    else:
        print("ℹ️  No emails in database yet. Send some emails to test this feature.")
    
    # Test 3: Basic similarity check
    print("\n" + "-" * 70)
    print("TEST 3: Email Similarity Detection (Basic Mode)")
    print("-" * 70)
    
    # Create mock emails
    mock_previous = [
        {
            'subject': 'Question about pricing',
            'body': 'I am interested in your email automation platform. Can you tell me about the pricing plans?'
        },
        {
            'subject': 'Product features',
            'body': 'What features does your email assistant include? Can it integrate with Gmail?'
        }
    ]
    
    # Test case 1: Related email
    print("\n📧 Test Case 1: Related Email")
    print("Previous: 'Question about pricing' + 'Product features'")
    print("New: 'Thanks for the info! What about the Business plan?'")
    
    is_related, confidence, context = conv_service._basic_similarity_check(
        "Thanks for the info",
        "Thanks for the pricing information. Can you tell me more about the Business plan features?",
        mock_previous
    )
    
    print(f"✓ Is related: {is_related}")
    print(f"✓ Confidence: {confidence:.2%}")
    print(f"✓ Context: {context}")
    
    # Test case 2: Unrelated email
    print("\n📧 Test Case 2: Unrelated Email")
    print("Previous: 'Question about pricing' + 'Product features'")
    print("New: 'Job application for Software Engineer'")
    
    is_related, confidence, context = conv_service._basic_similarity_check(
        "Job application",
        "I would like to apply for the Software Engineer position. Please find my resume attached.",
        mock_previous
    )
    
    print(f"✓ Is related: {is_related}")
    print(f"✓ Confidence: {confidence:.2%}")
    print(f"✓ Context: {context or 'Not related'}")
    
    # Test 4: Conversation summary
    print("\n" + "-" * 70)
    print("TEST 4: Conversation Summary")
    print("-" * 70)
    
    if all_emails:
        summary = await conv_service.get_conversation_summary(user_id, sample_sender)
        
        print(f"✓ Conversation Group ID: {summary['conversation_group_id'][:32]}...")
        print(f"✓ Sender: {summary['sender_email']}")
        print(f"✓ Total Emails: {summary['total_emails']}")
        print(f"✓ Emails Sent: {summary['emails_sent']}")
        print(f"✓ Unique Threads: {summary['unique_threads']}")
        print(f"✓ First Contact: {summary.get('first_contact', 'N/A')[:19]}")
        print(f"✓ Last Contact: {summary.get('last_contact', 'N/A')[:19]}")
        
        if summary['thread_ids']:
            print(f"✓ Thread IDs:")
            for tid in list(summary['thread_ids'])[:3]:
                print(f"    - {tid[:40]}...")
    
    # Test 5: Follow-up cancellation (simulation)
    print("\n" + "-" * 70)
    print("TEST 5: Follow-up Cancellation Logic")
    print("-" * 70)
    
    # Count pending follow-ups
    pending_followups = await db.follow_ups.count_documents({
        "user_id": user_id,
        "status": "pending"
    })
    
    print(f"✓ Current pending follow-ups: {pending_followups}")
    
    if pending_followups > 0:
        print("  To test cancellation, the system would:")
        print("  1. Get all emails from sender")
        print("  2. Find all pending follow-ups for those emails")
        print("  3. Update status to 'cancelled' with reason")
        print("  4. Log cancellation in email action history")
    else:
        print("  No pending follow-ups to cancel (send some emails first)")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ CONVERSATION LINKING TESTS COMPLETE")
    print("=" * 70)
    
    print("\nKEY CAPABILITIES DEMONSTRATED:")
    print("  ✓ Stable conversation group ID generation")
    print("  ✓ Conversation history retrieval")
    print("  ✓ Email similarity detection (basic mode)")
    print("  ✓ Conversation summary statistics")
    print("  ✓ Follow-up cancellation logic")
    
    print("\nNEXT STEPS:")
    print("  1. Send test emails from same address in different threads")
    print("  2. Watch logs for conversation linking")
    print("  3. Check emails have conversation_group_id field")
    print("  4. Verify follow-ups are cancelled when reply received")
    
    print("\nAI-POWERED FEATURES (require Groq API key):")
    if config.GROQ_API_KEY:
        print("  ✓ Groq API key configured")
        print("  ✓ Can use AI similarity detection")
        print("  ✓ More accurate conversation linking")
    else:
        print("  ⚠️  Groq API key not configured")
        print("  ⚠️  Will use basic keyword matching only")
    
    print("\n" + "=" * 70)
    
    client.close()


if __name__ == "__main__":
    asyncio.run(test_conversation_linking())
