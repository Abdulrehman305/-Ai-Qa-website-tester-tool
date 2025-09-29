from playwright.sync_api import Page


def test_clicks_and_forms(browser, base_url):
    page = browser.new_page()
    try:
        page.goto(base_url, timeout=10000)

        # Example: try clicking an obvious CTA
        if page.locator("text=Get Started").count() > 0:
            page.click("text=Get Started")

        # Fill common email fields if found
        if page.locator("input[type=email]").count() > 0:
            page.fill("input[type=email]", "qa@example.com")

        # Try submit
        if page.locator("button[type=submit]").count() > 0:
            page.click("button[type=submit]")

        assert page.title() != "", "Page did not load a title"
    finally:
        page.close()
