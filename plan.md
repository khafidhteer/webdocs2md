# webdocs2md — Project Plan

## Goal
A CLI tool that crawls documentation websites (e.g., `docs.cline.bot`), discovers all linked pages under the same domain, extracts their content, and compiles everything into a single structured Markdown document.

## Technology Stack
- **Python 3.10+**
- `requests` + `beautifulsoup4` — primary HTTP fetching & HTML parsing
- `playwright` — fallback headless browser for JavaScript-rendered content
- `markdownify` — HTML-to-Markdown conversion
- `click` — CLI argument parsing
- `tqdm` — progress bar for crawl & fetch phases

## Architecture

```
webdocs2md/
├── src/
│   ├── __init__.py
│   ├── cli.py            # CLI entry point (click)
│   ├── crawler.py        # BFS URL discovery (same-domain filtering)
│   ├── fetcher.py        # Page fetching (requests → playwright fallback)
│   ├── converter.py      # HTML → clean Markdown
│   ├── compiler.py       # Assemble monolithic .md (TOC + content)
│   └── utils.py          # URL normalization, helpers
├── output/               # Generated documents
├── .env                  # Local config (gitignored)
├── .env.example          # Config template
├── plan.md               # This file
├── LICENSE               # MIT License
├── README.md             # Usage documentation
├── requirements.txt      # Dependencies
└── .gitignore
```

## Core Workflow
1. **Input**: User provides a starting URL (e.g., `https://docs.cline.bot/cline-overview`)
2. **Crawl**: BFS discover all internal URLs under the same domain
   - Respect URL normalization (trailing slash, fragment removal)
   - Deduplicate discovered URLs
   - Limit via `--max-pages` if provided
3. **Fetch & Convert**: For each discovered page:
   - Fetch HTML (requests first; if content is empty/lacks text, fall back to Playwright)
   - Extract the main content area (heuristic: `<article>`, `<main>`, `.documentation`, `.content`, or fallback to `<body>`)
   - Convert HTML to clean Markdown via `markdownify`
4. **Compile**: Assemble all pages into one document:
   - YAML-style frontmatter (source URL, timestamp)
   - Table of Contents (linked to each section)
   - Each page as a section with hierarchy-preserved headings
5. **Output**: Save to `output/<domain>-docs.md`

## CLI Usage
```bash
# Basic usage
python -m src.cli https://docs.cline.bot/cline-overview

# With options
python -m src.cli https://docs.cline.bot/cline-overview --output my-docs --max-pages 50 --concurrency 5 --no-playwright
```

### Options
| Flag | Default | Description |
|------|---------|-------------|
| `--output`, `-o` | auto | Output filename (without .md extension) |
| `--max-pages`, `-m` | 200 | Maximum pages to crawl |
| `--concurrency`, `-c` | 3 | Number of concurrent fetchers |
| `--no-playwright` | False | Disable Playwright fallback |
| `--delay`, `-d` | 0.5 | Delay between requests (seconds) |

## Action-Item Checklist

- [x] Define project scope & architecture
- [x] Create project directory structure
- [x] Create `plan.md` with checklist
- [ ] Create `LICENSE` (MIT)
- [ ] Create `.env` and `.env.example`
- [ ] Create `.gitignore`
- [ ] Create `requirements.txt`
- [ ] Create `src/__init__.py`
- [ ] Create `src/utils.py` (URL normalization, domain helpers)
- [ ] Create `src/crawler.py` (BFS crawl, same-domain filter, dedup)
- [ ] Create `src/fetcher.py` (requests + playwright fallback)
- [ ] Create `src/converter.py` (HTML → clean Markdown)
- [ ] Create `src/compiler.py` (TOC generation, page assembly)
- [ ] Create `src/cli.py` (click CLI, argument parsing)
- [ ] Create `README.md` with usage examples
- [ ] Test end-to-end with a small docs site
- [ ] Verify output matches requirements