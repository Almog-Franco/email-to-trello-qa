def get_test_data(GmailClient, TrelloClient, mock_data_path):
    """
    Fixture helper to prepare test data for parametrization.
    Returns list of tuples: (card_subject, expected_card_data, actual_cards_map)
    """
    # 1. Prepare Expected State (Mock Gmail)
    gmail = GmailClient(mock_data_path)
    gmail.load_data()
    expected_cards = gmail.get_expected_trello_state()

    # 2. Fetch Actual State (Trello API)
    trello = TrelloClient()
    actual_cards_list = trello.get_cards_on_board()

    # Helper: Map actual cards by title for easy lookup
    actual_cards_map = {c['name']: c for c in actual_cards_list}

    # Create test parameters: one per expected card
    test_params = [
        (subject, expected_data, actual_cards_map)
        for subject, expected_data in expected_cards.items()
    ]

    return test_params


def get_urgent_cards_test_data(all_test_data):
    """
    Fixture helper to prepare test data for urgent cards only.
    Returns list of tuples: (card_subject, expected_card_data, actual_cards_map)
    Only includes cards that are marked as urgent.
    """

    # Filter only urgent cards
    urgent_test_data = [
        (subject, expected_data, actual_cards_map)
        for subject, expected_data, actual_cards_map in all_test_data
        if expected_data['is_urgent']
    ]

    return urgent_test_data


def get_urgent_card_titles(GmailClient, mock_data_path):
    """
    Helper to get list of urgent card titles for UI test parametrization.
    Returns list of card titles that should have the Urgent label.
    """
    gmail = GmailClient(mock_data_path)
    gmail.load_data()
    expected_cards = gmail.get_expected_trello_state()

    # Get titles of urgent cards only
    urgent_titles = [
        title
        for title, card_data in expected_cards.items()
        if card_data['is_urgent']
    ]

    return urgent_titles

