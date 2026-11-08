from .base_page import BasePage


class LoginPage(BasePage):

    def login(self, email, password):
        """
        Performs login to Trello.
        If using session persistence, this may be skipped if already authenticated.
        """
        # Check if already logged in (session persistence)
        self.page.goto("https://trello.com/login")

        # If already authenticated, redirect happens automatically
        if "/boards" in self.page.url or "trello.com/b/" in self.page.url:
            print("✅ Already authenticated (using saved session)")
            return

        # Email Step - Use data-testid selector (verified via Playwright MCP)
        self.page.fill("[data-testid='username']", email)
        self.page.click("[data-testid='login-submit-idf-testid']")

        # Password Step (Atlassian ID flow)
        self.page.wait_for_selector("[data-testid='password']")
        self.page.fill("[data-testid='password']", password)
        self.page.click("[data-testid='login-submit-idf-testid']")

        # Wait for redirection to complete
        # Note: MFA may be required on first login - use test_manual_login.py
        self.page.wait_for_url("**/boards", timeout=60000)
