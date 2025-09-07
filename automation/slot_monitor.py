# playwright/slot_monitor.py
import asyncio
import logging
import random
import hashlib
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TARGET_URL = "https://visa.vfsglobal.com/moz/en/prt/apply"

# Enhanced selectors for better detection
SELECTORS = {
    'slot_container': [
        'div.available-dates',
        '.calendar',
        '#calendar',
        '[data-testid="calendar"]',
        '.appointment-calendar',
        '.date-picker',
        '.slot-container'
    ],
    'captcha': [
        'iframe[title*="CAPTCHA"]',
        'iframe[title*="captcha"]',
        '#captcha-container',
        '.captcha',
        '[data-testid="captcha"]',
        'iframe[src*="recaptcha"]'
    ],
    'no_slots': [
        'text=No available dates',
        'text=No appointments available',
        'text=No slots available',
        '.no-slots',
        '.unavailable'
    ],
    'loading': [
        '.loading',
        '.spinner',
        '[data-testid="loading"]',
        '.loader'
    ]
}

POLL_INTERVAL = 60
JITTER_RANGE = (1, 10)
MAX_RETRIES = 3

async def http_notify(payload: dict):
    """Send event to FastAPI webhook"""
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                "http://api:8000/webhooks/monitor-event",
                json=payload,
                timeout=5.0
            )
    except Exception as e:
        logger.error(f"Failed to send log: {e}")

async def detect_captcha(page):
    """Check if CAPTCHA is present on the page"""
    for selector in SELECTORS['captcha']:
        try:
            if await page.is_visible(selector, timeout=2000):
                return True
        except:
            continue
    return False

async def get_page_content(page):
    """Get slot container content with multiple selector fallbacks"""
    for selector in SELECTORS['slot_container']:
        try:
            await page.wait_for_selector(selector, timeout=5000)
            content = await page.inner_html(selector)
            if content and content.strip():
                return content.strip()
        except PlaywrightTimeout:
            continue
    return ""

def compute_hash(content: str) -> str:
    """Compute MD5 hash of content for change detection"""
    return hashlib.md5(content.encode()).hexdigest()

async def wait_for_page_load(page, timeout=30000):
    """Wait for page to fully load"""
    try:
        await page.wait_for_load_state("networkidle", timeout=timeout)
        await page.wait_for_timeout(2000)  # Additional wait for dynamic content
    except PlaywrightTimeout:
        logger.warning("Page load timeout, continuing anyway")

class MonitorState:
    """Track monitoring state and retry logic"""
    def __init__(self):
        self.retry_count = 0
        self.captcha_detected = False
        self.last_successful_check = None
        self.consecutive_errors = 0
        
    def should_retry(self):
        return self.retry_count < MAX_RETRIES
        
    def get_retry_delay(self):
        """Exponential backoff with jitter"""
        base_delay = min(60 * (2 ** self.retry_count), 300)  # Max 5 minutes
        jitter = random.uniform(0.5, 1.5)
        return base_delay * jitter
        
    def reset_retry(self):
        self.retry_count = 0
        self.consecutive_errors = 0
        self.last_successful_check = datetime.utcnow()

async def monitor_slots(run_id: str, notify_callback):
    """Enhanced slot monitoring with CAPTCHA handling and retry logic"""
    state = MonitorState()
    old_hash = None
    first_run = True
    browser = None
    context = None
    page = None

    try:
        async with async_playwright() as p:
            # Launch browser with better configuration
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1366, "height": 768},
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                }
            )
            page = await context.new_page()

            while True:
                timestamp = datetime.utcnow().strftime("%H:%M:%S")
                
                # Log checking status
                await http_notify({
                    "event": "slot_check",
                    "timestamp": timestamp,
                    "message": f"[{timestamp}] 🔍 Checking slots... (attempt {state.retry_count + 1})"
                })

                try:
                    # Navigate to page
                    await page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
                    await wait_for_page_load(page)
                    
                    # Check for CAPTCHA first
                    if await detect_captcha(page):
                        state.captcha_detected = True
                        state.consecutive_errors += 1
                        
                        await http_notify({
                            "event": "captcha_detected",
                            "timestamp": timestamp,
                            "message": f"[{timestamp}] ⚠️ CAPTCHA detected — monitoring paused. Manual intervention required."
                        })
                        
                        # Wait longer when CAPTCHA is detected
                        await asyncio.sleep(300)  # 5 minutes
                        continue
                    
                    # Get page content
                    content = await get_page_content(page)
                    
                    if not content:
                        state.consecutive_errors += 1
                        await http_notify({
                            "event": "no_content",
                            "timestamp": timestamp,
                            "message": f"[{timestamp}] ⚠️ No slot container found - page may have changed"
                        })
                        
                        if state.should_retry():
                            state.retry_count += 1
                            delay = state.get_retry_delay()
                            await asyncio.sleep(delay)
                            continue
                        else:
                            await http_notify({
                                "event": "monitor_failed",
                                "timestamp": timestamp,
                                "message": f"[{timestamp}] ❌ Max retries reached. Monitor stopping."
                            })
                            break
                    
                    # Reset retry count on successful content retrieval
                    state.reset_retry()
                    current_hash = compute_hash(content)

                    if first_run:
                        await http_notify({
                            "event": "monitor_started",
                            "timestamp": timestamp,
                            "message": f"[{timestamp}] ✅ Monitoring started successfully"
                        })
                        old_hash = current_hash
                        first_run = False
                    elif current_hash != old_hash:
                        await http_notify({
                            "event": "slots_found",
                            "timestamp": timestamp,
                            "message": f"[{timestamp}] 🎉 SLOT AVAILABLE! Book now!"
                        })
                        old_hash = current_hash
                    else:
                        await http_notify({
                            "event": "no_slots",
                            "timestamp": timestamp,
                            "message": f"[{timestamp}] ❌ No slots available"
                        })

                except Exception as e:
                    state.consecutive_errors += 1
                    logger.error(f"Monitoring error: {e}")
                    
                    await http_notify({
                        "event": "error",
                        "timestamp": timestamp,
                        "message": f"[{timestamp}] ❌ Error: {str(e)}"
                    })
                    
                    if state.should_retry():
                        state.retry_count += 1
                        delay = state.get_retry_delay()
                        await asyncio.sleep(delay)
                        continue
                    else:
                        await http_notify({
                            "event": "monitor_failed",
                            "timestamp": timestamp,
                            "message": f"[{timestamp}] ❌ Max retries reached. Monitor stopping."
                        })
                        break

                # Normal wait with jitter
                jitter = random.randint(*JITTER_RANGE)
                await asyncio.sleep(POLL_INTERVAL + jitter)

    except Exception as e:
        logger.error(f"Critical monitoring error: {e}")
        await http_notify({
            "event": "critical_error",
            "timestamp": datetime.utcnow().strftime("%H:%M:%S"),
            "message": f"❌ Critical error: {str(e)}"
        })
    finally:
        if browser:
            await browser.close()