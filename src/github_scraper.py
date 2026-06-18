"""GitHub profile scraper for fetching public repositories and README content."""

import base64
import json
import logging
import os
import re
import time
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

# GitHub API base URL
GITHUB_API = "https://api.github.com"

# Default headers for GitHub API requests
DEFAULT_HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "webdocs2md/1.0.0",
}


def _get_headers() -> Dict[str, str]:
    """Get request headers, optionally including a GitHub token for higher rate limits."""
    headers = dict(DEFAULT_HEADERS)
    token = os.getenv("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def extract_username(url: str) -> str:
    """Extract the GitHub username from a profile URL.

    Handles formats like:
    - https://github.com/khafidhteer
    - https://github.com/khafidhteer/
    - github.com/khafidhteer
    """
    # Remove trailing slash
    url = url.rstrip("/")

    # Match the username from the URL path
    match = re.search(r"(?:github\.com/)([a-zA-Z0-9_-]+)", url)
    if not match:
        raise ValueError(f"Could not extract GitHub username from URL: {url}")

    return match.group(1)


def get_public_repos(
    username: str,
    max_repos: int = 100,
    delay: float = 0.1,
) -> List[Dict]:
    """Fetch all public repositories for a GitHub user.

    Args:
        username: GitHub username.
        max_repos: Maximum repositories to fetch.
        delay: Delay between paginated requests.

    Returns:
        List of repository metadata dicts with keys: name, description,
        language, html_url, topics, stars, forks.
    """
    repos: List[Dict] = []
    page = 1
    per_page = min(max_repos, 100)

    while len(repos) < max_repos:
        url = f"{GITHUB_API}/users/{username}/repos"
        params = {
            "type": "public",
            "sort": "full_name",
            "per_page": per_page,
            "page": page,
        }

        try:
            response = requests.get(
                url,
                headers=_get_headers(),
                params=params,
                timeout=30,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch repos page {page}: {e}")
            break

        data = response.json()
        if not data:
            break

        for repo in data:
            if len(repos) >= max_repos:
                break

            repos.append({
                "name": repo.get("name", ""),
                "description": repo.get("description") or "",
                "language": repo.get("language") or "Unknown",
                "html_url": repo.get("html_url", ""),
                "topics": repo.get("topics", []),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "is_archived": repo.get("archived", False),
                "is_fork": repo.get("fork", False),
            })

        # Check if there are more pages
        if len(data) < per_page:
            break

        page += 1

        if delay > 0:
            time.sleep(delay)

    return repos


def get_repo_readme(username: str, repo: str) -> str:
    """Fetch the README content for a repository.

    Tries multiple known README filenames and returns the first found.

    Args:
        username: GitHub username.
        repo: Repository name.

    Returns:
        README content as Markdown string, or empty string if not found.
    """
    # Try standard README filenames
    readme_names = ["README.md", "readme.md", "README", "Readme.md"]

    for readme_name in readme_names:
        url = f"{GITHUB_API}/repos/{username}/{repo}/contents/{readme_name}"

        try:
            response = requests.get(
                url,
                headers=_get_headers(),
                timeout=30,
            )

            if response.status_code == 404:
                continue

            response.raise_for_status()
            data = response.json()

            # GitHub returns content as base64-encoded
            if isinstance(data, dict) and "content" in data:
                content = data["content"]
                # Remove newlines from base64 string
                content = content.replace("\n", "").replace("\r", "")
                try:
                    decoded = base64.b64decode(content).decode("utf-8")
                    return decoded
                except (base64.binascii.Error, UnicodeDecodeError) as e:
                    logger.warning(f"Failed to decode README for {repo}: {e}")
                    continue

        except requests.RequestException as e:
            logger.warning(f"Failed to fetch README for {repo}/{readme_name}: {e}")
            continue

    # Try the repository's default branch readme endpoint as fallback
    try:
        url = f"{GITHUB_API}/repos/{username}/{repo}/readme"
        response = requests.get(url, headers=_get_headers(), timeout=30)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "content" in data:
                content = data["content"].replace("\n", "").replace("\r", "")
                try:
                    return base64.b64decode(content).decode("utf-8")
                except (base64.binascii.Error, UnicodeDecodeError):
                    pass
    except requests.RequestException:
        pass

    return ""


def has_no_readme(repo_name: str) -> str:
    """Return a placeholder message for repos without a README."""
    return f"*No README found for {repo_name}.*"


def check_rate_limit() -> Dict:
    """Check the current GitHub API rate limit status.

    Returns dict with 'limit', 'remaining', 'reset' keys.
    """
    try:
        response = requests.get(
            f"{GITHUB_API}/rate_limit",
            headers=_get_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            resources = data.get("resources", {})
            core = resources.get("core", {})
            return {
                "limit": core.get("limit", 60),
                "remaining": core.get("remaining", 0),
                "reset": core.get("reset", 0),
            }
    except requests.RequestException:
        pass

    return {"limit": 60, "remaining": 0, "reset": 0}