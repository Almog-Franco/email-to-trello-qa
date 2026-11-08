import json
import re
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GmailClient:
    """
    Simulates retrieving emails from a Gmail inbox by parsing a mock JSON file.
    Implements requirements with comprehensive error handling.
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.emails = []

    def load_data(self):
        """
        Parses the mock JSON file with error handling for missing files,
        invalid JSON, and malformed data.

        Raises:
            FileNotFoundError: If the mock data file doesn't exist
            ValueError: If the JSON is invalid or data structure is unexpected
        """
        if not os.path.exists(self.file_path):
            logger.error(f"Mock data file not found: {self.file_path}")
            raise FileNotFoundError(f"Mock data not found at {self.file_path}")

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in mock data file: {e}")
            raise ValueError(f"Invalid JSON format in {self.file_path}: {e}")
        except Exception as e:
            logger.error(f"Error reading mock data file: {e}")
            raise
        messages = data.get('messages', [])
        # Parse relevant fields from the raw JSON with error handling
        for msg in messages:
            email_data = {
                'id': msg.get('id', ''),
                'subject': msg.get('subject', ''),
                'clean_subject': self._clean_subject(msg.get('subject')),
                'body': msg.get('body', ''),
                'date': msg.get('date', '')
            }
            self.emails.append(email_data)

        # Sort by date to ensure merging happens in chronological order
        # Assuming date format allows standard string sort, or we parse it:
        # "Tue, 31 Dec 2024 15:01:20 +0000"
        self.emails.sort(key=lambda x: datetime.strptime(x['date'], "%a, %d %b %Y %H:%M:%S %z"))

    def _clean_subject(self, subject: str):
        """
        Removes 'Task:' prefix and extra whitespace.
        """
        if not subject:
            return ""
        # Remove 'Task:' (case insensitive) and trim whitespace
        return re.sub(r'^Task:\s*', '', subject, flags=re.IGNORECASE).strip()

    def get_expected_trello_state(self):
        """
        Processes emails to generate the Expected State of Trello cards.
        Handles Merging and Urgent Labeling.
        """
        cards_map = {}

        for email in self.emails:
            subject = email['clean_subject']
            body = email['body'].strip()

            # Logic: Check for 'Urgent' in body
            is_urgent = "urgent" in body.lower()

            if subject in cards_map:
                #MERGING LOGIC: Append body with newline only if it's different
                existing_card = cards_map[subject]

                # Check if this body is not already in the description to avoid duplicates
                if body and body not in existing_card['description']:
                    existing_card['description'] += f"\n{body}"

                # If any email in the chain was urgent, the card remains urgent
                if is_urgent:
                    existing_card['is_urgent'] = True
            else:
                # CREATE NEW CARD
                cards_map[subject] = {
                    'title': subject,
                    'description': body,
                    'is_urgent': is_urgent
                }

        return cards_map