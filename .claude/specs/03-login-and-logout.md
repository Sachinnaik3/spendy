# Spec: Login and Logout

## Overview

Add a working sign-in and sign-out flow so a registered user can prove who they are and the app can remember it between page loads. The `/login` page already renders a form, but submitting it does nothing. This step adds the `POST /login` handler, which looks up the user by email, checks the submitted password against the stored hash, and on success stores the user's id in the Flask session. It also replaces the `/logout` placeholder with a real handler that clears the session. This is step 3 of the Spendly roadmap. It builds on registration (step 2) and is the prerequisite for the profile page (step 4) and every feature that is tied to a logged-in user.

## Depends on

- **Step 1 — Database setup.** Requires the `users` table, `get_db()`, and `init_db()` from `database/db.py`.
- **Step 2 — Registration.** Requires users to exist with a `password_hash` created by `generate_password_hash`, and the normalised (lowercased) email convention.

## Routes

- `GET /login` — render the sign-in form (already exists, unchanged) — public
- `POST /login` — look up the user by email, verify the password, set the session on success and redirect to `/profile`, or re-render the form with an error on failure — public
- `GET /logout` — clear the session and redirect to `/` — logged-in (a logged-out visitor is also redirected to `/` harmlessly)

## Database changes

No database changes. The existing `users` table already has `id`, `email` (UNIQUE), and `password_hash`, which covers everything this step needs. Verified against `database/db.py`.

Add one helper function to `database/db.py`:

- `get_user_by_email(email)` — runs a parameterised `SELECT id, name, email, password_hash FROM users WHERE email = ?` and returns the row as a `sqlite3.Row`, or `None` if no match. Closes the connection in a `finally` block, matching `create_user()`.

## Templates

- **Create:** none
- **Modify:**
    - `templates/login.html` — pre-fill the `email` input with the submitted value on error (`value="{{ email or '' }}"`). Do not pre-fill the password. The `auth-error` block already renders `error`.
    - `templates/base.html` — none required for this step. The navbar currently shows "Get started" for everyone. Showing a logged-in state in the navbar is out of scope and belongs to the profile step.

## Files to change

- `app.py` — replace the `login()` view with one that handles `GET` and `POST`; replace the `logout()` placeholder with a real handler; import `session` from `flask`; import `check_password_hash` from `werkzeug.security`; import `get_user_by_email` from `database.db`; set `app.secret_key` from the `SECRET_KEY` environment variable
- `database/db.py` — add the `get_user_by_email()` function
- `templates/login.html` — pre-fill `email` on error, as described above

## Files to create

- None

## New dependencies

No new dependencies. Uses `flask.session` (already part of Flask) and `werkzeug.security.check_password_hash` (already installed).

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterised queries only. No string formatting or f-strings in SQL.
- Passwords verified with `werkzeug.security.check_password_hash`. Never compare plaintext, never store or log plaintext passwords.
- `app.secret_key` must be set before any session use. Read it from `os.environ.get("SECRET_KEY")`. If the variable is not set, fall back to a clearly-marked development-only default string so `uv run python app.py` still starts. Do not commit a real secret.
- Normalise the email with `.strip().lower()` before the lookup, exactly as registration does, so login matches the stored value.
- Validation happens in the route before any database call. Do not rely on the HTML `required` attribute alone.
- Use one generic message for every failed login: `"Invalid email or password."`. Do not reveal whether the email exists.
- On failure, re-render `login.html` with HTTP status 200, the error message, and the submitted email. Do not redirect.
- On success, call `session.clear()` first (to prevent session fixation), then set `session["user_id"]` and `session["user_name"]`, then redirect (HTTP 302) to `url_for('profile')`.
- `GET /logout` calls `session.clear()` and redirects (HTTP 302) to `url_for('landing')`. It must work whether or not a user is logged in.
- Use Flask's signed session cookie only. Do not add Flask-Login or any other auth library.
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`

## Definition of done

- [ ] `GET /login` still renders the form with no errors
- [ ] Logging in with `demo@spendly.com` / `demo123` (the seeded demo user) redirects to `/profile`
- [ ] After a successful login, the browser has a `session` cookie, and `/profile` is reachable (it currently shows the step-4 placeholder text, which confirms the redirect target)
- [ ] Logging in with `DEMO@spendly.com` / `demo123` (different casing) also succeeds
- [ ] Logging in with the correct email and a wrong password shows "Invalid email or password." and keeps the email value in the field
- [ ] Logging in with an email that does not exist shows the same "Invalid email or password." message
- [ ] Submitting an empty email or empty password shows "Invalid email or password." and does not crash
- [ ] The password field is empty after a failed login
- [ ] Visiting `/logout` after logging in clears the session and redirects to `/`
- [ ] After logout, visiting `/profile` no longer has the session set (verify via browser devtools that the `session` cookie is cleared or no longer contains `user_id`)
- [ ] Visiting `/logout` while logged out does not error and redirects to `/`
- [ ] Registering a new user at `/register` and then logging in with those credentials succeeds
- [ ] The login page renders correctly at phone width (16px side gutter, no horizontal scroll), using the existing `auth-*` and `form-*` styles
- [ ] `uv run python app.py` starts without errors and the login and logout flow works end to end on http://localhost:8080/login
</content>
