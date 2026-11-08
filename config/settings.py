import os

from dotenv import load_dotenv

# Credentials are never committed: set them in the environment or in a local .env file (see .env.example).
load_dotenv()


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable {name}. Copy .env.example to .env and fill it in.")
    return value


API_KEY = _required("TRELLO_API_KEY")
API_TOKEN = _required("TRELLO_API_TOKEN")

BOARD_ID_SHORT = _required("TRELLO_BOARD_ID")
BOARD_URL = f"https://trello.com/b/{BOARD_ID_SHORT}"

USER_EMAIL = _required("TRELLO_USER_EMAIL")
USER_PASSWORD = _required("TRELLO_USER_PASSWORD")

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCK_DATA_PATH = os.path.join(BASE_DIR, 'data', 'mock_gmail_data.json')
