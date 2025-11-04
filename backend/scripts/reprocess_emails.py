"""
Reprocess failed/unprocessed emails
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from config import config
from workers.email_worker import process_email


async def reprocess_unprocessed_emails():
    """Find and reprocess all unprocessed emails"""
    
    client = AsyncIOMotorClient(config.MONGO_URL)
    db = client[config.DB_NAME]
    
    try:
        # Find all unprocessed emails
        unprocessed = await db.emails.find({
            "processed": False,
            "status": {"$in": ["received", "error"]}
        }).to_list(100)
        
        print(f"Found {len(unprocessed)} unprocessed emails")
        
        for email_doc in unprocessed:
            email_id = email_doc['id']
            subject = email_doc.get('subject', 'N/A')
            print(f"\nReprocessing: {subject}")
            
            try:
                await process_email(email_id)
                print(f"  ✓ Processed successfully")
            except Exception as e:
                print(f"  ✗ Error: {e}")
        
        print(f"\n✅ Reprocessing complete")
        
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(reprocess_unprocessed_emails())
