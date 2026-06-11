# webdocs2md

**Crawl documentation websites and compile them into a single structured Markdown document.**

```
webdocs2md https://docs.cline.bot -o cline-documentation
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

### Option A — Python (native)

```bash
# Generate documentation from a URL
python -m src.cli https://docs.cline.bot -o cline-documentation
```

### Option B — Docker

```bash
docker compose run --rm webdocs2md https://docs.cline.bot -o cline-documentation
```

Both will:
1. Start from the given URL
2. Crawl all linked pages under `docs.cline.bot`
3. Convert each page to Markdown
4. Compile everything into `output/cline-documentation.md`

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--output`, `-o` | `<domain>-docs` | Output filename (without `.md` extension) |
| `--max-pages`, `-m` | `200` | Maximum number of pages to crawl |
| `--delay`, `-d` | `0.5` | Delay between requests (seconds) |
| `--no-playwright` | `False` | Disable Playwright fallback for JS content |
| `--verbose`, `-v` | `False` | Enable debug logging |
| `--title` | domain-based | Custom title for the generated document |
| `--version` | — | Show version and exit |
| `--help` | — | Show help message |

### Examples

```bash
# === Python (native) ===
# Crawl with custom output filename
python -m src.cli https://docs.cline.bot/cline-overview -o cline-documentation

# Limit to 50 pages, with 1 second delay
python -m src.cli https://docs.cline.bot/cline-overview -m 50 -d 1.0

# Disable Playwright (requests only)
python -m src.cli https://docs.cline.bot/cline-overview --no-playwright

# Verbose mode for debugging
python -m src.cli https://docs.cline.bot/cline-overview -v

# Custom document title
python -m src.cli https://docs.cline.bot/cline-overview --title "Cline Bot Docs"

# === Docker ===
# All the same flags work via Docker
docker compose run --rm webdocs2md https://docs.cline.bot/cline-overview -o cline-documentation -m 50 -d 1.0

# Show help
docker compose run --rm webdocs2md --help

# Disable Playwright in Docker
docker compose run --rm webdocs2md https://docs.cline.bot/cline-overview --no-playwright
```

## Output Format

The generated Markdown document includes:

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

## Configuration

Copy `.env.example` to `.env` and adjust:

| Variable | Default | Description |
|----------|---------|-------------|
| `OUTPUT_DIR` | `output` | Directory for generated documents |
| `DEFAULT_MAX_PAGES` | `200` | Default max pages to crawl |
| `DEFAULT_DELAY` | `0.5` | Default delay between requests (s) |
| `USER_AGENT` | Chrome UA | User-Agent header for HTTP requests |
| `PLAYWRIGHT_TIMEOUT` | `30000` | Playwright page load timeout (ms) |
| `PLAYWRIGHT_HEADLESS` | `true` | Run Playwright in headless mode |

## Project Structure

```
webdocs2md/
├── src/
│   ├── __init__.py      # Package init & version
│   ├── cli.py           # CLI entry point (click)
│   ├── crawler.py       # BFS URL discovery
│   ├── fetcher.py       # Page fetching (requests → playwright)
│   ├── converter.py     # HTML → Markdown conversion
│   ├── compiler.py      # Document assembly (TOC + content)
│   └── utils.py         # URL helpers & normalization
├── output/              # Generated documents
├── .env                 # Local configuration
├── .env.example         # Config template
├── .dockerignore        # Files excluded from Docker build context
├── Dockerfile           # Multi-stage Docker build (Playwright included)
├── docker-compose.yml   # One-command container orchestration
├── plan.md              # Project plan & checklist
├── LICENSE              # MIT License
├── README.md            # This file
└── requirements.txt     # Python dependencies
```

## License

MIT