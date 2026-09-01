"""
PromoChecker - Task Scheduler
Schedules automated scraping tasks using APScheduler
"""
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
from pathlib import Path
import sys

from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from automation.run_scrapers import run_full_pipeline

load_dotenv()

# Schedule configuration (override in .env)
#   SCRAPE_ENABLED      - "false" to disable the in-process scheduler entirely
#   SCRAPE_DAY_OF_WEEK  - cron day: mon/tue/.../sun, or "*" for every day
#   SCRAPE_HOUR         - hour of day, 0-23
#   SCRAPE_MINUTE       - minute of hour, 0-59
#   SCRAPE_TIMEZONE     - IANA timezone name
SCRAPE_ENABLED = os.getenv('SCRAPE_ENABLED', 'true').strip().lower() not in (
    'false', '0', 'no'
)
SCRAPE_DAY_OF_WEEK = os.getenv('SCRAPE_DAY_OF_WEEK', 'sun').strip()
SCRAPE_HOUR = int(os.getenv('SCRAPE_HOUR', 3))
SCRAPE_MINUTE = int(os.getenv('SCRAPE_MINUTE', 0))
SCRAPE_TIMEZONE = os.getenv('SCRAPE_TIMEZONE', 'Africa/Tunis').strip()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None


def scheduled_scraping_task():
    """
    Task that runs on schedule to scrape and update database
    """
    logger.info("🕐 Scheduled scraping task started")
    try:
        results = run_full_pipeline()
        
        # Log results
        if results['database_import']:
            logger.info("✅ Scheduled scraping completed successfully")
        else:
            logger.warning("⚠️ Scheduled scraping completed with errors")
            
    except Exception as e:
        logger.error(f"❌ Scheduled scraping failed: {e}", exc_info=True)


def start_scheduler():
    """
    Start the background scheduler with configured tasks
    """
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler already running")
        return scheduler

    if not SCRAPE_ENABLED:
        logger.info("⏸️  Scheduler disabled (SCRAPE_ENABLED=false)")
        return None

    logger.info("🚀 Starting task scheduler")

    # Create scheduler
    scheduler = BackgroundScheduler(
        daemon=True,
        timezone=SCRAPE_TIMEZONE
    )

    # Weekly scraping (default: Sunday 03:00 Africa/Tunis)
    scheduler.add_job(
        scheduled_scraping_task,
        trigger=CronTrigger(
            day_of_week=SCRAPE_DAY_OF_WEEK,
            hour=SCRAPE_HOUR,
            minute=SCRAPE_MINUTE,
        ),
        id='weekly_scraping',
        name='Weekly Product Scraping',
        replace_existing=True,
        max_instances=1,   # never overlap two pipeline runs
        coalesce=True,     # a backlog of missed runs collapses into one
        # The pipeline takes minutes and the machine may be asleep at 03:00;
        # still run if we come back within 6 hours of the scheduled time.
        misfire_grace_time=6 * 3600,
    )

    logger.info(
        "📅 Scheduled task: scraping on '%s' at %02d:%02d (%s)",
        SCRAPE_DAY_OF_WEEK, SCRAPE_HOUR, SCRAPE_MINUTE, SCRAPE_TIMEZONE
    )

    # Start the scheduler
    scheduler.start()
    logger.info("✅ Scheduler started successfully")
    
    # Print next scheduled runs
    jobs = scheduler.get_jobs()
    for job in jobs:
        next_run = job.next_run_time
        logger.info(f"📌 Next run for '{job.name}': {next_run}")
    
    return scheduler


def stop_scheduler():
    """
    Stop the background scheduler
    """
    global scheduler
    
    if scheduler is None:
        logger.warning("Scheduler not running")
        return
    
    logger.info("🛑 Stopping task scheduler")
    scheduler.shutdown(wait=True)
    scheduler = None
    logger.info("✅ Scheduler stopped")


def run_task_now():
    """
    Manually trigger the scraping task immediately (for testing)
    """
    logger.info("🔄 Running scraping task manually")
    scheduled_scraping_task()


if __name__ == "__main__":
    # Run the scheduler standalone (no API needed):
    #   python automation/scheduler.py         -> wait for the next scheduled run
    #   python automation/scheduler.py --now   -> also scrape immediately, once
    print("Starting scheduler...")
    start_scheduler()

    if "--now" in sys.argv:
        print("\nRunning the pipeline immediately...")
        run_task_now()

    print("\nScheduler is running. Press Ctrl+C to stop.")
    try:
        # Keep the script running
        import time
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping scheduler...")
        stop_scheduler()
        print("Done!")
