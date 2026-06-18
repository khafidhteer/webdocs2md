# Product Context: webdocs2md

## Why This Exists
Documentation websites are ephemeral — they go offline, restructure, or change without notice. Developers frequently need offline access to docs for travel, poor connectivity, or archival purposes. Traditional solutions (wget, httrack) produce messy folder hierarchies with broken relative links. webdocs2md solves this by producing a single portable Markdown file.

## Problem Solved
1. **Fragmented docs**: Manual copy-paste of documentation is tedious and error-prone
2. **JS-rendered content**: Simple HTTP downloaders miss content loaded by JavaScript frameworks (Docusaurus, VuePress, GitBook)
3. **Noise**: Documentation sites have navigation, sidebars, footers, ads — standard tools don't extract only the content
4. **Single-file consumption**: AI models, RAG systems, and offline readers work best with one cohesive document, not hundreds of linked HTML files
5. **Portability**: Markdown is the universal format — works in any editor, version control, or LLM context

## How It Works (User Perspective)
```bash
# One command to get all docs as a single markdown file
python -m src.cli https://docs.example.com -o my-docs

# Or via Docker (zero setup)
docker compose run --rm webdocs2md https://docs.example.com -o my-docs
```

## User Experience Goals
- **Zero configuration**: Should work out of the box for most documentation sites
- **Transparent progress**: Users see exactly what's happening (crawling, fetching, converting, compiling)
- **Graceful degradation**: If Playwright isn't installed, `requests` still works for most sites
- **No surprises**: Output is clean, predictable, and consistently formatted
- **Quick iteration**: Low-pages mode (`-m 5`) for testing before full crawl

## Core Differentiators
- **Content-first approach**: Actively strips chrome (nav, sidebar, footer, ads) rather than just downloading raw HTML
- **Two-tier fetching**: `requests` for speed, Playwright fallback only when needed — avoids unnecessary browser overhead
- **Single structured document**: Not a folder of files, not a zip — one `.md` file with TOC you can drop anywhere
- **TOC with unique anchors**: Handles duplicate page titles gracefully with indexed anchors