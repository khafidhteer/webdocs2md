# System Patterns: webdocs2md

## Architecture Overview
webdocs2md follows a sequential **pipeline architecture** with four stages, orchestrated by the CLI entry point:

```
CLI (click) → [1. Crawler] → [2. Fetcher] → [3. Converter] → [4. Compiler] → Output .md file
```

Each stage is a separate module with a single responsibility. Data flows in one direction only — no circular dependencies between stages.

## Pipeline Stages

### Stage 1: Crawler (`crawler.py`)
**Function**: `crawl_site(start_url, max_pages, delay, use_playwright) → List[str]`

- **Algorithm**: Breadth-First Search (BFS) using `collections.deque`
- URL normalization via `normalize_url()` before adding to visited/set
- Parses HTML with BeautifulSoup to find `<a href>` links
- Filters links: same-domain only, skip non-doc file extensions (`.pdf`, `.zip`, `.png`, etc.), skip anchors/javascript/mailto
- Uses `tqdm` progress bar for user feedback
- Output: Sorted list of discovered page URLs

```
queue = [start_url]
visited = set()
while queue and len(visited) < max_pages:
    url = queue.popleft()
    fetch HTML → parse links → filter → add to queue
return sorted(discovered)
```

### Stage 2: Fetcher (`fetcher.py`)
**Function**: `fetch_page(url, use_playwright, delay) → str (HTML)`

- **Two-tier strategy**:
  1. Try `requests.get()` with browser-like headers and 30s timeout
  2. If response lacks meaningful content (<200 chars after stripping scripts/styles), fall back to Playwright
- `_has_meaningful_content()`: Strips `script`, `style`, `nav`, `footer`, `header` from HTML, checks remaining text length > 200
- Rate limiting: `time.sleep(delay)` at the start of each fetch
- Playwright: Launches headless Chromium, waits for `networkidle`, extracts rendered HTML

### Stage 3: Converter (`converter.py`)
**Function**: `extract_content(html, url) → str (Markdown)`

- **Content detection heuristic** (priority order):
  1. `<article>` tag
  2. `<main>` tag
  3. `role="main"` attribute
  4. Elements with known content class names ("content", "documentation", "prose", "markdown", etc.)
  5. `<body>` fallback
- **Chrome removal**: Decomposes `script`, `style`, `nav`, `footer`, `header`, `aside` tags, plus elements with non-content class names (sidebar, menu, toc, ads, etc.)
- **Conversion**: Uses `markdownify` with ATX headings, `-` bullets, stripped `img`/`script`/`style`
- **Cleanup**: Removes excessive blank lines, trailing whitespace

### Stage 4: Compiler (`compiler.py`)
**Function**: `compile_document(pages, source_url, title) → str (complete Markdown)`

- Assembles final document in sections:
  1. **Header**: `# Title` + metadata (source URL, generation timestamp, page count placeholder)
  2. **Table of Contents**: Links to each page section with index-suffixed anchors
  3. **Page sections**: Each page as `## Title` + `*Source: [url]*` + content
- **Anchor generation**: `title-to-anchor` converts title to lowercase, replaces spaces with hyphens, appends `-{index}` for uniqueness
- **Subpage TOC indentation**: Pages with nested paths get 2-space indent in TOC

### GitHub Profile (`github_scraper.py`)
**Functions**:
- `extract_username(url)` → extracts username from GitHub profile URL via regex
- `get_public_repos(username, max_repos, delay)` → paginated fetch of public repos via `GET /users/{user}/repos`
- `get_repo_readme(username, repo)` → fetches README via `GET /repos/{user}/{repo}/contents/README.md` (tries multiple filenames + fallback endpoint)
- `check_rate_limit()` → checks remaining API calls via `GET /rate_limit`

**Compiler integration**: `compile_github_summary(username, repos, repo_readmes)` in compiler.py assembles:
- Profile header with metadata
- Table of Contents linking to each repo
- Repository sections with metadata table + README content
- Aggregated summary (languages, topics, statistics)

## Key Design Patterns

### Pipeline Pattern
Each stage receives input, processes it, and passes output to the next stage. This makes the code easy to test, modify, or replace individual stages.

### Two-Tier Fetching (Strategy Pattern)
The fetcher implements a fallback strategy: try the fast method first (requests), fall back to the heavyweight method (Playwright) only when necessary. The `use_playwright` flag controls whether the fallback is available.

### Content Heuristics (Chain of Responsibility)
The converter tries multiple content extraction strategies in priority order, falling through to the next if no match is found. This ensures maximum compatibility across different documentation site layouts.

### Placeholder Token
The page count in the header uses `{pages_placeholder}` because the exact count isn't known until all pages have been fetched and converted. The CLI performs a final string replacement before writing the file.

## Key Relationships
```
cli.py
  ├── (crawl mode) calls crawl_site() → fetch_page() loop → compile_document()
  ├── (gh-profile mode) calls extract_username() → get_public_repos() → get_repo_readme() loop → compile_github_summary()
  └── both modes write .md output files

crawler.py
  └── uses fetch_page() from fetcher.py
  └── uses is_internal_link(), resolve_url(), normalize_url() from utils.py

fetcher.py
  └── uses BeautifulSoup from bs4 for content checking

converter.py
  └── uses BeautifulSoup + markdownify

compiler.py
  └── (crawl mode) uses urlparse for URL → title conversion
  └── (gh-profile mode) compile_github_summary() for assembling GitHub profile docs
  └── uses collections.Counter for topic aggregation

github_scraper.py (new module)
  └── extract_username(url) — regex from GitHub URL
  └── get_public_repos(username) — GET /users/{user}/repos (paginated)
  └── get_repo_readme(username, repo) — GET /repos/{user}/{repo}/contents (base64 decode)
  └── check_rate_limit() — GET /rate_limit
  └── uses requests library (shared dependency)

utils.py (independent utility functions)
  └── normalize_url(), is_internal_link(), resolve_url(), extract_domain(), url_to_filename()