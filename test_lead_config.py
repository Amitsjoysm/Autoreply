"""
Test script to check lead qualification configuration
"""
import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import get_settings

async def check_configuration():
    """Check user and intent configuration for lead processing"""
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongo_url)
    db = client[settings.mongo_db_name]
    
    print("=" * 80)
    print("LEAD QUALIFICATION CONFIGURATION CHECK")
    print("=" * 80)
    
    # Get test user
    users_collection = db['users']
    user = await users_collection.find_one({"email": "test@example.com"})
    
    if not user:
        print("\n❌ Test user not found")
        return
    
    print(f"\n📧 User: {user['email']}")
    print(f"   User ID: {user['id']}")
    print(f"\n🌐 Global Settings:")
    print(f"   - global_lead_nurturing_enabled: {user.get('global_lead_nurturing_enabled', False)}")
    print(f"   - global_lead_qualification_enabled: {user.get('global_lead_qualification_enabled', False)}")
    print(f"   - default_nurturing_config_id: {user.get('default_nurturing_config_id', 'Not set')}")
    print(f"   - default_qualification_criteria_id: {user.get('default_qualification_criteria_id', 'Not set')}")
    
    # Get intents
    intents_collection = db['intents']
    intents = await intents_collection.find({"user_id": user['id']}).to_list(None)
    
    print(f"\n📋 Intents ({len(intents)}):")
    for intent in intents:
        print(f"\n   Intent: {intent['name']}")
        print(f"   - enable_lead_nurturing: {intent.get('enable_lead_nurturing', False)}")
        print(f"   - enable_lead_qualification: {intent.get('enable_lead_qualification', False)}")
        print(f"   - is_lead: {intent.get('is_lead', False)}")
        print(f"   - keywords: {intent.get('keywords', [])[:3]}...")
    
    # Get nurturing config
    nurturing_config_collection = db['lead_nurturing_config']
    nurturing_configs = await nurturing_config_collection.find({"user_id": user['id']}).to_list(None)
    
    print(f"\n🔧 Nurturing Configs ({len(nurturing_configs)}):")
    for config in nurturing_configs:
        print(f"\n   Config ID: {config['id']}")
        print(f"   - max_exchanges: {config.get('max_exchanges', 0)}")
        print(f"   - natural_integration: {config.get('natural_integration', True)}")
    
    # Get qualification criteria
    criteria_collection = db['lead_qualification_criteria']
    criteria = await criteria_collection.find({"user_id": user['id']}).to_list(None)
    
    print(f"\n✅ Qualification Criteria ({len(criteria)}):")
    for crit in criteria:
        print(f"\n   Criteria ID: {crit['id']}")
        print(f"   - min_exchanges: {crit.get('min_exchanges_before_check', 0)}")
        fields = crit.get('required_fields', [])
        print(f"   - required_fields ({len(fields)}): {[f['field_name'] for f in fields[:3]]}")
    
    # Get test leads
    leads_collection = db['inbound_leads']
    leads = await leads_collection.find({"user_id": user['id']}).sort("created_at", -1).limit(5).to_list(None)
    
    print(f"\n💡 Recent Leads ({len(leads)}):")
    for lead in leads:
        print(f"\n   Lead: {lead.get('lead_email', 'N/A')}")
        print(f"   - stage: {lead.get('stage', 'N/A')}")
        print(f"   - score: {lead.get('qualification_score', 0)}")
        print(f"   - attempt: {lead.get('qualification_attempt', 0)}")
        print(f"   - created_at: {lead.get('created_at', 'N/A')}")
    
    print("\n" + "=" * 80)
    
    # Check if configuration is complete
    global_nurturing = user.get('global_lead_nurturing_enabled', False)
    global_qualification = user.get('global_lead_qualification_enabled', False)
    
    lead_intents = [i for i in intents if i.get('is_lead', False)]
    intents_with_nurturing = [i for i in lead_intents if i.get('enable_lead_nurturing', False)]
    intents_with_qualification = [i for i in lead_intents if i.get('enable_lead_qualification', False)]
    
    print("\n📊 CONFIGURATION STATUS:")
    print(f"   ✅ Global Nurturing Enabled: {global_nurturing}")
    print(f"   ✅ Global Qualification Enabled: {global_qualification}")
    print(f"   ✅ Lead Intents: {len(lead_intents)}")
    print(f"   ✅ Intents with Nurturing: {len(intents_with_nurturing)}")
    print(f"   ✅ Intents with Qualification: {len(intents_with_qualification)}")
    print(f"   ✅ Nurturing Configs: {len(nurturing_configs)}")
    print(f"   ✅ Qualification Criteria: {len(criteria)}")
    
    if global_nurturing and global_qualification and intents_with_nurturing and intents_with_qualification:
        print("\n✅ CONFIGURATION COMPLETE - Lead processing should work!")
    else:
        print("\n⚠️  CONFIGURATION INCOMPLETE - Lead processing may not work!")
        if not global_nurturing:
            print("   - Enable global_lead_nurturing_enabled")
        if not global_qualification:
            print("   - Enable global_lead_qualification_enabled")
        if not intents_with_nurturing:
            print("   - Enable enable_lead_nurturing on lead intents")
        if not intents_with_qualification:
            print("   - Enable enable_lead_qualification on lead intents")
    
    print("=" * 80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_configuration())
