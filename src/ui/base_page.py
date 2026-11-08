from playwright.sync_api import Page

class BasePage:
    """Base POM class for common methods."""
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url):
        self.page.goto(url)