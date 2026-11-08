from .base_page import BasePage
from playwright.sync_api import TimeoutError as PlaywrightTimeout, Error as PlaywrightError
import logging

logger = logging.getLogger(__name__)


class BoardPage(BasePage):
    """Handles Board Interactions with robust error handling."""

    def get_urgent_cards(self):
        """
        Finds all cards with the 'Urgent' label.

        Returns:
            list: List of urgent card elements, or empty list if none found or error occurs
        """
        self.page.wait_for_load_state("networkidle", timeout=30000)
        try:
            cards = self.page.get_by_test_id("list-card").all()
            urgent_cards = []

            for card in cards:
                card.scroll_into_view_if_needed()
                labels = card.get_by_test_id('compact-card-label').all()
                for label in labels:
                    if label.inner_text() == "Urgent":
                        urgent_cards.append(card)
                        continue
            logger.info(f"Found {len(urgent_cards)} urgent cards")
            return urgent_cards

        except PlaywrightError as e:
            logger.error(f"Error finding urgent cards: {e}")
            return []

    def open_card_by_title(self, title):
        """
        Clicks a card to open its modal.

        Args:
            title: The title of the card to open

        Raises:
            PlaywrightTimeout: If card cannot be found or modal doesn't open
        """
        try:
            # Use data-testid for card name and filter by text
            card_selector = f"a[data-testid='card-name']:has-text('{title}')"

            # Wait for card to be available
            self.page.wait_for_selector(card_selector, state="visible", timeout=10000)
            self.page.locator(card_selector).first.click()

            # Wait for the dialog/modal to appear
            self.page.wait_for_selector("[data-testid='card-back-name']", state="visible", timeout=10000)
            logger.info(f"Successfully opened card: {title}")

        except PlaywrightError as e:
            logger.error(f"Error opening card '{title}': {e}")
            raise

    def get_card_modal_details(self):
        """
        Extracts data from the open card modal with comprehensive error handling.

        Returns:
            dict: Card details with keys: title, description, labels, status, error (if any)
        """
        error_response = {
            "title": "",
            "description": "",
            "labels": [],
            "status": "",
            "error": None
        }

        # Wait for modal to be fully loaded
        try:
            self.page.locator("[data-testid='card-back-title-input']").wait_for(
                state="visible", timeout=10000
            )
        except PlaywrightTimeout:
            logger.error("Card modal failed to load within timeout")
            error_response["error"] = "Modal load timeout"
            return error_response

        # Extract title safely
        try:
            title_elem = self.page.locator("[data-testid='card-back-title-input']")
            if title_elem.count() > 0:
                title = title_elem.input_value()
            else:
                logger.warning("Title element not found")
                title = ""
        except PlaywrightError as e:
            logger.warning(f"Error extracting title: {e}")
            title = ""

        # Extract description safely
        try:
            desc_elem = self.page.locator("[data-testid='description-content-area']")
            if desc_elem.count() > 0:
                description = desc_elem.inner_text()
            else:
                logger.debug("Description element not found (may be empty)")
                description = ""
        except PlaywrightError as e:
            logger.warning(f"Error extracting description: {e}")
            description = ""

        # Extract labels safely
        labels = []
        try:
            self.page.locator("[data-testid=card-back-labels-container]").wait_for(
                state="visible", timeout=5000
            )
            labels_elem = self.page.locator("[data-testid=card-back-labels-container]")
            if labels_elem.count() > 0:
                labels_text = labels_elem.inner_text()
                labels = [l.strip() for l in labels_text.split('\n') if l.strip()]
            else:
                logger.debug("Labels container not found")
        except PlaywrightTimeout:
            logger.debug("Labels container timeout (card may have no labels)")
        except PlaywrightError as e:
            logger.warning(f"Error extracting labels: {e}")

        # Extract status safely
        try:
            status_elem = self.page.locator(".lrbK2IonIC94Mu")
            if status_elem.count() > 0:
                status = status_elem.inner_text()
            else:
                logger.warning("Status element not found")
                status = ""
        except PlaywrightError as e:
            logger.warning(f"Error extracting status: {e}")
            status = ""

        logger.info(f"Extracted card details - Title: {title}, Labels: {labels}, Status: {status}")

        return {
            "title": title,
            "description": description,
            "labels": labels,
            "status": status,
            "error": None
        }

    def close_modal(self):
        """
        Closes the card modal with error handling.

        Returns:
            bool: True if modal closed successfully, False otherwise
        """
        try:
            self.page.click("[data-testid='CloseIcon']", timeout=5000)
            self.page.wait_for_selector(
                "[data-testid='quick-card-editor-dialog']",
                state="hidden",
                timeout=5000
            )
            logger.info("Card modal closed successfully")
            return True

        except PlaywrightError as e:
            logger.error(f"Error closing modal: {e}")
            return False

