"""
Helper test to perform initial login with MFA and save authenticated session.
Run this ONCE to handle MFA manually, then all other tests will reuse the session.

Usage:
    pytest tests/test_manual_login.py -v -s

After running this once successfully, run your actual tests:
    pytest tests/test_ui_scenarios.py -v
"""
import time
from config.settings import USER_EMAIL, USER_PASSWORD, BOARD_URL


def test_initial_login_with_mfa(page):
    """
    Perform initial login with MFA handling.
    You'll need to manually enter the MFA code when prompted.
    """

    print("\n" + "="*60)
    print("🔐 INITIAL LOGIN WITH MFA")
    print("="*60)

    # Navigate and fill credentials
    page.goto("https://trello.com/login")
    print("✅ Navigated to login page")

    # Email step
    page.fill("[data-testid='username']", USER_EMAIL)
    page.click("[data-testid='login-submit-idf-testid']")
    print(f"✅ Entered email: {USER_EMAIL}")

    # Password step
    page.wait_for_selector("[data-testid='password']", timeout=10000)
    page.fill("[data-testid='password']", USER_PASSWORD)
    page.click("[data-testid='login-submit-idf-testid']")
    print("✅ Entered password")

    # Check if MFA is required
    print("\n⏳ Checking for MFA challenge...")
    time.sleep(2)  # Wait a moment for redirect

    if "login/mfa" in page.url:
        print("\n" + "="*60)
        print("🔑 MFA VERIFICATION REQUIRED")
        print("="*60)
        print("📧 Check your email for the verification code")
        print("⌨️  Enter the 6-digit code in the browser window")
        print("⏰ Waiting up to 3 minutes for you to enter the code...")
        print("="*60 + "\n")

        # Wait for user to manually enter MFA code (3 minutes timeout)
        try:
            page.wait_for_url("**/boards**", timeout=180000)  # 3 minutes
            print("\n✅ MFA verification successful!")
        except Exception as e:
            print(f"\n❌ MFA verification failed or timed out: {e}")
            raise
    else:
        print("✅ No MFA required (or already completed)")
        page.wait_for_url("**/boards**", timeout=180000)

    # Verify we're logged in by navigating to the board
    page.goto(BOARD_URL)
    page.wait_for_selector(".board-header", timeout=10000)

    print("\n" + "="*60)
    print("✅ LOGIN SUCCESSFUL - Session will be saved for future tests")
    print("="*60)
    print("\nℹ️  You won't need to handle MFA again until the session expires")
    print("ℹ️  Just run: pytest tests/test_ui_scenarios.py -v\n")

    # Session will be automatically saved by conftest.py fixture
    assert True

