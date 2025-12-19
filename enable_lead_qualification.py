"""
Enable lead qualification and nurturing for the test user
"""
import os
from pymongo import MongoClient
import uuid
from datetime import datetime, timezone

def enable_lead_qualification():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = MongoClient(mongo_url)
    db = client['email_assistant_db']
    
    print("=" * 80)
    print("ENABLING LEAD QUALIFICATION & NURTURING")
    print("=" * 80)
    
    # Get user
    users_collection = db['users']
    user = users_collection.find_one({"email": "amits.joys@gmail.com"})
    
    if not user:
        print("\n❌ User not found")
        return
    
    user_id = user['id']
    print(f"\n📧 User: {user['email']} (ID: {user_id})")
    
    # Step 1: Create nurturing config
    nurturing_config_id = str(uuid.uuid4())
    nurturing_config = {
        "id": nurturing_config_id,
        "user_id": user_id,
        "max_exchanges": 3,
        "natural_integration": True,
        "questions_per_exchange": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    db['lead_nurturing_config'].delete_many({"user_id": user_id})
    db['lead_nurturing_config'].insert_one(nurturing_config)
    print(f"\n✅ Created nurturing config (ID: {nurturing_config_id})")
    
    # Step 2: Create qualification criteria
    qualification_criteria_id = str(uuid.uuid4())
    qualification_criteria = {
        "id": qualification_criteria_id,
        "user_id": user_id,
        "name": "Default Qualification Criteria",
        "is_active": True,
        "is_enabled": True,
        "min_exchanges_before_check": 1,
        "required_fields": [
            {
                "field_name": "company_size",
                "field_type": "text",
                "weight": 30,
                "validation_rule": "required"
            },
            {
                "field_name": "budget",
                "field_type": "text",
                "weight": 40,
                "validation_rule": "required"
            },
            {
                "field_name": "industry",
                "field_type": "text",
                "weight": 30,
                "validation_rule": "required"
            }
        ],
        "scoring_rules": {
            "company_size": {
                "1-10": 20,
                "11-50": 50,
                "51-200": 80,
                "200+": 100
            },
            "budget": {
                "< $1k": 20,
                "$1k-$5k": 50,
                "$5k-$10k": 80,
                "$10k+": 100
            }
        },
        "qualification_threshold": 60,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    db['lead_qualification_criteria'].delete_many({"user_id": user_id})
    db['lead_qualification_criteria'].insert_one(qualification_criteria)
    print(f"✅ Created qualification criteria (ID: {qualification_criteria_id})")
    
    # Step 3: Update user with global settings
    update_result = users_collection.update_one(
        {"id": user_id},
        {
            "$set": {
                "global_lead_nurturing_enabled": True,
                "global_lead_qualification_enabled": True,
                "default_nurturing_config_id": nurturing_config_id,
                "default_qualification_criteria_id": qualification_criteria_id,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    print(f"✅ Updated user with global settings (modified: {update_result.modified_count})")
    
    # Step 4: Update intents to enable lead nurturing and qualification
    intents_collection = db['intents']
    
    # Find intents that are marked as leads or have lead-related keywords
    lead_keywords = ['pricing', 'demo', 'inquiry', 'quote', 'interest', 'product', 'service']
    
    # Update specific intents
    updated_count = 0
    for intent in intents_collection.find({"user_id": user_id}):
        intent_name = intent.get('name', '').lower()
        keywords = [k.lower() for k in intent.get('keywords', [])]
        
        # Check if this intent should be a lead intent
        is_lead_intent = (
            intent.get('is_lead', False) or
            any(kw in intent_name for kw in lead_keywords) or
            any(any(lkw in kw for lkw in lead_keywords) for kw in keywords)
        )
        
        if is_lead_intent:
            intents_collection.update_one(
                {"id": intent['id']},
                {
                    "$set": {
                        "is_lead": True,
                        "enable_lead_nurturing": True,
                        "enable_lead_qualification": True,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            updated_count += 1
            print(f"   ✅ Updated intent: {intent['name']}")
    
    print(f"\n✅ Updated {updated_count} intents with lead qualification enabled")
    
    # Step 5: Verify configuration
    print("\n" + "=" * 80)
    print("CONFIGURATION VERIFICATION")
    print("=" * 80)
    
    updated_user = users_collection.find_one({"id": user_id})
    print(f"\n🌐 Global Settings:")
    print(f"   - global_lead_nurturing_enabled: {updated_user.get('global_lead_nurturing_enabled', False)}")
    print(f"   - global_lead_qualification_enabled: {updated_user.get('global_lead_qualification_enabled', False)}")
    print(f"   - default_nurturing_config_id: {updated_user.get('default_nurturing_config_id', 'Not set')}")
    print(f"   - default_qualification_criteria_id: {updated_user.get('default_qualification_criteria_id', 'Not set')}")
    
    lead_intents = list(intents_collection.find({
        "user_id": user_id,
        "is_lead": True
    }))
    
    print(f"\n📋 Lead Intents ({len(lead_intents)}):")
    for intent in lead_intents:
        print(f"   - {intent['name']}")
        print(f"     enable_lead_nurturing: {intent.get('enable_lead_nurturing', False)}")
        print(f"     enable_lead_qualification: {intent.get('enable_lead_qualification', False)}")
    
    print("\n" + "=" * 80)
    print("✅ CONFIGURATION COMPLETE!")
    print("=" * 80)
    
    client.close()

if __name__ == "__main__":
    enable_lead_qualification()
