# Active Context: webdocs2md

## Current State
webdocs2md is at **version 1.0.0** — a functional, stable release. The core pipeline (crawl → fetch → convert → compile) works end-to-end. The project is actively maintained and used.

## Recent Changes (from Git)
- Initial project setup, all modules implemented
- Docker support with multi-stage build (Playwright + Chromium bundled)
- `.clinerules` and `memory-bank/` created for AI-assisted development context

## Active Development Focus
- **New feature**: `gh-profile` subcommand for GitHub profile summaries (v1.1.0)
- The `--concurrency` flag is defined in the CLI but **not yet implemented** in the fetcher — pages are fetched sequentially in the current codebase
- No test suite exists yet (no `tests/` directory)
- No CI/CD pipeline configured

## Known Issues & Gaps

### Technical Debt
1. **Concurrency not implemented**: `--concurrency` flag accepted but unused — `cli.py` fetches pages in a simple `for` loop; no `asyncio` or `concurrent.futures` usage
2. **No unit tests**: No test files exist; the project relies on manual testing via `python -m src.cli`
3. **Playwright browser lifecycle**: Each call to `_fetch_with_playwright()` opens and closes a new browser instance — no connection/context pooling, leading to overhead
4. **Error recovery on crawl-crawl fetch failure**: When `crawl_site` fails to fetch a page during BFS, it silently continues — there's no retry logic
5. **Hard-coded timeout values**: 30s timeout is hard-coded in both `_fetch_with_requests()` and Playwright instead of reading from `.env`
6. **No streaming output**: All pages must be fetched before any output is written; no incremental/streaming write support

### Edge Cases
- Sites with redirect chains may produce unexpected URL sets
- Sites requiring authentication (login gates) aren't handled
- Very large sites (>200 pages) may hit rate limiting despite delay setting
- Single-page applications (SPAs) with hash-based routing won't be properly crawled

## Current Architecture Decisions

### What's Working Well
- Modular pipeline architecture makes each stage independently testable
- Content extraction heuristics handle multiple documentation site formats
- Two-tier fetching provides good balance of speed and coverage
- Docker setup is minimal-config and includes all dependencies
- Placeholder token pattern for page count is clean and practical

### What Needs Attention
- The sequential fetch loop in `cli.py` could be significantly faster with concurrent requests
- No robust error classification — fetch failures, conversion failures, and crawl failures all treated similarly
- URL deduplication currently removes query strings, which may cause issues for sites using query parameters for content variation
- No `robots.txt` respect (could be considered for politeness)

## Next Steps / Priorities
1. **Implement concurrency**: Use `concurrent.futures.ThreadPoolExecutor` for parallel fetching
2. **Add test suite**: pytest-based tests for each pipeline stage
3. **Improve error handling**: Retry logic, better error classification, user-friendly messages
4. **Add CI**: GitHub Actions for linting, testing, and Docker build verification
5. **Playwright pooling**: Reuse browser context across fetches for better performance
6. **Rate limit handling**: Detect 429 responses and implement exponential backoff
7. **Documentation**: Expand README with more examples, troubleshooting guide

## Active CLI Flags (all defined in Click command)
| Flag | Implemented? | Notes |
|------|-------------|-------|
| `--output` / `-o` | ✅ Yes | |
| `--max-pages` / `-m` | ✅ Yes | |
| `--concurrency` / `-c` | ❌ No | Flag exists but not wired to any parallel logic |
| `--delay` / `-d` | ✅ Yes | |
| `--no-playwright` | ✅ Yes | |
| `--verbose` / `-v` | ✅ Yes | |
| `--title` | ✅ Yes | |
| `--version` | ✅ Yes | Click built-in |