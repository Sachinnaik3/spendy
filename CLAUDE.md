# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- Setup: `uv sync` (Python 3.14 per `.python-version`; `uv.toml` sets `system-certs = true`)
- Run the dev server: `uv run python app.py` (serves on http://localhost:8080 with debug on)
- Tests: `uv run pytest`. `pytest` and `pytest-flask` are declared, but there is no `tests/` directory yet. To run one test: `uv run pytest path/to/test_file.py::test_name`
- `main.py` is an unused stub. `app.py` is the entry point.
- `requirements.txt` duplicates the dependencies in `pyproject.toml`. `pyproject.toml` and `uv.lock` are the source of truth.

## Architecture

- **Single Flask module.** All routes live in `app.py`. Most routes are placeholders that return plain strings and are scheduled for later steps (`/logout`, `/profile`, `/expenses/...`). Real pages so far are `/` (landing), `/register`, `/login`, `/terms`, and `/privacy`.
- **Database layer is not written yet.** `database/db.py` only contains comments describing `get_db()`, `init_db()`, and `seed_db()`. Expect these to be the first real code added there.
- **Templates share one base.** Every page extends `templates/base.html`, which provides the navbar, footer, and global `static/js/main.js`. Child templates fill these blocks: `title`, `head` (extra stylesheets), `content`, and `scripts` (page JS, loaded after `main.js`).
- **CSS is split by scope.** `static/css/style.css` holds the design tokens (`:root` variables for colors, fonts, radii), reset, navbar, footer, auth-page styles (`auth-*`, `form-*`, `btn-*`), and the legal-page styles (`legal-*`). `static/css/landing.css` is loaded only on the landing page (via the `head` block) and holds the `landing-*` hero, app-preview, and modal styles. New pages should reuse the tokens and classes from `style.css`. `landing.css` hard-codes hex colors instead of using the tokens, so don't copy that pattern elsewhere.
- **Landing modal.** The "See how it works" button opens a native `<dialog>` with an embedded YouTube iframe. The iframe's `src` is set only when the modal opens and reset to `about:blank` on the dialog's `close` event, so playback stops on every close path. The iframe's real URL lives in its `data-src` attribute.
