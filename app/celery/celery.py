from celery import Celery
import requests
import time

from app.core.constants import BASE_URL, API_KEY, REDIS_URL
from app.campaigns.models import Campaign
from app.core.database import SessionLocal

# Create a Celery app
celery_app = Celery('tasks', broker=REDIS_URL)  

# Defining the task that will call the endpoint
@celery_app.task
def mark_expired_campaigns_inactive():
    """
    Query active campaigns whose expiration timestamp has passed and mark them as inactive.
    """
    db = SessionLocal()
    try:
        now = int(time.time())
        # Query for campaigns that are still active but have passed their expiration date.
        expired_campaigns = db.query(Campaign).filter(
            Campaign.expiration < now,
            Campaign.is_active == True
        ).all()

        # Mark each campaign as inactive.
        for campaign in expired_campaigns:
            campaign.is_active = False

        db.commit()
        print(f"Marked {len(expired_campaigns)} campaigns as inactive.")
    except Exception as e:
        db.rollback()
        print(f"Error marking expired campaigns as inactive: {e}")
    finally:
        db.close()

# Schedule the task to run every 30 minutes.
celery_app.conf.beat_schedule = {
    'mark-expired-campaigns-inactive-every-30-minutes': {
        'task': 'tasks.mark_expired_campaigns_inactive',
        'schedule': 30 * 60,  # Every 30 minutes (in seconds)
    },
}

