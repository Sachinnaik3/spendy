# Implementation Plan: Step 3 — Login and Logout

Source spec: `.claude/specs/03-login-and-logout.md`.

## Context

`/login` renders a form, but `POST /login` does nothing. `/logout` is still a placeholder string. Registration (step 2) is merged, so users with hashed passwords already exist in `users`. This step adds credential checking and a session, so that the profile page (step 4) and every later feature can tell who is logged in. It adds no new packages and no new routes beyond the `POST /login` handler.

## Files to change

- `database/db.py`: add `get_user_by_email(email)`
- `app.py`: implement `login()` for GET and POST, implement `logout()`, set `app.secret_key`
- `templates/login.html`: pre-fill the email input on error

No new files. No CSS changes. No changes to `base.html`.

## Step 1: `database/db.py`

Add `get_user_by_email(email)` below `create_user()`:

- Run a parameterised `SELECT id, name, email, password_hash FROM users WHERE email = ?`.
- Return the row, or `None` when there is no match. `get_db()` sets `row_factory = sqlite3.Row`, so callers can use `user["password_hash"]`.
- Close the connection in a `finally` block, matching `create_user()`.

## Step 2: `app.py`

- Imports: `os`, `session` from Flask, `check_password_hash` from `werkzeug.security`, and `get_user_by_email` from `database.db`.
- After `app = Flask(__name__)`: `app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")`. The fallback is for local development only.
- `login()` accepts `GET` and `POST`:
  - `GET` renders `login.html`.
  - `POST` normalises the email with `.strip().lower()`. If the email or password is empty, or the user is not found, or `check_password_hash` fails, it re-renders with `"Invalid email or password."` and the submitted email. Otherwise it calls `session.clear()`, sets `user_id` and `user_name`, and redirects to `/profile`.
- `logout()` calls `session.clear()` and redirects to `/`. It has moved out of the placeholder block into the routes section.

## Step 3: `templates/login.html`

- Add `value="{{ email or '' }}"` to the email input. The password input is unchanged.

## Rules to follow (from the spec)

- `sqlite3` with `?` placeholders only. No ORM, no f-strings in SQL.
- Passwords are checked only with `check_password_hash`. Never log plaintext.
- One generic error message for every failed login.
- Flask's signed session only. No Flask-Login.
- Existing `auth-*` and `form-*` classes and CSS variables. No hex values.

## Verification

1. `uv run python app.py` starts. `/login` renders.
2. `demo@spendly.com` / `demo123` redirects to `/profile`. `DEMO@spendly.com` also succeeds.
3. A wrong password, an unknown email, and empty fields each show "Invalid email or password.". The email stays filled and the password is empty.
4. After login the `session` cookie holds `user_id`. `/logout` redirects to `/` and clears it. `/logout` while logged out also redirects to `/`.
5. Register a new user, then log in with those credentials.
6. Check the login page at phone width: no horizontal scroll, 16px gutter.

## Open points (recommended defaults)

1. **Secret key:** read from `SECRET_KEY` with a dev-only fallback. The alternative is a hard-coded key, which commits a secret to the repo.
2. **Post-login redirect:** `/profile`, which is a placeholder until step 4, as the spec says.
3. **Timing:** an unknown email skips the hash check, so that response is slightly faster. Left for later; outside the spec.
