import pytest
import logging
from src.api.gmail_client import GmailClient
from src.api.trello_client import TrelloClient
from config.settings import MOCK_DATA_PATH
from utils.utilities import get_test_data, get_urgent_cards_test_data
from utils.steps import Prepare, Action, Verify

logger = logging.getLogger(__name__)

test_data = get_test_data(GmailClient, TrelloClient, MOCK_DATA_PATH)

@pytest.mark.parametrize(
    "card_subject,expected_card,actual_cards_map",
    test_data,
    ids=lambda x: x if isinstance(x, str) else None
)
def test_card_description_sync(card_subject, expected_card, actual_cards_map):
    """
    Validates that card descriptions are properly synced and merged from Gmail to Trello.
    Tests existence and description merging logic.
    """
    with Prepare("Get expected and actual card data"):
        # Verify card exists in Trello
        assert card_subject in actual_cards_map, (
            f"Missing Card: '{card_subject}' exists in Gmail but not in Trello."
        )

        actual_card = actual_cards_map[card_subject]

        exp_desc = expected_card['description']
        act_desc = actual_card['desc']

    with Action("Compare expected and actual descriptions"):
        # Main comparison happens here
        description_matches = exp_desc == act_desc

    with Verify("Assert description is synced correctly"):
        assert description_matches, (
            f"Description Mismatch for '{card_subject}':\n"
            f"  Expected: {repr(exp_desc)}\n"
            f"  Actual:   {repr(act_desc)}"
        )

        logger.info(f"[PASS] '{card_subject}' - Description verified")


@pytest.mark.parametrize(
    "card_subject,expected_card,actual_cards_map",
    get_urgent_cards_test_data(all_test_data=test_data),
    ids=lambda x: x if isinstance(x, str) else None
)
def test_card_urgent_label_sync(card_subject, expected_card, actual_cards_map):
    """
    Validates that urgent labels are properly applied to cards from Gmail to Trello.
    Only tests cards that should have the urgent label.
    """
    with Prepare("Get card data for urgent card"):
        actual_card = actual_cards_map[card_subject]

    with Action("Extract labels from the card"):
        card_labels = actual_card.get('labels', [])
        labels = [l.get('name', '') for l in card_labels if isinstance(l, dict)]

    with Verify("Assert 'Urgent' label is present"):
        assert "Urgent" in labels, (
            f"Urgent Label Missing for '{card_subject}':\n"
            f"  Expected: 'Urgent' label present\n"
            f"  Actual labels: {labels}"
        )

        logger.info(f"[PASS] '{card_subject}' - Urgent label verified")


def test_no_extra_cards_in_trello():
    """
    Validates that Trello doesn't contain cards that don't exist in Gmail.
    This test runs separately to check the reverse sync direction.
    Uses the global test_data for consistency and efficiency.
    """
    with Prepare("Extract expected and actual card subjects from test data"):
        # Get expected subjects from test_data (already loaded Gmail data)
        expected_subjects = {card_subject for card_subject, _, _ in test_data}

        # Get actual subjects from test_data (already fetched Trello data)
        # All test_data entries share the same actual_cards_map
        _, _, actual_cards_map = test_data[0]
        actual_subjects = set(actual_cards_map.keys())

    with Action("Find cards in Trello that don't exist in Gmail"):
        extra_cards = actual_subjects - expected_subjects

    with Verify("Assert no extra cards exist in Trello"):
        assert not extra_cards, (
            f"\nExtra cards found in Trello that don't exist in Gmail:\n"
            f"  {', '.join(repr(card) for card in sorted(extra_cards))}"
        )

        logger.info(f"[PASS] No extra cards in Trello - All {len(actual_subjects)} cards match Gmail")
