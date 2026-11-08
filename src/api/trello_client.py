import requests
from requests.exceptions import HTTPError, RequestException, ConnectionError, Timeout
from config.settings import API_KEY, API_TOKEN, BOARD_ID_SHORT
import backoff
import logging

logger = logging.getLogger(__name__)

MAX_TRIES = 5
MAX_TIME = 300  # 5 minutes max total retry time

def _backoff_handler(details):
    """Handler for backoff retries with detailed logging."""
    wait_time = details.get('wait', 0)
    tries = details.get('tries', 0)
    exception = details.get('exception', None)

    if exception:
        logger.warning(
            f"Trello API error (attempt {tries}/{MAX_TRIES}). "
            f"Retrying in {wait_time:.2f}s. Error: {str(exception)}"
        )
    else:
        logger.warning(f"Retrying Trello API call (attempt {tries}/{MAX_TRIES}) in {wait_time:.2f}s")


def _giveup_handler(details):
    """Handler called when all retries are exhausted."""
    exception = details.get('exception', None)
    tries = details.get('tries', 0)
    logger.error(
        f"Trello API call failed after {tries} attempts. "
        f"Final error: {str(exception)}"
    )


class TrelloClient:
    """Wrapper for Trello API interactions with robust error handling."""

    BASE_URL = "https://api.trello.com/1"

    def __init__(self):
        self.auth = {
            'key': API_KEY,
            'token': API_TOKEN
        }

    @backoff.on_exception(
        backoff.expo,
        (HTTPError, ConnectionError, Timeout, RequestException),
        max_tries=MAX_TRIES,
        max_time=MAX_TIME,
        on_backoff=_backoff_handler,
        on_giveup=_giveup_handler,
        logger=None,
    )
    def get_cards_on_board(self):
        """Fetches all cards from the configured board."""
        url = f"{self.BASE_URL}/boards/{BOARD_ID_SHORT}/cards"
        response = requests.get(url, params=self.auth)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch cards: {response.status_code} - {response.text}")

        return response.json()