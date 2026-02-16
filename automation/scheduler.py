"""
PromoChecker - Task Scheduler
Schedules automated scraping tasks using APScheduler
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from automation.run_scrapers import run_full_pipeline

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
    
    logger.info("🚀 Starting task scheduler")
    
    # Create scheduler
    scheduler = BackgroundScheduler(
        daemon=True,
        timezone='Africa/Tunis'  # Tunisia timezone
    )
    
    # Schedule daily scraping at 2:00 AM
    scheduler.add_job(
        scheduled_scraping_task,
        trigger=CronTrigger(hour=2, minute=0),
        id='daily_scraping',
        name='Daily Product Scraping',
        replace_existing=True,
        max_instances=1  # Prevent overlapping runs
    )
    
    logger.info("📅 Scheduled task: Daily scraping at 2:00 AM (Africa/Tunis)")
    
    # Optional: Add more frequent task for testing (every hour)
    # Uncomment to enable hourly scraping
    # scheduler.add_job(
    #     scheduled_scraping_task,
    #     trigger=CronTrigger(minute=0),
    #     id='hourly_scraping',
    #     name='Hourly Product Scraping',
    #     replace_existing=True,
    #     max_instances=1
    # )
    
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
    # For testing: start scheduler and run task immediately
    print("Starting scheduler...")
    start_scheduler()
    
    print("\nRunning task immediately for testing...")
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
