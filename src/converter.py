"""HTML to Markdown conversion and content extraction."""

from typing import Optional

from bs4 import BeautifulSoup, Tag
from markdownify import markdownify as md


def extract_content(html: str, url: str) -> str:
    """
    Extract the main content from an HTML page and convert it to Markdown.
    
    Uses heuristics to find the main content area:
    1. <article> tag
    2. <main> tag
    3. Elements with class names like "content", "documentation", "doc", "markdown", "prose"
    4. <div> with role="main"
    5. Fallback to <body>
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted elements
    _remove_unwanted(soup)

    # Try to find the main content container
    content_element = _find_main_content(soup)

    if content_element is None:
        return ""

    # Convert to Markdown
    markdown_text = md(
        str(content_element),
        heading_style="ATX",        # Use # style headings
        bullets="-",                 # Use - for unordered lists
        strip=["img", "script", "style"],
        autolinks=True,
    )

    # Clean up the markdown
    markdown_text = _clean_markdown(markdown_text)

    return markdown_text


def _remove_unwanted(soup: BeautifulSoup) -> None:
    """Remove non-content elements from the soup."""
    # Remove script, style, nav, footer, header, aside
    for tag in soup.find_all(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # Remove elements with common non-content class names
    non_content_classes = [
        "sidebar", "side-bar", "side_bar",
        "navigation", "nav-bar", "navbar",
        "menu", "toc", "table-of-contents",
        "breadcrumb", "breadcrumbs",
        "footer", "header",
        "advertisement", "ads", "ad",
        "cookie", "cookies", "cookie-banner",
        "popup", "modal", "overlay",
        "search", "search-box",
        "comments", "comment",
        "social", "social-share",
        "newsletter", "subscribe",
    ]
    for class_name in non_content_classes:
        for element in soup.find_all(class_=lambda c: c and class_name in (c or "").lower().split()):
            element.decompose()


def _find_main_content(soup: BeautifulSoup) -> Optional[Tag]:
    """Find the main content element using heuristics."""
    # Priority 1: <article>
    article = soup.find("article")
    if article:
        return article

    # Priority 2: <main>
    main_tag = soup.find("main")
    if main_tag:
        return main_tag

    # Priority 3: role="main"
    role_main = soup.find(attrs={"role": "main"})
    if role_main:
        return role_main

    # Priority 4: Common content class names
    content_classes = [
        "content", "documentation", "doc-content", "doc_content",
        "markdown", "markdown-content", "markdown_content",
        "prose", "article-content", "article_content",
        "main-content", "main_content",
        "body-content", "body_content",
        "page-content", "page_content",
        "post-content", "post_content",
        "entry-content", "entry_content",
        "docs-content", "docs_content",
        "text-content", "text_content",
        "container", "wrapper",
        "theme-doc-content", "documentation-content",
    ]
    for class_name in content_classes:
        element = soup.find(class_=lambda c: c and class_name in (c or "").lower().split())
        if element:
            return element

    # Priority 5: <body>
    body = soup.find("body")
    if body:
        return body

    return None


def _clean_markdown(text: str) -> str:
    """Clean up the generated Markdown text."""
    # Remove excessive blank lines (more than 2 consecutive)
    import re
    text = re.sub(r"\n{4,}", "\n\n\n", text)

    # Remove lines that are just whitespace
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        if line.strip() or line == "":
            cleaned_lines.append(line)

    # Remove trailing whitespace on each line
    cleaned_lines = [line.rstrip() for line in cleaned_lines]

    text = "\n".join(cleaned_lines)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text