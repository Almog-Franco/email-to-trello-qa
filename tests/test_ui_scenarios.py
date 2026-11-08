import pytest
import logging
import os
from src.ui.login_page import LoginPage
from src.ui.board_page import BoardPage
from config.settings import USER_EMAIL, USER_PASSWORD, BOARD_URL
from utils.steps import Prepare, Action, Verify

logger = logging.getLogger(__name__)

# Path to check for authenticated session
AUTH_STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "resources", "auth_state.json")


@pytest.fixture
def setup_board(page):
    """Navigates to board, using existing authenticated session if available."""
    with Prepare("Navigate to Trello board"):
        board_page = BoardPage(page)

        # Check if we have an authenticated session
        if os.path.exists(AUTH_STATE_FILE):
            # Session exists - just navigate directly to the board
            logger.info("Using saved authenticated session")
            board_page.navigate(BOARD_URL)
        else:
            # No session - need to login first
            logger.warning("No saved session - performing login")
            login_page = LoginPage(page)
            login_page.login(USER_EMAIL, USER_PASSWORD)
            board_page.navigate(BOARD_URL)

    return board_page


def test_scenario_1_urgent_cards(setup_board):
    """
    Validate that a specific urgent card has the 'Urgent' label.
    Parametrized to test each urgent card individually for better coverage.
    """


    with Prepare(f"Acquire urgent cards"):
        board_page = setup_board
        urgent_cards = board_page.get_urgent_cards()

    with Action("Open card and get details"):
        cards_details = []
        for card in urgent_cards:
            card_title = card.get_by_test_id("card-name").inner_text()
            board_page.open_card_by_title(card_title)
            details = board_page.get_card_modal_details()
            cards_details.append(details)
            board_page.close_modal()

        # Report details
        for details in cards_details:
            logger.info(f"Card: {details['title']} | Status: {details['status']} | Labels: {details['labels']} | Description: {details['description'] if details['description'] else 'N/A'}")




def test_scenario_2_specific_card(setup_board):
    """Validate specific 'summarize the meeting' card."""
    board_page = setup_board

    with Prepare("Define expected values for the card"):
        target_title = "summarize the meeting"

        # Expected Description based on Mock Data Merging Logic
        # Mail 1 (08:02:20): "For all of us"
        # Mail 2 (08:02:32): "Please do so"
        expected_desc = "For all of us\nPlease do so"

    with Action("Open card and get details"):
        board_page.open_card_by_title(target_title)
        details = board_page.get_card_modal_details()

    with Verify("Assert card has correct title, description, labels, and status"):
        assert details['title'] == target_title, (
            f"Title mismatch:\n"
            f"  Expected: {target_title}\n"
            f"  Actual: {details['title']}"
        )

        assert expected_desc in details['description'], (
            f"Description mismatch:\n"
            f"  Expected to contain: {repr(expected_desc)}\n"
            f"  Actual description: {repr(details['description'])}"
        )

        assert "New" in details['labels'], (
            f"Missing 'New' label:\n"
            f"  Found labels: {details['labels']}"
        )

        assert "To Do" in details['status'], (
            f"Status mismatch:\n"
            f"  Expected: 'To Do'\n"
            f"  Actual: {details['status']}"
        )

        board_page.close_modal()

