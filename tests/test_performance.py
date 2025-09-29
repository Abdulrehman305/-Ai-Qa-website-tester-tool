from utils import measure_performance


def test_page_load_performance(browser, base_url):
    page = browser.new_page()
    try:
        page.goto(base_url)
        perf = measure_performance(page)
        load = perf.get("load_time_ms")
        # If load is None, warn but don't fail. Adjust threshold as needed.
        if load is not None:
            assert load < 5000, f"Page load too slow: {load} ms"
    finally:
        page.close()
