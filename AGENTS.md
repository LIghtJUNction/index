# Repository Guidelines

## Project Structure & Module Organization

This repository publishes LIghtJUNction’s public GitHub project index. `site/` contains the HTML, CSS, JavaScript, and generated `projects.json` snapshot. `scripts/update.py` fetches repository metadata and builds the static website. `tests/` contains Python unit tests. `.github/workflows/index.yml` checks contributions, refreshes metadata daily, and deploys GitHub Pages. `dist/` is ignored build output; never commit it.

## Build, Test, and Development Commands

Use Python 3.10 or newer and Node.js for JavaScript syntax checks. No third-party packages are required.

- `python scripts/update.py`: build `dist/` from the committed snapshot without network access.
- `python scripts/update.py --refresh`: fetch public repositories and rebuild; optionally supply `GH_TOKEN` through the environment.
- `python -m http.server 8000 --directory dist`: preview at `http://localhost:8000`.
- `python -m unittest discover -s tests -v`: run offline unit tests.
- `node --check site/app.js`: validate JavaScript syntax.

## Coding Style & Naming Conventions

Use four spaces and snake_case for Python functions; use two spaces and camelCase in JavaScript. Keep HTML semantic, form controls labeled, and layouts responsive. Use descriptive CSS classes and existing CSS variables. There is no configured formatter or linter. Prefer the standard library and browser APIs over introducing dependencies. Insert repository descriptions using `textContent`, never raw HTML.

## Testing Guidelines

Tests use Python’s `unittest`; name files `test_*.py` and methods `test_*`. Mock API requests and use temporary directories. Cover pagination, public-only filtering, deterministic snapshots, failure preservation, and build boundaries when changing synchronization. No numeric coverage threshold is enforced. Before submitting UI changes, check desktop/mobile layouts, search, filters, sorting, and empty results.

## Commit & Pull Request Guidelines

The repository starts without an established commit history. Use concise Conventional Commit subjects such as `feat: add language filter` or `fix: preserve snapshot on fetch failure`. Pull requests should explain behavior changes, list local validation, and link relevant issues. Include screenshots for visual changes. Keep generated metadata changes separate from unrelated edits.

## Automation & Security

Only publish public repository metadata. Never commit tokens or `.env` files. Preserve read-only PR permissions; update and deployment permissions belong only to the main-branch publishing job. Keep scheduled synchronization and Pages deployment in the same workflow run.
