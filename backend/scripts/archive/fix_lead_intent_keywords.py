"""
Fix lead intent keywords and priorities to ensure proper lead tracking
"""

import asyncio
import sys
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from config import config
from datetime import datetime, timezone

async def fix_lead_intents():
    """Update lead intent keywords and priorities"""
    
    client = AsyncIOMotorClient(config.MONGO_URL)
    db = client[config.DB_NAME]
    
    # Get user
    user_doc = await db.users.find_one({"email": "amits.joys@gmail.com"})
    if not user_doc:
        print("❌ User not found")
        return
    
    user_id = user_doc['id']
    print(f"✅ User: {user_doc['email']} (ID: {user_id})")
    
    print("\n" + "="*70)
    print("🔧 FIXING LEAD INTENT CONFIGURATION")
    print("="*70)
    
    # Update Pricing Request intent
    pricing_result = await db.intents.update_one(
        {
            "user_id": user_id,
            "name": "Pricing Request"
        },
        {
            "$set": {
                "keywords": [
                    "pricing", "cost", "price", "plan", "plans",
                    "subscription", "payment", "how much", "fee", 
                    "charge", "quote", "enterprise pricing", "pricing information",
                    "pricing details", "pricing options"
                ],
                "priority": 9,  # Increase from 7 to 9 (higher than General Inquiry)
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if pricing_result.modified_count > 0:
        print("\n✅ Updated Pricing Request intent:")
        print("   - Added more specific pricing keywords")
        print("   - Increased priority from 7 → 9")
    
    # Update Demo Request intent
    demo_result = await db.intents.update_one(
        {
            "user_id": user_id,
            "name": "Demo Request"
        },
        {
            "$set": {
                "keywords": [
                    "demo", "demonstration", "trial", "test", "try",
                    "show me", "walkthrough", "see the product",
                    "product demo", "demo request", "schedule demo",
                    "watch demo", "live demo"
                ],
                "priority": 9,  # Increase from 8 to 9 (same as Pricing)
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if demo_result.modified_count > 0:
        print("\n✅ Updated Demo Request intent:")
        print("   - Added more specific demo keywords")
        print("   - Priority: 9 (unchanged)")
    
    # Update General Inquiry to have more specific keywords
    general_result = await db.intents.update_one(
        {
            "user_id": user_id,
            "name": "General Inquiry"
        },
        {
            "$set": {
                "keywords": [
                    "question about", "inquiry about", "tell me about",
                    "what is", "how does", "curious about", "wondering about",
                    "can you explain", "need information", "find out more"
                ],
                "priority": 5,  # Keep lower priority
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if general_result.modified_count > 0:
        print("\n✅ Updated General Inquiry intent:")
        print("   - Removed broad single-word keywords")
        print("   - Added more specific phrase-based keywords")
        print("   - Priority: 5 (unchanged)")
    
    # Verify changes
    print("\n" + "="*70)
    print("📋 VERIFICATION")
    print("="*70)
    
    intents = await db.intents.find({
        "user_id": user_id,
        "name": {"$in": ["Pricing Request", "Demo Request", "General Inquiry"]}
    }).to_list(10)
    
    for intent in intents:
        lead_flag = "🎯" if intent.get('is_inbound_lead', False) else "  "
        print(f"\n{lead_flag} {intent['name']} (Priority: {intent.get('priority', 0)})")
        print(f"   Keywords ({len(intent.get('keywords', []))}): {', '.join(intent.get('keywords', [])[:5])}...")
        print(f"   Lead tracking: {intent.get('is_inbound_lead', False)}")
    
    print("\n" + "="*70)
    print("✅ Lead intent configuration updated!")
    print("="*70)
    print("\n💡 CHANGES SUMMARY:")
    print("   • Pricing Request: Priority 7 → 9, more specific keywords")
    print("   • Demo Request: Priority stays 9, more specific keywords")
    print("   • General Inquiry: Removed broad keywords, more specific phrases")
    print("\n   This should improve lead capture for pricing and demo inquiries!")

if __name__ == "__main__":
    asyncio.run(fix_lead_intents())
