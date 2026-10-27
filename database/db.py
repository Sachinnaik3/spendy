import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "spendly.db"
)

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                email         TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at    TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id),
                amount      REAL NOT NULL,
                category    TEXT NOT NULL,
                date        TEXT NOT NULL,
                description TEXT,
                created_at  TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
    finally:
        conn.close()


def create_user(name, email, password):
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_db()
    try:
        return conn.execute(
            "SELECT id, name, email, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_db()
    try:
        return conn.execute(
            "SELECT id, name, email, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()


def get_expense_summary(user_id):
    conn = get_db()
    try:
        return conn.execute(
            "SELECT COUNT(*) AS expense_count, "
            "COALESCE(SUM(amount), 0) AS total, "
            "COUNT(DISTINCT category) AS category_count "
            "FROM expenses WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()


def seed_db():
    conn = get_db()
    try:
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if count > 0:
            return

        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
        )
        user_id = cursor.lastrowid

        # One expense per category, plus one extra Food entry for 8 total.
        # Days are spread from the 1st up to today so no date is in the future.
        today = date.today()
        sample = [
            (12.50, "Food", "Lunch at the canteen"),
            (40.00, "Transport", "Monthly bus pass"),
            (85.00, "Bills", "Electricity bill"),
            (25.00, "Health", "Pharmacy visit"),
            (30.00, "Entertainment", "Movie tickets"),
            (60.00, "Shopping", "New shoes"),
            (8.00, "Other", "Stationery"),
            (18.75, "Food", "Groceries"),
        ]
        rows = []
        for i, (amount, category, description) in enumerate(sample):
            day = 1 + round(i * (today.day - 1) / (len(sample) - 1))
            expense_date = today.replace(day=day).isoformat()
            rows.append((user_id, amount, category, expense_date, description))

        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
