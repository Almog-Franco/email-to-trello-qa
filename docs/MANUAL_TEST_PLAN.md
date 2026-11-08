# Manual test plan — email-to-Trello sync

The manual cases that shaped the automated suite.

## Core cases

1. **New card creation**: send a standard email to the integrated inbox and verify a new card appears with the
   label "New" in the "To Do" column.
2. **Subject parsing**: send an email with the subject "meeting" and verify the card title is "meeting".
3. **Prefix removal**: send an email with the subject "Task: book a flight" and verify the card title is
   "book a flight".
4. **Body mapping**: send an email with a multi-line body and verify the card description matches it exactly,
   whitespace and special characters included.
5. **"Urgent" label**: send an email with the word "Urgent" in the body and verify the card has the "Urgent" label.
6. **"Urgent" case sensitivity** (if the requirements define it): send emails with "urgent" and "URGENT".
7. **No partial-word match**: send an email with "surgent" in the body and verify the card is *not* labeled "Urgent".
8. **De-duplication**: send the exact same email (subject and body) twice and verify only one card is created.
9. **Appending**: send email A ("Hello", body "Part 1") then email B ("Hello", body "Part 2") and verify a single
   card whose description contains both bodies separated by a newline.
10. **Append order**: verify the description follows the arrival order of the emails.
11. **Done sync**: drag a card to "Done" and verify the matching email moves to Gmail's Trash.
12. **In-progress retention**: drag a card to "In progress" and verify the email stays in the inbox.

## Additional cases

1. **Reverse sync (negative)**: delete an email in Gmail manually and verify what happens to its card.
2. **"Task:" prefix position**: put characters before the "Task:" prefix and verify the resulting card.
3. **"Task:" case sensitivity**: use "TASK:" or "task:" and verify the outcome against the requirements.
4. **Same body, different subject**: send two emails with the same body but different subjects (whitespace
   included) and verify two cards are created.
