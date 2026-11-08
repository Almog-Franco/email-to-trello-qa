# Email-to-Trello Sync — QA Automation Suite

A test automation framework for validating Gmail-to-Trello synchronization using API validation and UI testing with Playwright.

## 📋 Overview

This project automates testing of an email-to-Trello integration, where incoming emails become Trello cards. It validates:
- **Email synchronization**: Cards are created from emails with correct merging logic
- **Urgent labeling**: Cards are properly labeled as "Urgent" based on email content
- **UI consistency**: Trello board UI displays correct card information

## 🚀 Quick Setup & Run

### Prerequisites
- **Python 3.8+** installed
- **pip** package manager
- Internet connection (for Trello API and Playwright)

### 1. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers (required for UI tests)
playwright install
```

**Dependencies installed:**
- `pytest` - Test framework
- `playwright` - Browser automation
- `requests` - HTTP client for Trello API
- `python-dotenv` - Environment variable support
- `backoff` - API retry logic

### 2. Configure Credentials
```bash
cp .env.example .env   # fill in Trello API key/token, board id and the test account's login
```

### 3. Initial Login (One-Time MFA Setup)
**Required once** to save authenticated session:

```bash
pytest tests/test_manual_login.py -v -s
```

**What happens:**
1. Browser opens with credentials auto-filled
2. MFA prompt appears → **Check email for 6-digit code**
3. Enter code in browser (you have 3 minutes)
4. Session saved to `resources/auth_state.json`
5. ✅ **Done!** No MFA needed for weeks/months

### 4. Run Tests
All tests run automatically using saved session:

```bash
# Run API sync validation tests
pytest tests/test_sync_login.py -v

# Run UI automation tests
pytest tests/test_ui_scenarios.py -v

# Run all tests (excluding manual login)
pytest tests/ -v --ignore=tests/test_manual_login.py
```

---

## ⚙️ Configuration & Environment Variables

### Configuration File: `config/settings.py`

All settings are centralized in this file. Credentials are **never committed**: they are read from environment
variables, or from a local `.env` file (gitignored):

```bash
cp .env.example .env   # then fill in your Trello API key/token, board id and test-account login
```

In CI the same variables come from GitHub Actions secrets.

**Example:**
```bash
# Run tests in headless mode (no browser window)
HEADLESS=true pytest tests/test_ui_scenarios.py -v
```

### Authentication Session

- **File**: `resources/auth_state.json` (auto-generated)
- **Purpose**: Stores browser cookies and session tokens to bypass MFA
- **Lifespan**: Several weeks to months
- **Security**: Already in `.gitignore` - won't be committed

---

## 📁 Project Structure

```
email-to-trello-qa/
├── config/
│   ├── __init__.py
│   └── settings.py              # Configuration (credentials come from env vars)
├── data/
│   └── mock_gmail_data.json     # Mock Gmail messages for sync tests
├── resources/
│   └── auth_state.json          # Saved session (auto-generated, gitignored)
├── src/
│   ├── api/
│   │   ├── gmail_client.py      # Gmail mock data parser
│   │   └── trello_client.py     # Trello API client with retry logic
│   └── ui/
│       ├── base_page.py         # Base page object class
│       ├── login_page.py        # Login page automation
│       └── board_page.py        # Board page automation
├── tests/
│   ├── conftest.py              # Pytest fixtures & session management
│   ├── test_manual_login.py     # Initial MFA login helper
│   ├── test_sync_login.py       # API sync validation tests
│   └── test_ui_scenarios.py     # UI automation tests
├── utils/
│   ├── steps.py                 # Test step context managers
│   └── utilities.py             # Helper functions
├── docs/
│   └── MANUAL_TEST_PLAN.md      # Manual test cases the suite is based on
├── .env.example                 # Template for local credentials
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## 📦 Dependencies Explained

### Core Testing Framework
- **pytest** (latest): Test framework and runner
  - Used for: Test execution, fixtures, parametrization

### Browser Automation
- **playwright** (latest): Cross-browser automation library
  - Used for: UI testing, browser control, session management
  - Requires: `playwright install` to download browser binaries

### API & Networking
- **requests** (latest): HTTP library for API calls
  - Used for: Trello API interactions, card validation

### Utilities
- **python-dotenv** (latest): Environment variable management
  - Used for: Loading credentials from a local .env file
  
- **backoff** (latest): Retry library with exponential backoff
  - Used for: Resilient API calls with automatic retries

Install with: `pip install -r requirements.txt`

---

## 🔑 MFA Handling - Session Persistence

### How Often Do I Need to Handle MFA?

**Answer: Once every few weeks/months, possibly longer.**

The saved session (`auth_state.json`) typically lasts:
- **Normal case:** Several weeks to months
- **Trello's session policy:** Very long-lived (60-90 days or more)
- **Only re-login when:** Session naturally expires or you delete the file

### How It Works

```
First Time:
Login → Enter MFA code → Session Saved → Tests Run
         ↓
    auth_state.json created (lasts weeks/months)

All Future Runs:
Load Session → Already Logged In → Tests Run
(No MFA needed!)

When Session Expires (weeks/months later):
Delete auth_state.json → Re-run manual login → Good for another few weeks/months
```

### Why This Approach?

✅ **Handle MFA only once per month (or less)**  
✅ **Fast test execution** - No login delays  
✅ **Industry standard** - Used by professional QA teams  
✅ **Simple** - Just 2 commands  
✅ **Secure** - Session file is gitignored  

---

## 📊 How It Works

### Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Mock Gmail     │────▶│  Gmail Client    │────▶│  Expected State │
│  JSON Data      │     │  (Parser)        │     │  (cards_map)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                           │
                                                           ▼
                        ┌──────────────────┐     ┌─────────────────┐
                        │  Trello API      │────▶│  Actual State   │
                        │  Client          │     │  (Trello Board) │
                        └──────────────────┘     └─────────────────┘
                                                           │
                                                           ▼
                        ┌──────────────────┐     ┌─────────────────┐
                        │  Playwright      │────▶│  UI Validation  │
                        │  Browser         │     │  (Visual Check) │
                        └──────────────────┘     └─────────────────┘
```

## 🎯 Test Suites Explained

### API Sync Validation (`test_sync_login.py`)

**Purpose**: Validate Gmail-to-Trello synchronization logic

**Tests:**
- `test_card_description_sync`: Verifies each card exists with correct merged description
- `test_card_urgent_label_sync`: Confirms urgent cards have "Urgent" label
- `test_no_extra_cards_in_trello`: Ensures no orphaned cards exist

**Key Features:**
- Uses mock Gmail data (`data/mock_gmail_data.json`)
- Validates via Trello REST API
- Parametrized tests (one test per card)
- Tests merging logic: Multiple emails → Single card

**Run:**
```bash
pytest tests/test_sync_login.py -v
```

**Example Output:**
```
test_sync_login.py::test_card_description_sync[Check the UI] PASSED
test_sync_login.py::test_card_urgent_label_sync[Check the UI] PASSED
test_sync_login.py::test_no_extra_cards_in_trello PASSED
```

---

### UI Automation (`test_ui_scenarios.py`)

**Purpose**: Validate Trello board UI displays correct information

**Scenarios:**

1. **test_scenario_1_urgent_cards**
   - Finds all cards with "Urgent" label
   - Opens each card modal
   - Validates label presence in UI
   - Logs card details (title, status, labels, description)

2. **test_scenario_2_specific_card**
   - Validates specific card: "summarize the meeting"
   - Checks title, merged description, labels, status
   - Confirms merging: "For all of us\nPlease do so"

---

## 🚀 Running Tests - Complete Guide

### Run All Tests
```bash
# Recommended: Run all tests except manual login
pytest tests/ -v --ignore=tests/test_manual_login.py

# Run with detailed output
pytest tests/ -v -s --ignore=tests/test_manual_login.py
```

### Run Specific Test Suites
```bash
# Only API sync validation tests (fast, ~5-10 seconds)
pytest tests/test_sync_login.py -v

# Only UI automation tests (~30-60 seconds)
pytest tests/test_ui_scenarios.py -v
```

### Run Individual Tests
```bash
# Run specific test function
pytest tests/test_ui_scenarios.py::test_scenario_1_urgent_cards -v

# Run specific parametrized test
pytest tests/test_sync_login.py::test_card_description_sync -v
```

### Headless Mode (No Browser Window)
```bash
# Set HEADLESS environment variable
HEADLESS=true pytest tests/test_ui_scenarios.py -v
```
---

## 📝 Summary

This automation framework provides:
- ✅ **Fast setup**: 3 commands to get started
- ✅ **Minimal maintenance**: MFA once per month (or less)
- ✅ **Comprehensive testing**: API + UI validation
- ✅ **Production-ready**: Error handling, retries, logging
- ✅ **Well-structured**: Page Object Model, fixtures, utilities

```bash
pytest tests/test_manual_login.py -v -s  # First time only
pytest tests/ -v --ignore=tests/test_manual_login.py  # All future runs
```
