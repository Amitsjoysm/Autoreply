#!/usr/bin/env python3
"""
Worker script to run background tasks for email processing
"""
import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from workers.email_worker import poll_all_accounts, check_follow_ups, check_reminders

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def run_email_polling():
    """Run email polling worker"""
    while True:
        try:
            await poll_all_accounts()
        except Exception as e:
            logger.error(f"Error in email polling: {e}", exc_info=True)
        await asyncio.sleep(60)  # Poll every 60 seconds


async def run_follow_up_worker():
    """Run follow-up checking worker"""
    while True:
        try:
            await check_follow_ups()
        except Exception as e:
            logger.error(f"Error in follow-up worker: {e}", exc_info=True)
        await asyncio.sleep(300)  # Check every 5 minutes


async def run_reminder_worker():
    """Run reminder checking worker"""
    while True:
        try:
            await check_reminders()
        except Exception as e:
            logger.error(f"Error in reminder worker: {e}", exc_info=True)
        await asyncio.sleep(3600)  # Check every 1 hour


async def main():
    """Run all workers concurrently"""
    logger.info("Starting email workers...")
    logger.info("- Email polling: Every 60 seconds")
    logger.info("- Follow-up checking: Every 5 minutes")
    logger.info("- Reminder checking: Every 1 hour")
    
    await asyncio.gather(
        run_email_polling(),
        run_follow_up_worker(),
        run_reminder_worker(),
        return_exceptions=True
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Workers stopped by user")
    except Exception as e:
        logger.error(f"Fatal error in workers: {e}", exc_info=True)
        sys.exit(1)
