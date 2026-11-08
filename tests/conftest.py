import pytest
import logging
import os
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

# Path to store authenticated session (cookies, local storage, etc.)
RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "..", "resources")
AUTH_STATE_FILE = os.path.join(RESOURCES_DIR, "auth_state.json")

# Ensure resources directory exists
os.makedirs(RESOURCES_DIR, exist_ok=True)

@pytest.fixture(scope="session")
def browser_context():
    """Setup Playwright browser with session persistence to handle MFA once."""
    with sync_playwright() as p:
        # Check if running in CI environment (headless mode)
        headless = os.getenv("HEADLESS", "false").lower() == "true"
        browser = p.chromium.launch(headless=headless)

        # Try to load existing authenticated session
        if os.path.exists(AUTH_STATE_FILE):
            logger.info("Loading saved authenticated session (MFA not needed)")
            context = browser.new_context(storage_state=AUTH_STATE_FILE)
        else:
            logger.warning("No saved session found. You'll need to login with MFA once.")
            context = browser.new_context()

        yield context

        # Save the session state after tests complete
        try:
            context.storage_state(path=AUTH_STATE_FILE)
            logger.info("Saved authenticated session for future test runs")
        except Exception as e:
            logger.warning(f"Could not save session: {e}")

        browser.close()

@pytest.fixture
def page(browser_context):
    """Provides a fresh page for each test."""
    page = browser_context.new_page()
    yield page
    page.close()