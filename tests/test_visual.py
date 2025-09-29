import os
from utils import take_screenshot, compare_screenshots


def test_visual_regression(browser, base_url):
    page = browser.new_page()
    try:
        page.goto(base_url)
        current = take_screenshot(page, "current")
        baseline = os.getenv("BASELINE_SCREENSHOT", "screenshots/baseline.png")

        result = compare_screenshots(baseline, current)
        assert result["status"] in ("match", "no_baseline"), f"Visual regression detected: {result}"
    finally:
        page.close()
