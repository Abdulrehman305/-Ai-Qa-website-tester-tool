import os
from playwright.sync_api import Page
from PIL import Image, ImageChops


def measure_performance(page: Page) -> dict:
    # Use the modern performance API where available
    try:
        perf = page.evaluate(
            "() => ({navigation: performance.getEntriesByType('navigation')[0] || {}, timing: performance.timing})"
        )
    except Exception:
        perf = page.evaluate("() => performance.timing")

    # Derive load times safely
    navigation_start = (
        perf.get("navigation", {}).get("startTime")
        or perf.get("navigationStart")
        or perf.get("timing", {}).get("navigationStart", 0)
    )
    load_event_end = (
        perf.get("navigation", {}).get("loadEventEnd")
        or perf.get("timing", {}).get("loadEventEnd", 0)
    )

    load_time = None
    try:
        load_time = int(load_event_end - navigation_start)
    except Exception:
        load_time = None

    return {
        "raw": perf,
        "load_time_ms": load_time,
    }


def take_screenshot(page: Page, name: str) -> str:
    os.makedirs("screenshots", exist_ok=True)
    path = os.path.join("screenshots", f"{name}.png")
    page.screenshot(path=path, full_page=True)
    return path


def compare_screenshots(baseline_path: str, current_path: str) -> dict:
    if not os.path.exists(baseline_path):
        return {"status": "no_baseline", "message": "Baseline does not exist"}

    a = Image.open(baseline_path).convert("RGBA")
    b = Image.open(current_path).convert("RGBA")

    # Resize check: if different sizes, return mismatch
    if a.size != b.size:
        return {"status": "size_mismatch", "baseline_size": a.size, "current_size": b.size}

    diff = ImageChops.difference(a, b)
    bbox = diff.getbbox()
    if bbox is None:
        return {"status": "match"}
    else:
        # Save diff for inspection
        diff_path = current_path.replace('.png', '.diff.png')
        diff.save(diff_path)
        return {"status": "diff", "diff_path": diff_path, "bbox": bbox}
