import requests
from urllib.parse import urlparse


def is_internal(url, base):
    if not url:
        return False
    try:
        u = urlparse(url)
        b = urlparse(base)
        return (not u.netloc) or (u.netloc == b.netloc)
    except Exception:
        return False


def test_broken_internal_links(browser, base_url):
    page = browser.new_page()
    try:
        page.goto(base_url)
        hrefs = page.eval_on_selector_all('a', 'els => els.map(e => e.href).filter(Boolean)')
        bad = []
        for h in set(hrefs):
            if not is_internal(h, base_url):
                continue
            try:
                r = requests.head(h, allow_redirects=True, timeout=8)
                if r.status_code >= 400:
                    bad.append((h, r.status_code))
            except Exception as e:
                bad.append((h, str(e)))
        assert not bad, f"Broken internal links: {bad}"
    finally:
        page.close()
