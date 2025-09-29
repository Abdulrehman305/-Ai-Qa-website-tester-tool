from ai_analysis import accessibility_ai_check


def test_accessibility_ai(browser, base_url):
    page = browser.new_page()
    try:
        page.goto(base_url)
        html = page.content()
        # Limit length to keep token usage reasonable
        snippet = html[:12000]
        result = accessibility_ai_check(snippet)
        # Print AI output to test report; don't fail automatically — human review is recommended
        print("\n--- Accessibility AI Report ---\n", result)
    finally:
        page.close()
