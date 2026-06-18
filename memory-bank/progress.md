# Progress: webdocs2md

## What Works (Implemented Features)
- **BFS Crawler**: Full BFS crawl implementation with URL normalization, domain filtering, file extension exclusion, sorted output
- **Two-tier Fetching**: `requests` → Playwright fallback with meaningful content detection (200 char threshold)
- **Content Extraction**: Multi-strategy heuristic (`article` → `main` → `role="main"` → class names → `body`)
- **Chrome Removal**: Strips nav, sidebar, footer, header, aside, ads, cookies, search, comments, etc.
- **Markdown Conversion**: Using `markdownify` with ATX headings, bullet lists, autolinks
- **Document Compilation**:
  - Header with title, source URL, timestamp, page count
  - Table of Contents with unique indexed anchors
  - Individual page sections with source attribution
  - Subpage indentation in TOC
- **CLI Interface**: Click-based with all documented flags
- **Configuration**: `.env` file support via python-dotenv
- **Docker**: Multi-stage Dockerfile with Chromium pre-installed, docker-compose orchestration
- **Progress Feedback**: `tqdm` for crawl progress, per-page status during fetch/convert
- **Error Handling**: Graceful handling of fetch failures, conversion failures, empty pages

## What's Partially Implemented
- **`--concurrency` flag**: Defined in CLI and `.env.example` but **not wired to any parallel logic** — pages are fetched sequentially
- **Content detection heuristics**: Work well for common docs frameworks (Docusaurus, MkDocs, ReadTheDocs) but may fail on custom sites

## What's Missing / Not Started

### Testing
- [ ] No test suite (`tests/` directory doesn't exist)
- [ ] No unit tests for individual modules
- [ ] No integration tests
- [ ] No fixtures for sample HTML/Markdown

### CI/CD
- [ ] No GitHub Actions workflow
- [ ] No linting (ruff/flake8) configuration
- [ ] No type checking (mypy/pyright) configuration
- [ ] No automated Docker build verification

### Features
- [ ] Concurrent fetching (ThreadPoolExecutor or asyncio)
- [ ] Playwright browser context pooling
- [ ] Retry logic for transient failures
- [ ] Rate limiting detection (429 responses) with exponential backoff
- [ ] `robots.txt` compliance
- [ ] Incremental crawling (resume from cache)
- [ ] Authentication support (cookies, API keys, basic auth)
- [ ] Custom output template support
- [ ] Multiple output formats (PDF, HTML, JSON)
- [ ] Verbose output showing which content heuristic matched

### Quality & Polish
- [ ] Comprehensive logging throughout pipeline
- [ ] Better error messages with troubleshooting hints
- [ ] Command-line completion scripts
- [ ] Pre-commit hooks configuration
- [ ] Contribution guidelines (CONTRIBUTING.md)
- [ ] Changelog (CHANGELOG.md)
- [ ] Code quality badges in README

### Documentation
- [ ] API documentation (Sphinx or mkdocs)
- [ ] Troubleshooting guide
- [ ] FAQ section
- [ ] Examples directory with sample outputs

## Known Limitations
1. **Sequential fetch**: Despite `--concurrency` flag, pages are fetched one at a time (slow for large sites)
2. **No test coverage**: All testing is manual — no automated regression protection
3. **Playwright overhead**: New browser instance per page — inefficient for sites needing many JS renders
4. **No SPA/hash routing support**: Hash-based URL fragments are stripped during normalization
5. **No incremental mode**: Full crawl every time, no caching or resume capability
6. **Hard-coded timeouts**: 30s timeout in both fetcher paths not configurable via `.env` at runtime
7. **Error opacity**: All exceptions are caught as `Exception` — no fine-grained error classification

## Milestone History
| Milestone | Status | Description |
|-----------|--------|-------------|
| v1.0.0 | ✅ Complete | Core pipeline working, Docker support, basic features |
| v1.1.0 | ⬜ Planned | Concurrent fetching, test suite, improved error handling |
| v1.2.0 | ⬜ Planned | Playwright pooling, rate limit handling, CI/CD setup |
| v2.0.0 | ⬜ Future | Authentication support, SPA routing, incremental crawling |