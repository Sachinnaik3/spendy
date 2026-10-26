# Implementation Plan: Step 1 — Database Setup

Source spec: `.claude/specs/database-setup.md`. You asked for `01-database-setup.md`, but that file does not exist. The spec is at `database-setup.md` and has its full content, so this plan follows it.

## Context

`database/db.py` is a stub with comments only. `app.py` has no database wiring. Authentication, profile, and expense features (Steps 3 onward) all depend on a working data layer. This step adds it, using only the standard library `sqlite3` and `werkzeug.security`. It adds no new packages and no routes.

## Files to change

- `database/db.py`: implement `get_db()`, `init_db()`, `seed_db()`
- `app.py`: add the imports and the startup calls

No new files. No template or CSS changes.

## Step 1: `database/db.py`

Module-level constant: `DB_PATH = os.path.join(<project root>, "spendly.db")`, where the project root comes from `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`. Using `__file__` keeps the path correct regardless of the working directory.

Use `import sqlite3`, `import os`, and `from werkzeug.security import generate_password_hash`.

**`get_db()`**
- `conn = sqlite3.connect(DB_PATH)`
- `conn.row_factory = sqlite3.Row`
- `conn.execute("PRAGMA foreign_keys = ON")`
- Return `conn`

**`init_db()`**
- Open a connection with `get_db()`, run two `CREATE TABLE IF NOT EXISTS` statements, commit, and close the connection in a `finally` block.
- `users`: `id INTEGER PRIMARY KEY AUTOINCREMENT`, `name TEXT NOT NULL`, `email TEXT NOT NULL UNIQUE`, `password_hash TEXT NOT NULL`, `created_at TEXT DEFAULT (datetime('now'))`
- `expenses`: `id INTEGER PRIMARY KEY AUTOINCREMENT`, `user_id INTEGER NOT NULL REFERENCES users(id)`, `amount REAL NOT NULL`, `category TEXT NOT NULL`, `date TEXT NOT NULL`, `description TEXT`, `created_at TEXT DEFAULT (datetime('now'))`
- Optional, not in the spec: `CREATE INDEX IF NOT EXISTS idx_expenses_user_date ON expenses(user_id, date)`. Add it only if you want it; the spec does not require it.

**`seed_db()`**
- Open a connection. Run `SELECT COUNT(*) FROM users`. If the count is greater than 0, close the connection and return. This is the guard against duplicates.
- Insert the demo user with a parameterized query: name `Demo User`, email `demo@spendly.com`, `password_hash = generate_password_hash("demo123")`.
- Read the new user's `id` from `cursor.lastrowid`.
- Insert 8 expenses with one `executemany` call, parameterized. The list must cover all seven categories (`Food`, `Transport`, `Bills`, `Health`, `Entertainment`, `Shopping`, `Other`) with at least one each, which is 7 rows, plus one more for a total of 8.
- Dates must be `YYYY-MM-DD` and fall in the current month. Build them in Python with `date.today()`, using day numbers from 1 up to today's day of month, so no date is in the future. A simple approach is to spread the 8 entries across `min(today.day, 28)`-style offsets; the exact spread is an implementation choice. Start from day 1 so the list always has data, even on the first day of the month.
- Commit once after all inserts. Roll back on error so a partial seed never remains.

Categories are a fixed list. Keep them as a module-level constant, such as `CATEGORIES`, and use it in the seed data.

## Step 2: `app.py`

- Change the import line to `from database.db import get_db, init_db, seed_db`. The spec asks for `get_db` in the imports. `get_db` is not used by the startup code, so import it only if the spec's wording is treated as a requirement; otherwise leave it out and note that.
- In the `if __name__ == "__main__":` block, before `app.run`, add:
  ```python
  with app.app_context():
      init_db()
      seed_db()
  ```
- Leave every route unchanged.

Note: with `debug=True`, Flask's reloader runs this block in the parent and the child process. Both calls are idempotent, so the second run changes nothing.

## Rules to follow (from the spec)

- No ORM. Use `sqlite3` only.
- Parameterized queries only: `?` placeholders. No f-strings or `%` formatting in SQL.
- `PRAGMA foreign_keys = ON` on every connection, set inside `get_db()`.
- `amount` is `REAL`.
- Dates are `YYYY-MM-DD` text.

## Verification

Run these from the project root with `uv run`:

1. `uv sync`, then `uv run python -c "from database.db import init_db, seed_db; init_db(); seed_db()"`. Expect no error and a `spendly.db` file in the project root.
2. Check the schema with `sqlite3` or a short script: both tables exist, the `email` column is unique, and `expenses.user_id` has a foreign key to `users.id`.
3. Run the init and seed functions a second time. `SELECT COUNT(*)` on `users` stays 1 and on `expenses` stays 8.
4. Check the seed data: `demo@spendly.com` exists, `password_hash` is not `demo123`, `check_password_hash(hash, "demo123")` returns True, there are 8 expenses, all 7 categories appear, and every date is in the current month.
5. Error cases:
   - Inserting a second user with `demo@spendly.com` raises `sqlite3.IntegrityError`.
   - Inserting an expense with `user_id = 9999` raises `sqlite3.IntegrityError`.
6. `get_db().execute("SELECT name FROM users").fetchone()["name"]` works, which confirms `row_factory`.
7. `uv run python app.py` starts with no errors. Load `/`, `/register`, `/login`, `/terms`, and `/privacy` and confirm they still render.
8. Confirm `spendly.db` is in `.gitignore`. If it is not, add it, since the spec does not say to commit the database file.

Map these to the spec's Definition of Done in section 14 when finished.

## Open points

1. Database filename: the spec allows `spendly.db` or `expense_tracker.db`. This plan uses `spendly.db`.
2. The spec's `app.py` section lists `get_db` as an import, but the startup code does not call it. This plan imports it only if you want the literal spec wording.
3. The `user_id` index is optional and not in the spec.
