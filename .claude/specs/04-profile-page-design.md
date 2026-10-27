# Spec: Profile Page Design

## Overview

Replace the `/profile` placeholder with a real, logged-in profile page that shows who the user is and a short summary of their spending. The page shows the user's name, email, and the date they joined, along with a small stats block (number of expenses, total amount spent, and number of categories used) computed from the `expenses` table. This gives the signed-in user a first real page to land on after logging in, and establishes the layout, card styles, and logged-in access check that later steps (add, edit, and delete expense) will build on. It is step 4 of the Spendly roadmap. It depends on login (step 3), because the page reads the user id from the session. Adding or editing expenses is out of scope here; the stats reflect whatever rows already exist, such as the seeded demo data.

## Depends on

- **Step 1 — Database setup.** Requires the `users` and `expenses` tables, `get_db()`, and `init_db()` from `database/db.py`.
- **Step 2 — Registration.** Requires users with `name`, `email`, and `created_at` values.
- **Step 3 — Login and logout.** Requires `session["user_id"]` to be set on login and cleared on logout, and the `login()` redirect to `url_for('profile')`.

## Routes

- `GET /profile` — render the profile page for the logged-in user (name, email, member since, and expense stats). If there is no `user_id` in the session, redirect (HTTP 302) to `url_for('login')` — logged-in

No new routes. The existing `/profile` route is replaced with a real view.

## Database changes

No database changes. The existing `users` table has `id`, `name`, `email`, and `created_at`. The `expenses` table has `user_id`, `amount`, and `category`. Verified against `database/db.py`.

Add two helper functions to `database/db.py`:

- `get_user_by_id(user_id)` — runs a parameterised `SELECT id, name, email, created_at FROM users WHERE id = ?` and returns the row as a `sqlite3.Row`, or `None` if no match. Closes the connection in a `finally` block, matching `get_user_by_email()`.
- `get_expense_summary(user_id)` — runs a parameterised query that returns `COUNT(*)`, `COALESCE(SUM(amount), 0)`, and `COUNT(DISTINCT category)` from `expenses` for that `user_id`, as a single `sqlite3.Row`. Closes the connection in a `finally` block.

## Templates

- **Create:**
    - `templates/profile.html` — extends `base.html`. Sets `title` to "Profile". Shows a header with the user's name and email, a "Member since" line formatted from `created_at`, and a three-item stats row (expense count, total spent, categories used). Uses existing tokens and classes where they fit, plus new `profile-*` classes.
- **Modify:**
    - `templates/base.html` — none required. The navbar still shows "Get started" for everyone. A logged-in navbar state is out of scope for this step.

## Files to change

- `app.py` — replace the placeholder `profile()` view with a real one that checks `session["user_id"]`, loads the user and expense summary, and renders `profile.html`. Import `get_user_by_id` and `get_expense_summary` from `database.db`.
- `database/db.py` — add `get_user_by_id()` and `get_expense_summary()`.
- `static/css/style.css` — add `profile-*` rules (page wrapper, header, stats row, stat card) under a new section comment. Use only CSS variables from `:root` for colors, radii, and fonts.

## Files to create

- `templates/profile.html`

## New dependencies

No new dependencies. Uses Flask's `session`, `redirect`, `url_for`, and `render_template`, which are already imported in `app.py`.

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterised queries only. No string formatting or f-strings in SQL.
- Passwords hashed with werkzeug. This step does not write passwords; it must never read or display `password_hash`.
- The profile view must check `session.get("user_id")` before any database call. If it is missing, redirect to `url_for('login')`. Do not rely on the template to hide content.
- If `get_user_by_id()` returns `None` (for example, the user was deleted while logged in), clear the session and redirect to `url_for('login')`.
- Format `total spent` with two decimal places in the template (`"%.2f"` or `|round(2)`). Do not hardcode a currency symbol unless the existing templates already use one.
- Format `created_at` as a short date (for example, `27 Oct 2026`). Do not show the raw timestamp string.
- Show zero values (0 expenses, 0.00 spent) without error for a user with no expenses. `COALESCE` must handle the empty case.
- Use CSS variables — never hardcode hex values. Do not copy the hard-coded colors from `landing.css`.
- Reuse the existing `:root` tokens and the `auth-*` / `form-*` / `btn-*` classes where they fit. Do not duplicate them.
- All templates extend `base.html`

## Definition of done

- [ ] Visiting `/profile` while logged out redirects to `/login`
- [ ] Logging in with `demo@spendly.com` / `demo123` lands on `/profile` (no longer shows the "coming in Step 4" text)
- [ ] The profile page shows the name "Demo User" and the email `demo@spendly.com`
- [ ] The "Member since" line shows a readable date, not a raw timestamp
- [ ] The stats row shows 8 expenses for the demo user, a total of 279.25, and 7 categories (values from the current seed data in `seed_db()`)
- [ ] Registering a new user, logging in, and visiting `/profile` shows 0 expenses, 0.00 spent, and 0 categories without an error
- [ ] Logging out and then visiting `/profile` redirects to `/login`
- [ ] Stats for one user do not include expenses that belong to another user (verify by logging in as a newly registered user and confirming their counts are 0)
- [ ] The profile page does not display the password hash or any password value anywhere in the HTML
- [ ] The page renders correctly at phone width (16px side gutter, no horizontal scroll)
- [ ] No hex color values were added to `templates/profile.html` or to the new `profile-*` rules in `style.css`
- [ ] `uv run python app.py` starts without errors, and the login → profile → logout flow works end to end on http://localhost:8080
