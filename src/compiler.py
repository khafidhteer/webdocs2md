"""Compiler that assembles all page content into a single structured Markdown document."""

import re
from datetime import datetime
from typing import Dict, List, Tuple
from urllib.parse import urlparse


def compile_document(
    pages: Dict[str, str],
    source_url: str,
    title: str = None,
) -> str:
    """
    Compile all page content into a single structured Markdown document.
    
    Args:
        pages: Dictionary mapping page URL -> Markdown content
        source_url: The original starting URL
        title: Optional document title (defaults to domain name)
    
    Returns:
        A complete Markdown document string
    """
    if not pages:
        return "# No content found\n\nNo pages were discovered or fetched."

    domain = urlparse(source_url).netloc
    if title is None:
        title = f"{domain} Documentation"

    # Build the document parts
    parts = []
    
    # 1. Document header
    parts.append(_build_header(title, source_url))
    parts.append("")

    # 2. Table of Contents
    toc_entries = _build_toc(pages)
    if toc_entries:
        parts.append("## Table of Contents")
        parts.append("")
        parts.extend(toc_entries)
        parts.append("")

    # 3. Page content sections
    for i, (url, content) in enumerate(pages.items()):
        if not content.strip():
            continue
        
        section = _build_section(url, content, i)
        parts.append(section)
        parts.append("")

    # Join everything together
    document = "\n".join(parts)

    # Final cleanup
    document = re.sub(r"\n{4,}", "\n\n\n", document)
    document = document.strip() + "\n"

    return document


def _build_header(title: str, source_url: str) -> str:
    """Build the document header with metadata."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return (
        f"# {title}\n\n"
        f"> **Source**: [{source_url}]({source_url})\n"
        f"> **Generated**: {now}\n"
        f"> **Pages**: {{pages_placeholder}}\n"
        "---"
    )


def _build_toc(pages: Dict[str, str]) -> List[str]:
    """Build a table of contents from page URLs."""
    entries = []
    for i, url in enumerate(pages.keys()):
        # Extract a readable title from URL
        title = _url_to_title(url)
        anchor = _title_to_anchor(title, i)
        indent = "  " if _is_subpage(url) else ""
        entries.append(f"{indent}- [{title}](#{anchor})")
    return entries


def _build_section(url: str, content: str, index: int) -> str:
    """Build a single page section with heading and content."""
    title = _url_to_title(url)
    anchor = _title_to_anchor(title, index)
    
    section_parts = [
        f"---",
        f"",
        f"## {title}",
        f"",
        f"*Source: [{url}]({url})*",
        f"",
        content,
    ]
    return "\n".join(section_parts)


def _url_to_title(url: str) -> str:
    """Convert a URL path to a human-readable title."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    
    if not path:
        return "Home / Overview"
    
    # Split path segments
    segments = path.split("/")
    
    # Take the last meaningful segment
    last = segments[-1] if segments else ""
    
    # Clean up the segment
    title = last.replace("-", " ").replace("_", " ")
    title = re.sub(r"\.(html?|php|aspx?)$", "", title, flags=re.IGNORECASE)
    title = title.strip()
    
    if not title:
        # Use parent segment
        if len(segments) > 1:
            title = segments[-2].replace("-", " ").replace("_", " ")
        else:
            title = "Overview"
    
    # Capitalize words
    title = title.title()
    
    return title


def _title_to_anchor(title: str, index: int) -> str:
    """Convert a title to an anchor ID."""
    anchor = title.lower()
    anchor = re.sub(r"[^a-z0-9\s-]", "", anchor)
    anchor = anchor.replace(" ", "-")
    anchor = re.sub(r"-+", "-", anchor)
    anchor = anchor.strip("-")
    # Add index to ensure uniqueness
    return f"{anchor}-{index}"


def _is_subpage(url: str) -> bool:
    """Check if a URL represents a subpage (nested path)."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    return "/" in path