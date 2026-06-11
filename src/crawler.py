"""BFS web crawler for discovering documentation pages."""

from collections import deque
from typing import Set, List, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from tqdm import tqdm

from .utils import is_internal_link, resolve_url, normalize_url
from .fetcher import fetch_page


def crawl_site(
    start_url: str,
    max_pages: int = 200,
    delay: float = 0.5,
    use_playwright: bool = True,
) -> List[str]:
    """
    BFS crawl a documentation site starting from start_url.
    Returns a sorted list of discovered page URLs.
    """
    start_url = normalize_url(start_url)
    base_domain = urlparse(start_url).netloc

    visited: Set[str] = set()
    queue: deque = deque([start_url])
    discovered: List[str] = []

    with tqdm(desc="Crawling pages", unit="page") as pbar:
        while queue and len(visited) < max_pages:
            url = queue.popleft()
            if url in visited:
                continue

            visited.add(url)

            try:
                html = fetch_page(url, use_playwright=use_playwright, delay=delay)
            except Exception as e:
                tqdm.write(f"  [!] Failed to fetch {url}: {e}")
                continue

            if not html:
                continue

            discovered.append(url)
            pbar.update(1)

            # Parse HTML and find links
            soup = BeautifulSoup(html, "html.parser")
            for anchor in soup.find_all("a", href=True):
                href = anchor["href"]
                if not is_internal_link(href, url):
                    continue

                resolved = resolve_url(href, url)

                # Skip if already visited or queued
                if resolved in visited or resolved in queue:
                    continue

                # Only add pages under the same path prefix as start_url
                # (avoids crawling the entire domain, e.g., blog, docs vs main site)
                resolved_domain = urlparse(resolved).netloc
                if resolved_domain != base_domain:
                    continue

                queue.append(resolved)

    # Sort URLs for consistent ordering
    discovered.sort()
    return discovered