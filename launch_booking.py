#!/usr/bin/env python3
"""
Standalone booking launcher for host machine
Run this script on your local machine to launch the booking browser
"""

import asyncio
import json
import sys
from playwright.async_api import async_playwright

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
        print(f"Navigation warning: {e}")
        return False

async def autofill_form(page, applicant_data):
    """Auto-fill the booking form"""
    print("📝 Starting form auto-fill...")
    
    for field_name, selectors in BOOKING_SELECTORS['form_fields'].items():
        value = applicant_data.get(field_name)
        if not value:
            continue
            
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    await element.fill(value)
                    print(f"✅ Filled {field_name}: {value}")
                    break
            except Exception as e:
                print(f"Failed to fill {field_name}: {e}")
                continue

async def main():
    """Main booking session"""
    print("🚀 Starting Visa Booking Session")
    print("=" * 50)
    
    # Default applicant data (you can modify this)
    applicant_data = {
        "first_name": "John",
        "last_name": "Doe",
        "dob": "1990-01-01",
        "passport": "A12345678"
    }
    
    # Allow user to input their data
    print("📝 Enter your details (or press Enter to use defaults):")
    first_name = input(f"First Name [{applicant_data['first_name']}]: ").strip()
    if first_name:
        applicant_data['first_name'] = first_name
        
    last_name = input(f"Last Name [{applicant_data['last_name']}]: ").strip()
    if last_name:
        applicant_data['last_name'] = last_name
        
    dob = input(f"Date of Birth (YYYY-MM-DD) [{applicant_data['dob']}]: ").strip()
    if dob:
        applicant_data['dob'] = dob
        
    passport = input(f"Passport Number [{applicant_data['passport']}]: ").strip()
    if passport:
        applicant_data['passport'] = passport
    
    print(f"\n✅ Using data: {applicant_data}")
    print("🌐 Launching browser...")
    
    async with async_playwright() as p:
        # Launch browser in visible mode
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--start-maximized"
            ]
        )
        
        context = await browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            # Navigate to VFS website
            print("🌐 Navigating to VFS website...")
            await page.goto(VFS_URL, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)

            # Navigate through booking flow
            await navigate_to_booking_form(page)
            
            # Check for CAPTCHA
            if await detect_captcha(page):
                print("\n" + "="*60)
                print("🚨 CAPTCHA DETECTED!")
                print("👉 Please solve the CAPTCHA in the browser window")
                print("👉 Complete any facial verification if required")
                print("👉 Press Enter when you're ready to continue")
                print("="*60 + "\n")
                
                input("🛑 Press Enter after solving CAPTCHA...")

            # Auto-fill form
            await autofill_form(page, applicant_data)
            
            print("\n" + "="*60)
            print("✅ BOOKING SESSION READY!")
            print("👉 Review the form data in the browser")
            print("👉 Click 'Submit' or 'Book Appointment' when ready")
            print("👉 Press Enter when you've submitted the form")
            print("="*60 + "\n")
            
            # Wait for user to submit
            input("🛑 Press Enter after submitting the form...")
            
            print("✅ Booking session completed!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await browser.close()
            print("🔚 Browser closed")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Booking session cancelled by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
