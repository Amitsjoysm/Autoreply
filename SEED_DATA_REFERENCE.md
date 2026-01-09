# 🚀 Comprehensive Seed Data - Quick Reference

## User Credentials
- **Email:** amits.joys@gmail.com
- **Password:** ij@123...
- **Name:** Amit Joys

## What Was Created

### ✅ User Settings
- Global Lead Qualification: **ENABLED**
- Global Lead Nurturing: **ENABLED**
- Timezone: America/New_York
- Working Hours: 9 AM - 5 PM (Mon-Fri)
- Quota: 1000 emails/day

### 📋 Intents (5)
1. **🎯 Pricing Inquiry (Lead)** - Qualification ✓ | Nurturing ✓ | Auto-Send ✓
2. **🎯 Demo Request (Lead)** - Qualification ✓ | Nurturing ✓ | Auto-Send ✓
3. **🎯 Partnership Inquiry (Lead)** - Qualification ✓ | Auto-Send ✗
4. **📧 Support Request** - Regular intent, Auto-Send ✓
5. **📧 General Inquiry (Default)** - Default fallback intent

### 📚 Knowledge Base (8)
- Product Pricing (Starter, Professional, Enterprise)
- Key Features (AI Assistant, Campaigns, Lead Qualification)
- Integrations (Gmail/Outlook, Calendar Sync)

### 🎯 Lead Qualification Criteria (1)
**B2B SaaS Lead Qualification** - Question-based criteria with 4 questions:
1. Company size
2. Timeline for implementation
3. Budget range
4. Decision-making authority

Min qualification score: 65%

### 🌱 Lead Nurturing Config (1)
**Standard B2B Nurturing** - 4 contextual questions:
1. Specific challenges to solve
2. Current process handling
3. Important features
4. Implementation timeline

Strategy: 2 questions per email, max 2 exchanges

### 📧 Campaign Templates (3)
1. **Cold Outreach - Introduction** (Initial)
2. **Follow-up 1 - Value Proposition**
3. **Follow-up 2 - Final Touch** (Breakup email)

All templates include personalization tags: {{first_name}}, {{company}}, {{industry}}, etc.

### 👥 Campaign Contacts (5)
1. **Sarah Johnson** - TechCorp Inc (VP of Sales) - Tags: technology, enterprise, hot-lead
2. **Michael Chen** - Startup Ventures (Founder & CEO) - Tags: saas, startup, founder
3. **Emily Rodriguez** - Growth Agency (Marketing Director) - Tags: marketing, agency
4. **David Kim** - Enterprise Solutions (CTO) - Tags: enterprise, technology, decision-maker
5. **Lisa Anderson** - Consulting Pro (Senior Consultant) - Tags: consulting, professional-services

### 📑 Contact Lists (3)
1. **Enterprise Prospects** - Large companies (1000+ employees)
2. **Startup Founders** - Early-stage companies
3. **Hot Leads Q1 2024** - High-priority leads

### 🎯 Sample Inbound Leads (3)
1. **Jennifer Williams** (Acme Corporation)
   - Stage: **Qualified** | Score: 85 | Priority: High
   - Intent: Pricing Inquiry | Nurturing: Active
   
2. **Robert Martinez** (Innovate Tech)
   - Stage: **New** | Score: 0 | Priority: Medium
   - Intent: Demo Request | Just received
   
3. **Patricia Brown** (Global Enterprises)
   - Stage: **Awaiting Info** | Score: 45 | Priority: High
   - Intent: Pricing Inquiry | Waiting for answers

## How to Use

### Run Seed Script
```bash
# From root directory
python seed_database.py

# Or from backend directory
cd backend
python scripts/comprehensive_seed_data.py
```

### Login to App
1. Navigate to the app URL
2. Email: `amits.joys@gmail.com`
3. Password: `ij@123...`

### What You Can Do Immediately

#### ✅ View Intents
- Go to **Initial Setup → Intents**
- See all 5 intents with lead controls
- Edit or create new intents

#### ✅ Explore Lead Controls
- Go to **Initial Setup → Lead Controls**
- See global settings (already enabled)
- View qualification and nurturing status

#### ✅ Check Knowledge Base
- Go to **Settings → Knowledge Base**
- See 8 entries covering pricing, features, integrations

#### ✅ View Inbound Leads
- Go to **Inbound Leads**
- See 3 sample leads in different stages
- Test lead qualification and nurturing

#### ✅ Create Campaign
- Go to **Campaigns → Create Campaign**
- Select from 5 contacts
- Use pre-built templates
- Set up follow-ups

#### ✅ View Contact Lists
- Go to **Contacts → Lists**
- See 3 organized lists
- Manage contacts

## What Requires User Action

### 🔌 Email Account Connection
- Go to **Settings → Email Accounts**
- Connect Gmail or Outlook via OAuth
- Enable auto-reply and follow-ups

### 📅 Calendar Connection
- Go to **Settings → Calendar**
- Connect Google or Microsoft Calendar
- Enable meeting detection

### 💼 HubSpot Integration (Optional)
- Go to **Settings → Integrations**
- Connect HubSpot account
- Enable lead sync

## Scripts Location

- **Main Script:** `/app/backend/scripts/comprehensive_seed_data.py`
- **Convenience Script:** `/app/seed_database.py`
- **Archive:** `/app/backend/scripts/archive/` (old scripts)
- **Documentation:** `/app/backend/scripts/README.md`

## Safe to Re-run

The seed script is **safe to run multiple times**:
- Updates existing user
- Recreates all data fresh
- No duplicate issues

## Models Not Seeded

These models are created dynamically by the app:
- **Email** - Created when emails received
- **Email Account** - Requires OAuth connection
- **Campaign** - User creates campaigns
- **Campaign Email** - Created when campaign runs
- **Campaign Follow Up** - Created when campaign runs
- **Follow Up** - Created when follow-ups scheduled
- **Calendar Provider** - Requires OAuth connection
- **Calendar Event** - Created when meetings detected
- **HubSpot Credential** - Requires OAuth connection

---

**✨ Your app is fully seeded and ready to explore all features!**
