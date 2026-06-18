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


# ─── GitHub Profile Summary ────────────────────────────────────────────────


def compile_github_summary(
    username: str,
    repos: list,
    repo_readmes: dict,
) -> str:
    """Compile a GitHub profile summary document.

    Args:
        username: GitHub username.
        repos: List of repository metadata dicts.
        repo_readmes: Dict mapping repo name -> README markdown content.

    Returns:
        A complete Markdown document string.
    """
    if not repos:
        return f"# {username}\n\nNo public repositories found."

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    parts = []

    # 1. Header
    parts.append(f"# {username} — GitHub Profile Summary")
    parts.append("")
    parts.append(f"> **Profile**: https://github.com/{username}")
    parts.append(f"> **Generated**: {now}")
    parts.append(f"> **Public Repositories**: {len(repos)}")
    parts.append("---")
    parts.append("")

    # 2. Table of Contents
    parts.append("## Table of Contents")
    parts.append("")
    for i, repo in enumerate(repos):
        name = repo["name"]
        anchor = _github_repo_anchor(name, i)
        parts.append(f"- [{name}](#{anchor})")
    parts.append("- [Summary](#summary)")
    parts.append("")

    # 3. Repository sections
    for i, repo in enumerate(repos):
        name = repo["name"]
        anchor = _github_repo_anchor(name, i)
        readme_content = repo_readmes.get(name, "")

        parts.append("---")
        parts.append("")
        parts.append(f"## {name}")
        parts.append("")
        parts.append(f"*Repository: [{name}]({repo['html_url']})*")
        parts.append("")

        # Metadata table
        topics_str = ", ".join(repo["topics"]) if repo["topics"] else "*None*"
        parts.append("| Attribute | Value |")
        parts.append("|-----------|-------|")
        parts.append(f"| **Description** | {repo['description'] or '*No description*'} |")
        parts.append(f"| **Language** | {repo['language']} |")
        parts.append(f"| **Stars** | {repo['stars']} |")
        parts.append(f"| **Forks** | {repo['forks']} |")
        parts.append(f"| **Topics** | {topics_str} |")
        parts.append(f"| **Archived** | {'Yes' if repo['is_archived'] else 'No'} |")
        parts.append(f"| **Fork** | {'Yes' if repo['is_fork'] else 'No'} |")
        parts.append("")

        # README content
        if readme_content:
            parts.append(readme_content)
        else:
            parts.append(f"*No README found for {name}.*")
        parts.append("")

    # 4. Aggregated Summary
    parts.append("---")
    parts.append("")
    parts.append("## Summary")
    parts.append("")

    # Group by language
    languages: dict = {}
    for repo in repos:
        lang = repo["language"]
        if lang and lang != "Unknown":
            if lang not in languages:
                languages[lang] = 0
            languages[lang] += 1

    if languages:
        parts.append("### Languages Used")
        parts.append("")
        # Sort by count descending
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        for lang, count in sorted_langs:
            bar = "█" * count
            parts.append(f"- **{lang}**: {count} repo{'s' if count > 1 else ''} {bar}")
        parts.append("")

    # Collect all topics
    all_topics: list = []
    for repo in repos:
        all_topics.extend(repo.get("topics", []))
    if all_topics:
        # Count topic frequency
        from collections import Counter
        topic_counts = Counter(all_topics)
        parts.append("### Common Topics")
        parts.append("")
        for topic, count in topic_counts.most_common(10):
            parts.append(f"- **{topic}** ({count} repo{'s' if count > 1 else ''})")
        parts.append("")

    # Archive/fork stats
    archived_count = sum(1 for r in repos if r["is_archived"])
    fork_count = sum(1 for r in repos if r["is_fork"])
    parts.append("### Repository Statistics")
    parts.append("")
    parts.append(f"- **Total public repos**: {len(repos)}")
    parts.append(f"- **Archived**: {archived_count}")
    parts.append(f"- **Forks**: {fork_count}")
    parts.append(f"- **Active (non-archived, non-fork)**: {len(repos) - archived_count - fork_count}")
    parts.append("")

    # Note about future AI processing
    parts.append("---")
    parts.append("")
    parts.append("*This document contains all README content for LLM ingestion.*")
    parts.append("")

    document = "\n".join(parts)
    document = re.sub(r"\n{4,}", "\n\n\n", document)
    document = document.strip() + "\n"

    return document


def _github_repo_anchor(name: str, index: int) -> str:
    """Generate a unique anchor ID for a GitHub repository."""
    anchor = name.lower()
    anchor = re.sub(r"[^a-z0-9\s-]", "", anchor)
    anchor = anchor.replace(" ", "-")
    anchor = re.sub(r"-+", "-", anchor)
    anchor = anchor.strip("-")
    return f"{anchor}-{index}"
