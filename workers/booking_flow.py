# workers/booking_flow.py
import asyncio
import logging
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VFS_URL = "https://visa.vfsglobal.com/moz/en/prt/apply"

# Enhanced selectors for booking flow
BOOKING_SELECTORS = {
    'apply_visa': [
        'text=Apply for a visa',
        'a[href*="apply"]',
        'button:has-text("Apply")',
        '[data-testid="apply-visa"]'
    ],
    'book_appointment': [
        'text=Book an appointment',
        'a[href*="appointment"]',
        'button:has-text("Book")',
        '[data-testid="book-appointment"]'
    ],
    'captcha': [
        'iframe[title*="CAPTCHA"]',
        'iframe[title*="captcha"]',
        '#captcha-container',
        '.captcha',
        'iframe[src*="recaptcha"]'
    ],
    'form_fields': {
        'first_name': ['input[name*="first"]', 'input[id*="first"]', 'input[placeholder*="First"]'],
        'last_name': ['input[name*="last"]', 'input[id*="last"]', 'input[placeholder*="Last"]'],
        'dob': ['input[name*="dob"]', 'input[id*="dob"]', 'input[type="date"]'],
        'passport': ['input[name*="passport"]', 'input[id*="passport"]', 'input[placeholder*="Passport"]']
    }
}

async def detect_captcha(page):
    """Check if CAPTCHA is present on the page"""
    for selector in BOOKING_SELECTORS['captcha']:
        try:
            if await page.is_visible(selector, timeout=2000):
                return True
        except:
            continue
    return False

async def wait_for_captcha_resolution(page, timeout=300000):
    """Wait for user to resolve CAPTCHA"""
    logger.info("🔍 Waiting for CAPTCHA resolution...")
    try:
        # Wait for CAPTCHA to disappear
        await page.wait_for_function(
            "() => !document.querySelector('iframe[title*=\"CAPTCHA\"]') && !document.querySelector('#captcha-container')",
            timeout=timeout
        )
        logger.info("✅ CAPTCHA resolved!")
        return True
    except PlaywrightTimeout:
        logger.warning("⚠️ CAPTCHA resolution timeout")
        return False

async def navigate_to_booking_form(page):
    """Navigate through the booking flow"""
    try:
        # Step 1: Click "Apply for a visa"
        for selector in BOOKING_SELECTORS['apply_visa']:
            try:
                await page.click(selector, timeout=5000)
                await page.wait_for_timeout(2000)
                break
            except:
                continue
        
        # Step 2: Click "Book an appointment"
        for selector in BOOKING_SELECTORS['book_appointment']:
            try:
                await page.click(selector, timeout=5000)
                await page.wait_for_timeout(3000)
                break
            except:
                continue
                
        return True
    except Exception as e:
        logger.warning(f"Navigation warning: {e}")
        return False

async def autofill_form(page, applicant_data):
    """Auto-fill the booking form"""
    logger.info("📝 Starting form auto-fill...")
    
    for field_name, selectors in BOOKING_SELECTORS['form_fields'].items():
        value = applicant_data.get(field_name)
        if not value:
            continue
            
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    await element.fill(value)
                    logger.info(f"✅ Filled {field_name}: {value}")
                    break
            except Exception as e:
                logger.warning(f"Failed to fill {field_name}: {e}")
                continue

async def launch_browser_on_host(applicant_id: str, run_id: str, form_data: dict = None):
    """Notify user to run booking script on host machine"""
    logger.info("🐳 Running in Docker - cannot launch browser directly")
    
    # Prepare form data for display
    form_data_display = form_data or {
        "first_name": "John",
        "last_name": "Doe", 
        "dob": "1990-01-01",
        "passport": "A12345678"
    }
    
    print("\n" + "="*80)
    print("🚀 BOOKING SESSION READY!")
    print("="*80)
    print("Since you're running in Docker, please run the booking script on your host machine:")
    print()
    print("1. Open a new terminal/command prompt")
    print("2. Navigate to your project directory")
    print("3. Run: python launch_booking.py")
    print()
    print("Your form data:")
    for key, value in form_data_display.items():
        print(f"   {key}: {value}")
    print()
    print("The script will:")
    print("✅ Launch a visible browser window")
    print("✅ Navigate to the VFS booking form")
    print("✅ Help you solve CAPTCHA")
    print("✅ Auto-fill your form data")
    print("✅ Wait for you to submit")
    print("="*80)
    
    logger.info("✅ Booking instructions provided to user")

async def launch_booking_session(applicant_id: str, run_id: str, form_data: dict = None):
    """Launch visible browser for booking with CAPTCHA handling"""
    logger.info(f"🌐 Launching booking session for {applicant_id}")
    
    # Check if we're running in Docker
    import os
    is_docker = os.path.exists('/.dockerenv')
    
    if is_docker:
        logger.info("🐳 Running in Docker - launching browser on host machine")
        # Launch browser on host machine instead of in container
        await launch_browser_on_host(applicant_id, run_id, form_data)
        return
    
    async with async_playwright() as p:
        # Launch browser in VISIBLE mode for CAPTCHA solving (when not in Docker)
        browser = await p.chromium.launch(
            headless=False,  # ✅ Make browser visible
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"  # Start maximized for better visibility
            ]
        )
        
        logger.info("✅ Browser launched successfully (visible mode)")
        
        context = await browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            # Navigate to VFS website
            logger.info("🌐 Navigating to VFS website...")
            await page.goto(VFS_URL, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)

            # Navigate through booking flow
            await navigate_to_booking_form(page)
            
            # Check for CAPTCHA and wait for resolution
            if await detect_captcha(page):
                logger.info("⚠️ CAPTCHA detected! Please solve it in the browser window.")
                print("\n" + "="*60)
                print("🚨 CAPTCHA DETECTED!")
                print("👉 Please solve the CAPTCHA in the browser window")
                print("👉 Complete any facial verification if required")
                print("👉 The system will continue automatically after resolution")
                print("="*60 + "\n")
                
                # Wait for CAPTCHA resolution
                if await wait_for_captcha_resolution(page, timeout=300000):  # 5 minutes
                    logger.info("✅ CAPTCHA resolved, continuing...")
                else:
                    logger.warning("⚠️ CAPTCHA resolution timeout")
                    print("⚠️ CAPTCHA resolution timeout. Please try again.")
                    return

            # Use provided form data or defaults
            applicant_data = form_data or {
                "first_name": "John",
                "last_name": "Doe", 
                "dob": "1990-01-01",
                "passport": "A12345678"
            }
            
            await autofill_form(page, applicant_data)
            
            print("\n" + "="*60)
            print("✅ BOOKING SESSION READY!")
            print("👉 Review the form data in the browser")
            print("👉 Click 'Submit' or 'Book Appointment' when ready")
            print("👉 The system will capture the confirmation PDF")
            print("="*60 + "\n")
            
            # Wait for user to submit the form
            logger.info("⏳ Waiting for form submission...")
            
            # Wait for either success page or PDF download
            try:
                await page.wait_for_function(
                    "() => window.location.href.includes('success') || window.location.href.includes('confirmation') || document.querySelector('a[href*=\".pdf\"]')",
                    timeout=3600000  # 1 hour timeout
                )
                logger.info("✅ Form submitted successfully!")
                
                # Try to capture PDF if available
                try:
                    pdf_link = await page.query_selector('a[href*=".pdf"]')
                    if pdf_link:
                        await pdf_link.click()
                        logger.info("📄 PDF downloaded")
                except:
                    logger.info("📄 No PDF link found")
                    
            except PlaywrightTimeout:
                logger.info("⏰ Session timeout reached")
                
        except Exception as e:
            logger.error(f"❌ Booking session error: {e}")
            print(f"❌ Error: {e}")
            
        finally:
            # Keep browser open for a bit to show results
            await page.wait_for_timeout(5000)
            await browser.close()
            logger.info("🔚 Booking session completed")

def launch_booking_session_sync(applicant_id: str, run_id: str, form_data: dict = None):
    print(f"🚀 Starting booking session for applicant: {applicant_id}, run_id: {run_id}")
    try:
        asyncio.run(launch_booking_session(applicant_id, run_id, form_data))
        print(f"✅ Booking session completed successfully for {applicant_id}")
    except Exception as e:
        print(f"❌ Booking failed for {applicant_id}: {e}")
        import traceback
        traceback.print_exc()
        raise