"""CLI entry point for webdocs2md."""

import os
import sys
import logging
from typing import Optional

import click
from dotenv import load_dotenv

from . import __version__
from .crawler import crawl_site
from .fetcher import fetch_page
from .converter import extract_content
from .compiler import compile_document, compile_github_summary
from .utils import extract_domain
from .github_scraper import extract_username, get_public_repos, get_repo_readme, check_rate_limit


# Load .env file if present
load_dotenv()


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


@click.group()
@click.version_option(version=__version__, prog_name="webdocs2md")
def cli():
    """Crawl documentation websites and compile them into structured Markdown."""
    pass


@cli.command()
@click.argument("url", type=str, required=True)
@click.option(
    "--output", "-o",
    type=str,
    default=None,
    help="Output filename (without .md extension). Defaults to <domain>-docs.md",
)
@click.option(
    "--max-pages", "-m",
    type=int,
    default=None,
    help=f"Maximum pages to crawl (default: {os.getenv('DEFAULT_MAX_PAGES', '200')})",
)
@click.option(
    "--concurrency", "-c",
    type=int,
    default=None,
    help=f"Number of concurrent fetchers (default: {os.getenv('DEFAULT_CONCURRENCY', '3')})",
)
@click.option(
    "--delay", "-d",
    type=float,
    default=None,
    help=f"Delay between requests in seconds (default: {os.getenv('DEFAULT_DELAY', '0.5')})",
)
@click.option(
    "--no-playwright",
    is_flag=True,
    default=False,
    help="Disable Playwright fallback for JavaScript-rendered content",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    default=False,
    help="Enable verbose/debug logging",
)
@click.option(
    "--title",
    type=str,
    default=None,
    help="Custom title for the generated document",
)
def crawl(
    url: str,
    output: Optional[str],
    max_pages: Optional[int],
    concurrency: Optional[int],
    delay: Optional[float],
    no_playwright: bool,
    verbose: bool,
    title: Optional[str],
):
    """
    Crawl a documentation website and compile it into a structured Markdown file.

    URL is the starting documentation URL (e.g., https://docs.cline.bot/cline-overview)
    """
    setup_logging(verbose)

    # Apply defaults from .env or hardcoded defaults
    max_pages = max_pages or int(os.getenv("DEFAULT_MAX_PAGES", "200"))
    delay = delay or float(os.getenv("DEFAULT_DELAY", "0.5"))
    use_playwright = not no_playwright

    # Determine output path
    domain = extract_domain(url)
    if output is None:
        output = f"{domain}-docs"
    output_dir = os.getenv("OUTPUT_DIR", "output")
    output_path = os.path.join(output_dir, f"{output}.md")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    click.echo(f"webdocs2md v{__version__} — Documentation Crawl")
    click.echo(f"  Source URL: {url}")
    click.echo(f"  Max pages:  {max_pages}")
    click.echo(f"  Delay:      {delay}s")
    click.echo(f"  Playwright: {'enabled' if use_playwright else 'disabled'}")
    click.echo(f"  Output:     {output_path}")
    click.echo()

    # Step 1: Crawl
    click.echo("[1/3] Crawling site to discover pages...")
    try:
        urls = crawl_site(
            start_url=url,
            max_pages=max_pages,
            delay=delay,
            use_playwright=use_playwright,
        )
    except Exception as e:
        click.echo(f"  [!] Crawl failed: {e}", err=True)
        sys.exit(1)

    if not urls:
        click.echo("  [!] No pages discovered. Exiting.")
        sys.exit(1)

    click.echo(f"  Discovered {len(urls)} pages.")
    click.echo()

    # Step 2: Fetch & Convert
    click.echo("[2/3] Fetching and converting pages to Markdown...")
    pages = {}
    for i, page_url in enumerate(urls, 1):
        click.echo(f"  [{i}/{len(urls)}] {page_url}", nl=False)

        try:
            html = fetch_page(page_url, use_playwright=use_playwright, delay=delay)
        except Exception as e:
            click.echo(f"  [!] Fetch failed: {e}")
            continue

        if not html:
            click.echo("  [skipped - empty response]")
            continue

        try:
            markdown_content = extract_content(html, page_url)
        except Exception as e:
            click.echo(f"  [!] Conversion failed: {e}")
            continue

        if not markdown_content.strip():
            click.echo("  [skipped - no content extracted]")
            continue

        pages[page_url] = markdown_content
        click.echo(f"  [{len(markdown_content):,} chars]")

    click.echo(f"  Successfully converted {len(pages)}/{len(urls)} pages.")
    click.echo()

    # Step 3: Compile
    click.echo("[3/3] Compiling document...")
    document = compile_document(
        pages=pages,
        source_url=url,
        title=title,
    )

    # Fix the pages count placeholder in the header
    document = document.replace("{pages_placeholder}", str(len(pages)))

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(document)

    file_size = os.path.getsize(output_path)
    click.echo(f"  Document written to: {output_path}")
    click.echo(f"  Size: {file_size:,} bytes")
    click.echo()
    click.echo("Done!")


@cli.command()
@click.argument("url", type=str, required=True)
@click.option(
    "--output", "-o",
    type=str,
    default=None,
    help="Output filename (without .md extension). Defaults to <username>-profile.md",
)
@click.option(
    "--max-repos", "-m",
    type=int,
    default=100,
    help="Maximum repositories to fetch (default: 100)",
)
@click.option(
    "--delay", "-d",
    type=float,
    default=0.2,
    help="Delay between API requests in seconds (default: 0.2)",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    default=False,
    help="Enable verbose/debug logging",
)
def gh_profile(
    url: str,
    output: Optional[str],
    max_repos: int,
    delay: float,
    verbose: bool,
):
    """
    Fetch a GitHub user's public repository READMEs and compile a profile summary.

    URL is the GitHub profile URL (e.g., https://github.com/khafidhteer)
    """
    setup_logging(verbose)

    click.echo(f"webdocs2md v{__version__} — GitHub Profile Summary")
    click.echo(f"  Profile URL: {url}")
    click.echo()

    # Step 1: Extract username
    click.echo("[1/4] Extracting GitHub username...")
    try:
        username = extract_username(url)
    except ValueError as e:
        click.echo(f"  [!] {e}", err=True)
        sys.exit(1)
    click.echo(f"  Username: {username}")
    click.echo()

    # Step 2: Check rate limit
    click.echo("[2/4] Checking API rate limit...")
    rate = check_rate_limit()
    click.echo(f"  Rate limit: {rate['remaining']}/{rate['limit']} remaining")
    if rate["remaining"] < len(username) * 2:
        click.echo("  [!] Low rate limit remaining. Consider setting GITHUB_TOKEN in .env")
    click.echo()

    # Step 3: Fetch public repos
    click.echo("[3/4] Fetching public repositories...")
    try:
        repos = get_public_repos(
            username=username,
            max_repos=max_repos,
            delay=delay,
        )
    except Exception as e:
        click.echo(f"  [!] Failed to fetch repositories: {e}", err=True)
        sys.exit(1)

    if not repos:
        click.echo("  [!] No public repositories found.")
        sys.exit(1)

    click.echo(f"  Found {len(repos)} public repositories.")
    click.echo()

    # Step 4: Fetch READMEs and compile
    click.echo("[4/4] Fetching READMEs and compiling summary...")
    repo_readmes = {}
    for i, repo in enumerate(repos, 1):
        name = repo["name"]
        click.echo(f"  [{i}/{len(repos)}] {name}", nl=False)

        try:
            readme = get_repo_readme(username, name)
        except Exception as e:
            click.echo(f"  [!] Failed: {e}")
            continue

        repo_readmes[name] = readme
        click.echo(f"  [{len(readme):,} chars]" if readme else "  [no README]")

    click.echo(f"  Successfully fetched {len(repo_readmes)}/{len(repos)} READMEs.")
    click.echo()

    # Compile the document
    click.echo("  Compiling profile summary...")
    document = compile_github_summary(
        username=username,
        repos=repos,
        repo_readmes=repo_readmes,
    )

    # Determine output path
    if output is None:
        output = f"{username}-profile"
    output_dir = os.getenv("OUTPUT_DIR", "output")
    output_path = os.path.join(output_dir, f"{output}.md")
    os.makedirs(output_dir, exist_ok=True)

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(document)

    file_size = os.path.getsize(output_path)
    click.echo(f"  Document written to: {output_path}")
    click.echo(f"  Size: {file_size:,} bytes")
    click.echo()
    click.echo("Done!")


if __name__ == "__main__":
    cli()