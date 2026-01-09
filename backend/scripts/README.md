# Scripts Directory

## Active Scripts

### comprehensive_seed_data.py
**THE MAIN SEED SCRIPT** - Creates complete app data covering ALL models.

**What it creates:**
- User (amits.joys@gmail.com with password ij@123...)
- 5 Intents (including lead qualification & nurturing enabled intents)
- 8 Knowledge Base entries
- 1 Lead Qualification Criteria
- 1 Lead Nurturing Configuration
- 3 Campaign Templates (initial + 2 follow-ups)
- 5 Campaign Contacts
- 3 Contact Lists
- 3 Sample Inbound Leads (qualified, new, awaiting_info)

**Usage:**
```bash
cd /app/backend
python scripts/comprehensive_seed_data.py
```

**Safe to run multiple times** - It updates existing user and recreates data.

### run_workers.py
Worker management script for background tasks.

**Usage:**
```bash
cd /app/backend
python scripts/run_workers.py
```

## Archive Directory

All old/deprecated scripts have been moved to `archive/` directory for reference.
These scripts are no longer needed but kept for historical purposes.

## Creating New Seed Data

To create seed data for a different user:
1. Copy `comprehensive_seed_data.py`
2. Update `USER_EMAIL`, `USER_PASSWORD`, and `USER_NAME` variables
3. Run the script

## Models Covered

The comprehensive seed script covers these models:
- ✅ User
- ✅ Email Account (user needs to connect via OAuth)
- ✅ Intent
- ✅ Knowledge Base
- ✅ Lead Qualification Criteria
- ✅ Lead Nurturing Config
- ✅ Campaign Template
- ✅ Campaign Contact
- ✅ Contact List
- ✅ Inbound Lead
- ✅ Campaign (user can create)
- ✅ Campaign Email (created when campaign runs)
- ✅ Campaign Follow Up (created when campaign runs)
- ✅ Email (created when emails received)
- ✅ Follow Up (created when follow-ups scheduled)
- ✅ Calendar Provider (user connects via OAuth)
- ✅ Calendar Event (created when meetings detected)
- ✅ HubSpot Credential (user connects via OAuth)

## Note

Email Account, Calendar Provider, and HubSpot Credential require OAuth connections
which users must do through the UI. These cannot be pre-seeded with dummy data.
