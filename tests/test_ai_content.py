from ai_analysis import content_quality_check


def test_ai_content_review(browser, base_url):
    page = browser.new_page()
    try:
        page.goto(base_url)
        text = page.inner_text("body")[:8000]
        result = content_quality_check(text)
        print("\n--- AI Content Review ---\n", result)
    finally:
        page.close()
