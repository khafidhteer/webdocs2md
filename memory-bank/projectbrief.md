# Project Brief: webdocs2md

## What is webdocs2md?
A Python CLI tool that crawls documentation websites and compiles them into a single structured Markdown document. It's designed for developers who want to download, archive, or process documentation for offline use, AI context, or custom knowledge bases.

## Core Mission
Provide a reliable, zero-config way to convert any documentation website into a clean, well-structured Markdown file — handling JS-rendered content, stripping navigation chrome, and producing a single portable document with a Table of Contents.

## Key Features
- **Automatic crawling** — BFS discovery of all internal documentation pages
- **Smart content extraction** — Heuristics to find main content, remove navigation/sidebars/ads
- **Clean Markdown output** — Uses `markdownify` for high-quality HTML-to-Markdown conversion
- **JavaScript support** — Optional Playwright fallback for JS-rendered documentation sites
- **Single-file output** — All pages compiled into one well-structured document with Table of Contents
- **Configurable** — Max pages, delay, concurrency, and more via CLI flags or `.env`
- **Progress bars** — Real-time feedback during crawling and conversion
- **Docker-ready** — Pre-configured multi-stage Dockerfile with Playwright pre-installed

## Target Users
- Developers who need offline/local access to documentation
- AI engineers building RAG systems (providing doc context)
- Technical writers and archivists
- Anyone who wants to consume docs as Markdown

## Success Criteria
- Correctly crawls and extracts content from a variety of documentation sites (Docusaurus, MkDocs, ReadTheDocs, GitBook, custom docs)
- Handles JS-rendered content gracefully via Playwright fallback
- Produces valid, clean Markdown without excessive whitespace or broken links
- Respects target servers (rate limiting, delay, max pages)
- Works both natively (Python) and via Docker with zero extra config