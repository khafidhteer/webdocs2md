# webdocs2md

**Transform documentation websites and GitHub profiles into structured Markdown documents.**

```
# Crawl a documentation site
webdocs2md crawl https://docs.cline.bot -o cline-documentation

# Or compile a GitHub profile summary
webdocs2md gh-profile https://github.com/khafidhteer -o khafidhteer-summary
```

## Features

- 🔍 **Automatic crawling** — BFS discovery of all internal documentation pages
- 🧹 **Smart content extraction** — Heuristics to find main content, remove navigation/sidebars/ads
- 📝 **Clean Markdown output** — Uses `markdownify` for high-quality HTML-to-Markdown conversion
- 🌐 **JavaScript support** — Optional Playwright fallback for JS-rendered documentation sites
- 📑 **Single-file output** — All pages compiled into one well-structured document with Table of Contents
- ⚙️ **Configurable** — Max pages, delay, concurrency, and more via CLI flags or `.env`
- 🦦 **Progress bars** — Real-time feedback during crawling and conversion
- 🐳 **Docker-ready** — Pre-configured multi-stage Dockerfile with Playwright pre-installed
- 👤 **GitHub Profile Summary** — Fetch all public repository READMEs and compile a single profile document with aggregated stats

## Installation

### Option A — Python (native)

#### Prerequisites
- **Python 3.10 or higher**
- **Playwright** (optional, for JS-rendered sites): `playwright install chromium`

#### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/webdocs2md.git
cd webdocs2md

# Install dependencies
pip install -r requirements.txt

# (Optional) Install Playwright browsers for JavaScript-rendered content
playwright install chromium
```

### Option B — Docker (recommended for zero-config)

#### Prerequisites
- **Docker** and **Docker Compose** installed

#### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/webdocs2md.git
cd webdocs2md

# Build the Docker image (Playwright + Chromium included)
docker compose build
```

No Python or Playwright installation needed — everything is bundled inside the container.

## Usage

The tool has two modes, each as a subcommand:

### Mode 1: Crawl Documentation Sites (`crawl`)

```bash
# Python (native)
python -m src.cli crawl https://docs.cline.bot -o cline-documentation

# Docker
docker compose run --rm webdocs2md crawl https://docs.cline.bot -o cline-documentation
```

This will:
1. Start from the given URL
2. Crawl all linked pages under `docs.cline.bot`
3. Convert each page to Markdown
4. Compile everything into `output/cline-documentation.md`

#### Options (`crawl`)

| Flag | Default | Description |
|------|---------|-------------|
| `--output`, `-o` | `<domain>-docs` | Output filename (without `.md` extension) |
| `--max-pages`, `-m` | `200` | Maximum number of pages to crawl |
| `--concurrency`, `-c` | `3` | Number of concurrent fetchers (not yet implemented) |
| `--delay`, `-d` | `0.5` | Delay between requests (seconds) |
| `--no-playwright` | `False` | Disable Playwright fallback for JS content |
| `--verbose`, `-v` | `False` | Enable debug logging |
| `--title` | domain-based | Custom title for the generated document |
| `--version` | — | Show version and exit |
| `--help` | — | Show help message |

#### Examples (`crawl`)

```bash
# === Python (native) ===
# Crawl with custom output filename
python -m src.cli crawl https://docs.cline.bot/cline-overview -o cline-documentation

# Limit to 50 pages, with 1 second delay
python -m src.cli crawl https://docs.cline.bot/cline-overview -m 50 -d 1.0

# Disable Playwright (requests only)
python -m src.cli crawl https://docs.cline.bot/cline-overview --no-playwright

# Verbose mode for debugging
python -m src.cli crawl https://docs.cline.bot/cline-overview -v

# Custom document title
python -m src.cli crawl https://docs.cline.bot/cline-overview --title "Cline Bot Docs"

# === Docker ===
# All the same flags work via Docker
docker compose run --rm webdocs2md crawl https://docs.cline.bot/cline-overview -o cline-documentation -m 50 -d 1.0

# Show help
docker compose run --rm webdocs2md --help

# Disable Playwright in Docker
docker compose run --rm webdocs2md crawl https://docs.cline.bot/cline-overview --no-playwright
```

### Mode 2: GitHub Profile Summary (`gh-profile`)

```bash
# Python (native)
python -m src.cli gh-profile https://github.com/khafidhteer -o khafidhteer-summary

# Docker
docker compose run --rm webdocs2md gh-profile https://github.com/khafidhteer -o khafidhteer-summary
```

This will:
1. Extract the GitHub username from the profile URL
2. Check GitHub API rate limit status
3. List all public repositories with metadata (language, topics, stars, forks)
4. Fetch each repository's README file
5. Compile everything into `output/khafidhteer-summary.md`

The generated document includes all README content in a single file, structured for direct use as LLM input or AI context.

#### Options (`gh-profile`)

| Flag | Default | Description |
|------|---------|-------------|
| `--output`, `-o` | `<username>-profile` | Output filename (without `.md` extension) |
| `--max-repos`, `-m` | `100` | Maximum number of repositories to fetch |
| `--delay`, `-d` | `0.2` | Delay between API requests (seconds) |
| `--verbose`, `-v` | `False` | Enable debug logging |
| `--help` | — | Show help message |

#### Examples (`gh-profile`)

```bash
# === Python (native) ===
# Generate a full profile summary
python -m src.cli gh-profile https://github.com/khafidhteer -o khafidhteer-summary

# Limit to 5 repositories for testing
python -m src.cli gh-profile https://github.com/khafidhteer -m 5

# Verbose mode with debug logging
python -m src.cli gh-profile https://github.com/khafidhteer -v

# === Docker ===
docker compose run --rm webdocs2md gh-profile https://github.com/khafidhteer -o khafidhteer-summary

# With repo limit
docker compose run --rm webdocs2md gh-profile https://github.com/khafidhteer -m 5

# Show help
docker compose run --rm webdocs2md gh-profile --help
```

#### Rate Limits

The GitHub API has rate limits:
- **Unauthenticated**: 60 requests per hour (sufficient for small profiles)
- **Authenticated**: 5,000 requests per hour (set `GITHUB_TOKEN` in `.env`)

The tool checks your rate limit before fetching and warns if it's low.

## Output Formats

### Documentation Crawl Output

```markdown
# Cline Bot Documentation

> **Source**: https://docs.cline.bot/cline-overview
> **Generated**: 2026-06-11 07:30 UTC
> **Pages**: 42

---

## Table of Contents
- [Home / Overview](#home--overview-0)
- [Getting Started](#getting-started-1)
  - [Installation](#installation-2)

---

## Home / Overview

*Source: [https://docs.cline.bot/cline-overview](https://docs.cline.bot/cline-overview)*

[content...]

---

## Getting Started

*Source: [https://docs.cline.bot/getting-started](https://docs.cline.bot/getting-started)*

[content...]
```

### GitHub Profile Summary Output

```markdown
# username — GitHub Profile Summary

> **Profile**: https://github.com/username
> **Generated**: 2026-06-18 12:00 UTC
> **Public Repositories**: 26

---

## Table of Contents
- [repo-one](#repo-one-0)
- [repo-two](#repo-two-1)
- [Summary](#summary)

---

## repo-one

*Repository: [repo-one](https://github.com/username/repo-one)*

| Attribute | Value |
|-----------|-------|
| **Description** | Description of the repo |
| **Language** | Python |
| **Stars** | 5 |
| **Forks** | 2 |
| **Topics** | python, cli, docs |
| **Archived** | No |
| **Fork** | No |

[README content...]

---

## Summary

### Languages Used
- **Python**: 10 repos ██████████
- **JavaScript**: 5 repos █████

### Common Topics
- **python** (10 repos)
- **cli** (3 repos)

### Repository Statistics
- **Total public repos**: 26
- **Archived**: 1
- **Forks**: 3
- **Active (non-archived, non-fork)**: 22

---

*This document contains all README content for LLM ingestion.*
```

## Configuration

Copy `.env.example` to `.env` and adjust:

| Variable | Default | Description |
|----------|---------|-------------|
| `OUTPUT_DIR` | `output` | Directory for generated documents |
| `DEFAULT_MAX_PAGES` | `200` | Default max pages to crawl |
| `DEFAULT_CONCURRENCY` | `3` | Default concurrent fetchers |
| `DEFAULT_DELAY` | `0.5` | Default delay between requests (s) |
| `USER_AGENT` | Chrome UA | User-Agent header for HTTP requests |
| `PLAYWRIGHT_TIMEOUT` | `30000` | Playwright page load timeout (ms) |
| `PLAYWRIGHT_HEADLESS` | `true` | Run Playwright in headless mode |
| `GITHUB_TOKEN` | — | GitHub API token for higher rate limits (optional) |

## Project Structure

```
webdocs2md/
├── src/
│   ├── __init__.py         # Package init & version
│   ├── cli.py              # CLI entry point (click, subcommands: crawl + gh-profile)
│   ├── crawler.py          # BFS URL discovery
│   ├── fetcher.py          # Page fetching (requests → playwright)
│   ├── converter.py        # HTML → Markdown conversion
│   ├── compiler.py         # Document assembly (crawl + gh-profile summaries)
│   ├── github_scraper.py   # GitHub API interaction (repos, READMEs)
│   └── utils.py            # URL helpers & normalization
├── output/                 # Generated documents
├── .env                    # Local configuration
├── .env.example            # Config template
├── .dockerignore           # Files excluded from Docker build context
├── Dockerfile              # Multi-stage Docker build (Playwright included)
├── docker-compose.yml      # One-command container orchestration
├── .clinerules             # AI-assisted development rules
├── memory-bank/            # Project context for AI tools
├── plan.md                 # Project plan & checklist
├── LICENSE                 # MIT License
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

## License

MIT