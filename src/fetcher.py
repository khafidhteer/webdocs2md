"""Page fetching with requests and optional Playwright fallback."""

import time
import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Default headers to mimic a browser
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def fetch_page(url: str, use_playwright: bool = True, delay: float = 0.5) -> str:
    """
    Fetch HTML content from a URL.
    Uses requests first. If the response has no meaningful text content,
    falls back to Playwright (headless browser) if enabled.

    Returns the HTML string, or raises an exception on failure.
    """
    if delay > 0:
        time.sleep(delay)

    # Step 1: Try with requests
    html = _fetch_with_requests(url)
    if html and _has_meaningful_content(html):
        return html

    # Step 2: Fall back to Playwright if enabled
    if use_playwright:
        logger.info(f"Falling back to Playwright for {url}")
        html = _fetch_with_playwright(url)
        if html and _has_meaningful_content(html):
            return html

    # Return whatever we got (even if minimal)
    return html or ""


def _fetch_with_requests(url: str) -> str:
    """Fetch a page using the requests library."""
    try:
        response = requests.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=30,
            allow_redirects=True,
        )
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.warning(f"requests failed for {url}: {e}")
        return ""


def _fetch_with_playwright(url: str) -> str:
    """Fetch a page using Playwright headless browser."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.warning("Playwright not installed. Skipping Playwright fallback.")
        return ""

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=DEFAULT_HEADERS["User-Agent"],
                viewport={"width": 1280, "height": 720},
            )
            page = context.new_page()
            page.goto(url, wait_until="networkidle", timeout=30000)
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        logger.warning(f"Playwright failed for {url}: {e}")
        return ""


def _has_meaningful_content(html: str) -> bool:
    """Check if the HTML contains meaningful text content (not just navigation/chrome)."""
    if not html:
        return False
    soup = BeautifulSoup(html, "html.parser")
    # Remove script and style elements
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    # Require at least 200 characters of meaningful text
    return len(text) > 200