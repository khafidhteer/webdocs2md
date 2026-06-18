# Technical Context: webdocs2md

## Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.10+ | Main implementation |
| CLI Framework | Click | >=8.1.0 | Argument parsing, command interface |
| HTTP Client | requests | >=2.31.0 | Page fetching |
| HTML Parsing | BeautifulSoup 4 | >=4.12.0 | HTML parsing and content extraction |
| HTML→Markdown | markdownify | >=0.12.0 | HTML to Markdown conversion |
| Progress Bars | tqdm | >=4.66.0 | Crawl progress feedback |
| Browser Automation | Playwright | >=1.45.0 | JS-rendered page fallback |
| Config | python-dotenv | >=1.0.0 | `.env` file loading |

## Development Environment
- **Python**: 3.10+ required (type hints, f-strings, modern features)
- **Package manager**: pip
- **Containerization**: Docker + Docker Compose (multi-stage build)
- **OS**: Cross-platform (Windows, macOS, Linux)

## Project Structure
```
webdocs2md/
├── src/                    # Package source
│   ├── __init__.py         # Version: 1.0.0
│   ├── cli.py              # Click CLI entry point
│   ├── crawler.py          # BFS crawler
│   ├── fetcher.py          # HTTP + Playwright fetcher
│   ├── converter.py        # HTML → Markdown
│   ├── compiler.py         # Document assembly
│   └── utils.py            # URL helpers
├── output/                 # Generated .md files (gitignored)
├── .env                    # Local configuration (gitignored)
├── .env.example            # Configuration template
├── Dockerfile              # Multi-stage build
├── docker-compose.yml      # One-command orchestration
├── requirements.txt        # Python dependencies
├── README.md               # Documentation
└── LICENSE                 # MIT
```

## Configuration (.env)
| Variable | Default | Description |
|----------|---------|-------------|
| `OUTPUT_DIR` | `output` | Directory for generated documents |
| `DEFAULT_MAX_PAGES` | `200` | Default max pages to crawl |
| `DEFAULT_CONCURRENCY` | `3` | Concurrent fetcher count |
| `DEFAULT_DELAY` | `0.5` | Delay between requests (seconds) |
| `USER_AGENT` | Chrome 125 UA | User-Agent header for HTTP requests |
| `PLAYWRIGHT_TIMEOUT` | `30000` | Playwright page load timeout (ms) |
| `PLAYWRIGHT_HEADLESS` | `true` | Run Playwright in headless mode |

## Docker Setup
- **Base image**: `python:3.11-slim`
- **Playwright**: Installed system dependencies + Chromium browser in Dockerfile
- **Usage**: `docker compose run --rm webdocs2md <url> [options]`
- **Build**: `docker compose build` (includes Playwright + Chromium)

## Key Technical Decisions

### Why `requests` + Playwright (not just one or the other)
- `requests` is lightweight, fast, and works for 90%+ of sites (especially static docs)
- Playwright adds ~300MB+ of browser binaries and startup latency
- Two-tier approach: use the fast path when possible, fall back only when needed

### Why BeautifulSoup (not lxml or html5lib)
- BeautifulSoup is already included in most Python environments
- Handles real-world broken HTML better than lxml
- `html.parser` (stdlib) keeps the dependency footprint smaller than `lxml` or `html5lib`

### Why `markdownify` (not pandoc or custom converter)
- Pure Python library, no external binary dependencies
- Sufficient quality for documentation content
- Easy to customize (heading style, bullet style, strip tags, autolinks)

### Why BFS (not DFS)
- Respects site hierarchy — pages closer to root are processed first
- More predictable ordering than DFS
- Sorted output at the end provides consistent, deterministic results

## Dependencies (requirements.txt)
```
click>=8.1.0
requests>=2.31.0
beautifulsoup4>=4.12.0
markdownify>=0.12.0
tqdm>=4.66.0
playwright>=1.45.0
python-dotenv>=1.0.0
```

## Key Constraints & Limitations
- **Python 3.10+ required**: Uses modern typing features
- **No concurrency in current implementation**: Sequential fetch after crawl (despite `--concurrency` flag existing)
- **Single-threaded Playwright**: Each Playwright call opens/closes a browser instance (no connection pooling)
- **No incremental crawling**: Always starts from scratch
- **No output diffing**: Overwrites existing output file entirely