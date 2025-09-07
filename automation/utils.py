# playwright/utils.py
import asyncio
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def take_screenshot(page, filename_prefix: str) -> str:
    """
    Take a screenshot and save it with timestamp.
    Returns the filename of the saved screenshot.
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.png"
        
        # Create screenshots directory if it doesn't exist
        screenshots_dir = Path("logs/screenshots")
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = screenshots_dir / filename
        await page.screenshot(path=str(filepath), full_page=True)
        
        logger.info(f"Screenshot saved: {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Failed to take screenshot: {e}")
        return ""

async def log_action(run_id: str, action: str, data: dict):
    """
    Log an action to file or database.
    """
    try:
        timestamp = datetime.utcnow().isoformat()
        log_entry = {
            "run_id": run_id,
            "timestamp": timestamp,
            "action": action,
            "data": data
        }
        
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Log to file (you can extend this to log to database later)
        log_file = logs_dir / f"monitor_{run_id}.log"
        with open(log_file, "a") as f:
            f.write(f"{timestamp} [{action}] {data}\n")
            
        logger.info(f"Action logged: {run_id} - {action}")
    except Exception as e:
        logger.error(f"Failed to log action: {e}")