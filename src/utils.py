"""Utility functions for URL normalization and domain handling."""

from urllib.parse import urlparse, urlunparse, urljoin


def normalize_url(url: str) -> str:
    """Normalize a URL by removing fragments and ensuring consistent trailing slash."""
    parsed = urlparse(url)
    # Remove fragment
    parsed = parsed._replace(fragment="")
    # Remove query string for dedup purposes (optional, but helps)
    parsed = parsed._replace(query="")
    return urlunparse(parsed)


def is_same_domain(url: str, base_url: str) -> bool:
    """Check if url belongs to the same domain as base_url."""
    url_domain = urlparse(url).netloc
    base_domain = urlparse(base_url).netloc
    return url_domain == base_domain or url_domain.endswith("." + base_domain)


def is_internal_link(href: str, base_url: str) -> bool:
    """
    Determine if an href is an internal link belonging to the same documentation site.
    Returns True if it should be crawled.
    """
    if not href:
        return False

    # Skip anchors, javascript, mailto, tel
    if href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:") or href.startswith("tel:"):
        return False

    # Skip non-HTTP protocols
    if href.startswith("ftp:") or href.startswith("file:"):
        return False

    # Skip common non-documentation file types
    skip_extensions = (".pdf", ".zip", ".tar", ".gz", ".png", ".jpg", ".jpeg",
                       ".gif", ".svg", ".ico", ".css", ".js", ".json", ".xml",
                       ".mp4", ".mp3", ".avi", ".mov")
    if href.lower().endswith(skip_extensions):
        return False

    # Resolve relative URLs
    full_url = urljoin(base_url, href)
    full_parsed = urlparse(full_url)

    # Must have a scheme and netloc
    if not full_parsed.scheme or not full_parsed.netloc:
        return False

    # Must be http or https
    if full_parsed.scheme not in ("http", "https"):
        return False

    # Must be the same domain
    if not is_same_domain(full_url, base_url):
        return False

    return True


def resolve_url(href: str, base_url: str) -> str:
    """Resolve a potentially relative href to an absolute URL."""
    return normalize_url(urljoin(base_url, href))


def extract_domain(url: str) -> str:
    """Extract the domain name from a URL for use in filenames."""
    parsed = urlparse(url)
    domain = parsed.netloc
    # Remove www. prefix
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def url_to_filename(url: str) -> str:
    """Convert a URL path to a safe filename segment."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        path = "index"
    # Replace non-alphanumeric characters
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in path)
    return safe