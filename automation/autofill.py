# playwright/autofill.py
from playwright.async_api import Page
import logging

logger = logging.getLogger(__name__)

FIELD_MAPPING = {
    "first_name": 'label:has-text("First Name")',
    "last_name": 'label:has-text("Surname")',
    "dob": 'label:has-text("Date of Birth")',
    "passport_number": 'label:has-text("Passport Number")',
}

async def autofill_applicant_data(page: Page, applicant_data: dict):
    await page.wait_for_load_state("domcontentloaded")
    for field, selector in FIELD_MAPPING.items():
        try:
            input_field = await page.query_selector(f"{selector} + input, {selector} ~ input")
            if input_field:
                value = applicant_data.get(field)
                if value:
                    await input_field.fill(value)
                    logger.info(f"Filled {field}")
                    await page.screenshot(path=f"debug_{field}.png")
            else:
                logger.warning(f"Selector not found for {field}")
        except Exception as e:
            logger.error(f"Failed to fill {field}: {e}")
            await page.screenshot(path=f"error_{field}.png")