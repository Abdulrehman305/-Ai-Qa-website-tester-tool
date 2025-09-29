import os
import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()


def pytest_addoption(parser):
    parser.addoption("--headed", action="store_true", help="Run browser in headed mode")
    parser.addoption(
        "--url",
        action="store",
        default=os.getenv("DEFAULT_URL", "https://example.com"),
        help="Base URL to test",
    )


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance, pytestconfig):
    headed = pytestconfig.getoption("headed")
    # slow_mo helpful in headed mode for demos
    slow_mo = 200 if headed else 0
    browser = playwright_instance.chromium.launch(headless=not headed, slow_mo=slow_mo)
    yield browser
    browser.close()


@pytest.fixture
def base_url(pytestconfig):
    return pytestconfig.getoption("--url")
