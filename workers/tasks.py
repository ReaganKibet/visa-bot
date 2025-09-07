# workers/tasks.py
from celery import Celery
from config.settings import REDIS_URL

# Add project root to path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

# Fix the import - renamed directory to avoid conflict
from automation.slot_monitor import monitor_slots
import asyncio
from automation.utils import take_screenshot, log_action

celery_app = Celery('tasks', broker=REDIS_URL)

# The missing task
@celery_app.task
def start_monitor(run_id: str):
    """
    Wrapper task to start monitoring for appointment slots.
    Called by FastAPI when POST /monitors/ is hit.
    """
    print(f"[start_monitor] Starting monitor for run_id={run_id}")
    try:
        # Run async monitor in sync context
        asyncio.run(monitor_slots(run_id, notify_via_api))
    except Exception as e:
        print(f"[start_monitor] Failed: {e}")
        import traceback
        traceback.print_exc()
        raise

# Dummy notification callback (will connect to Telegram later)
async def notify_via_api(alert: dict):
    print("🔔 SLOT ALERT: ", alert)
    # Later: call Telegram bot or POST to webhook

# Enhanced booking task with form data
@celery_app.task
def trigger_booking(applicant_id: str, run_id: str, form_data: dict = None):
    try:
        from workers.booking_flow import launch_booking_session_sync
        launch_booking_session_sync(applicant_id, run_id, form_data)
    except Exception as e:
        print(f"Booking failed: {e}")
        raise