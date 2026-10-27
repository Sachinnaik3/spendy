# Spec: Registration

## Overview

Add a working sign-up flow so a new visitor can create a Spendly account. The `/register` page already renders a form, but submitting it does nothing. This step adds the `POST /register` handler, validates the submitted fields, stores the new user with a hashed password in the `users` table, and reports errors back on the same form. It is step 2 of the Spendly roadmap: it builds on the data layer from step 1 and is the prerequisite for login (step 3), profile (step 4), and every feature that is tied to a user.

## Depends on

- **Step 1 — Database setup.** Requires the `users` table, `get_db()`, and `init_db()` from `database/db.py`, and `werkzeug.security` for password hashing.

## Routes

- `GET /register` — render the registration form (already exists, unchanged) — public
- `POST /register` — validate the form, create the user, redirect to `/login` on success or re-render the form with an error on failure — public

## Database changes

No database changes. The existing `users` table already has `name`, `email` (UNIQUE), `password_hash`, and `created_at`, which covers everything this step needs. Verified against `database/db.py`.

Add one helper function to `database/db.py`:

- `create_user(name, email, password)` — hashes the password with `generate_password_hash`, inserts the row using a parameterised `INSERT`, commits, and returns the new user id. It lets the duplicate-email `sqlite3.IntegrityError` propagate so the route can handle it.

## Templates

- **Create:** none
- **Modify:**
    - `templates/register.html` — no structural change required. Confirm it renders the `error` variable inside `.auth-error` (it already does). Pre-fill the `name` and `email` inputs with the submitted values on error so the user does not retype them (`value="{{ name or '' }}"`, `value="{{ email or '' }}"`). Do not pre-fill the password.

## Files to change

- `app.py` — replace the `register()` view with one that handles both `GET` and `POST`; import `create_user` from `database.db`; import `request` from `flask`
- `database/db.py` — add the `create_user()` function
- `templates/register.html` — pre-fill `name` and `email` on error, as described above

## Files to create

- None

## New dependencies

No new dependencies. Uses `flask.request` (already part of Flask) and `werkzeug.security` (already installed).

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterised queries only. No string formatting or f-strings in SQL.
- Passwords hashed with `werkzeug.security.generate_password_hash`. Never store or log plaintext passwords.
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validation happens in the route before any database call. Do not rely on the HTML `required` attribute alone.
- Normalise the email with `.strip().lower()` before validation and before insert, so `Demo@Spendly.com` and `demo@spendly.com` are treated as the same account.
- Trim `name` with `.strip()`.
- Validation rules, checked in this order, returning the first failure:
    1. `name` is empty after stripping → `"Full name is required."`
    2. `email` is empty or has no `@` → `"Please enter a valid email address."`
    3. `password` is shorter than 8 characters → `"Password must be at least 8 characters."`
    4. Email already exists → `"An account with this email already exists."`
- On validation failure, re-render `register.html` with HTTP status 200 and the error message. Do not redirect.
- On success, redirect (HTTP 302) to `url_for('login')`. Do not log the user in automatically; that belongs to step 3.
- Do not change the existing placeholder routes (`/logout`, `/profile`, `/expenses/...`).

## Definition of done

- [ ] `GET /register` still renders the form with no errors
- [ ] Submitting a valid name, email, and 8+ character password redirects to `/login`
- [ ] A new row exists in `users` with the normalised (lowercased) email and a `password_hash` that starts with a werkzeug scheme prefix (for example `scrypt:` or `pbkdf2:`), not the plaintext password
- [ ] The stored password can be verified with `check_password_hash` and the entered password
- [ ] Submitting an empty name shows "Full name is required." and keeps the email value in the field
- [ ] Submitting an email without `@` shows "Please enter a valid email address."
- [ ] Submitting a password shorter than 8 characters shows "Password must be at least 8 characters."
- [ ] Submitting `demo@spendly.com` (the seeded demo user) shows "An account with this email already exists." and creates no new row
- [ ] Submitting `DEMO@spendly.com` with different casing is also rejected as a duplicate
- [ ] Failed submissions do not clear the name and email fields, and the password field is empty
- [ ] The page renders correctly at phone width (16px side gutter, no horizontal scroll), using the existing `auth-*` and `form-*` styles
- [ ] `uv run python app.py` starts without errors and the registration flow works end to end on http://localhost:8080/register
