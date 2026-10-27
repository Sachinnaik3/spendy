# Plan: Profile Page (Step 4) — revised with updated frontend-design skill

## Context

`/profile` is still a placeholder ("Profile page — coming in Step 4"). Login (step 3) already redirects there. This step replaces it with a logged-in page showing the user's name, email, join date, and an expense summary.

Sources: `.claude/specs/04-profile-page-design.md` (branch `feature/profile-page-design`), `CLAUDE.md`, the updated `spendly-ui-designer` skill, and the existing `static/css/style.css`, `templates/base.html`, and `templates/login.html`.

## Where the skill and the project disagree

The project rules win over the skill's generic defaults:

| Skill default | Decision | Why |
|---|---|---|
| Hex palette (`#F7F8FA`, `#6366F1`, etc.) | Use existing `:root` tokens only | Spec and CLAUDE.md say never hardcode hex. Existing tokens already cover the palette. |
| Inter font | Keep `--font-body` (DM Sans) and `--font-display` (DM Serif Display) | Already loaded in `base.html`. Adding Inter would be a second font family. |
| Lucide icons via CDN in `base.html` | No icons | Would modify `base.html`, which the spec leaves untouched, and add a CDN dependency. Existing auth and landing pages have no icons. |
| Generic classes (`.card`, `.btn`, `.input`) | Project prefixes: `profile-*`, plus existing `btn-ghost` | Matches the scoped-prefix pattern and avoids clashes. |
| Card shadow | Border only (`--border`) | Matches `auth-card`. The skill allows borders instead of shadows. |
| 8px grid | Existing `rem` values (0.5, 0.75, 1, 1.25, 1.5, 2rem) | Each lands on a multiple of 4px at 16px root, so it fits the grid. |

Kept from the skill: one restrained accent, `tabular-nums` on amounts, a label-above-value stats pattern, stacked cards on narrow screens, and a scoped class prefix.

## UI plan

- **Layout:** centered single column. Container max-width 720px, `legal-section`-style padding (`3rem 1rem`). Stacks cleanly on phones with no horizontal scroll.
- **Header card:** initial avatar in an `--accent-light` circle with `--accent` text, name in `--font-display`, email in `--ink-muted`, "Member since <date>" below. A `btn-ghost` "Sign out" link to `url_for('logout')` sits on the right, and wraps below the name on narrow screens.
- **Stats row:** three equal cards in a grid. Each has an uppercase muted label (Expenses, Total spent, Categories) above a `--font-display` value. Amounts use `font-variant-numeric: tabular-nums` and two decimals. The row goes to one column under 600px.
- **Assumption (stated up front):** the page is read-only. There are no edit controls, no tables, and no charts.

## Files

| File | Change |
|---|---|
| `app.py` | Replace the `profile()` placeholder. Import `get_user_by_id`, `get_expense_summary`, `datetime`. |
| `database/db.py` | Add `get_user_by_id()` and `get_expense_summary()`. |
| `templates/profile.html` | **New.** Extends `base.html`. |
| `static/css/style.css` | Add a `Profile page` section between Auth pages and Legal pages. |

No new dependencies. `base.html`, `login.html`, and `landing.css` are not modified.

## Backend

- `profile()`: `user_id = session.get("user_id")`. If missing, redirect to `url_for('login')` before any DB call.
- `get_user_by_id(user_id)`: copy the shape of `get_user_by_email()`. Parameterised `SELECT id, name, email, created_at FROM users WHERE id = ?`, `fetchone()`, `finally: conn.close()`.
- If the user is `None`, call `session.clear()` and redirect to login.
- `get_expense_summary(user_id)`: one parameterised query, `COUNT(*)`, `COALESCE(SUM(amount), 0)`, `COUNT(DISTINCT category)`, `WHERE user_id = ?`. Returns one `sqlite3.Row`.
- Format `created_at` in the view: `datetime.strptime(value, "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y")`. SQLite stores UTC from `datetime('now')`.

## Template sketch (`templates/profile.html`)

```jinja
{% extends "base.html" %}
{% block title %}Profile — Spendly{% endblock %}
{% block content %}
<section class="profile-section">
  <div class="profile-container">

    <header class="profile-card profile-header">
      <div class="profile-avatar">{{ user.name[:1]|upper }}</div>
      <div class="profile-identity">
        <h1 class="profile-name">{{ user.name }}</h1>
        <p class="profile-email">{{ user.email }}</p>
        <p class="profile-meta">Member since {{ joined }}</p>
      </div>
      <a href="{{ url_for('logout') }}" class="btn-ghost">Sign out</a>
    </header>

    <div class="profile-stats">
      <div class="profile-card profile-stat">
        <span class="profile-stat-label">Expenses</span>
        <span class="profile-stat-value">{{ summary.count }}</span>
      </div>
      <div class="profile-card profile-stat">
        <span class="profile-stat-label">Total spent</span>
        <span class="profile-stat-value">{{ "%.2f"|format(summary.total) }}</span>
      </div>
      <div class="profile-card profile-stat">
        <span class="profile-stat-label">Categories</span>
        <span class="profile-stat-value">{{ summary.categories }}</span>
      </div>
    </div>

  </div>
</section>
{% endblock %}
```

No hex values, no inline `style=`. The `summary` and `user` names are placeholders to match the view's variables.

## CSS sketch (`static/css/style.css`, new `Profile page` section)

Token mapping: surfaces `--paper-card`, borders `--border`, radius `--radius-md`, muted text `--ink-muted`, values `--ink`, accent `--accent` / `--accent-light`, display font `--font-display`.

- `.profile-section`: `padding: 3rem 1rem;` (mirrors `.legal-section`)
- `.profile-container`: `max-width: 720px; margin: 0 auto; display: flex; flex-direction: column; gap: 1.5rem;`
- `.profile-card`: `background: var(--paper-card); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.5rem;`
- `.profile-header`: flex row, `align-items: center; gap: 1.25rem; flex-wrap: wrap;`, with `.btn-ghost` pushed right via `margin-left: auto`
- `.profile-avatar`: 56px circle, `background: var(--accent-light); color: var(--accent); font-family: var(--font-display); display: grid; place-items: center;`
- `.profile-name`: `font-family: var(--font-display); font-size: 1.75rem; color: var(--ink);`
- `.profile-email`, `.profile-meta`: `color: var(--ink-muted); font-size: 0.9rem;`
- `.profile-stats`: `display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;`
- `.profile-stat`: flex column, `gap: 0.25rem;`
- `.profile-stat-label`: uppercase, `font-size: 0.8rem; letter-spacing: 0.06em; color: var(--ink-muted);`
- `.profile-stat-value`: `font-family: var(--font-display); font-size: 1.75rem; color: var(--ink); font-variant-numeric: tabular-nums;`
- `@media (max-width: 600px)`: `.profile-stats { grid-template-columns: 1fr; }`

Sizes are multiples of 4px at 16px root: 56px avatar, 1.25rem = 20px, 1.5rem = 24px.

## Verification

1. `uv run python app.py` starts cleanly. Open http://localhost:8080.
2. **Logged out:** `/profile` returns 302 to `/login`.
3. **Demo user** (`demo@spendly.com` / `demo123`): name "Demo User", email, readable join date, stats of 8 / 279.25 / 7.
4. **New user:** register, log in, see 0 / 0.00 / 0 with no error.
5. **Isolation:** new user's stats do not include demo expenses.
6. **Sign out:** the button goes to `/logout`, then `/profile` redirects to `/login`.
7. **Security:** page source contains no `password_hash` and no password text.
8. **Responsive:** at 375px, no horizontal scroll, 16px gutter, stats stack to one column.
9. **Hex audit:** `Grep` `#[0-9a-fA-F]{3,6}` over `templates/profile.html` and the `Profile page` CSS block. Expect no matches.
10. **Token audit:** every colour in the new CSS is a `var(--...)`.
11. **Amounts:** total shows two decimals and digits align (tabular-nums) when compared across users.

Verification is manual. `tests/` does not exist yet, and adding a pytest file is out of scope unless requested.

## Decisions carried over

- Sign out button in the header (added beyond the spec, approved earlier).
- Navbar unchanged in this step.
- Stats block kept.
- No icons (new, follows from the conflicts table above; confirm if you want Lucide added later).
