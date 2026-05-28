import hashlib
import os
import sqlite3
from datetime import date


DB_NAME = "expense_tracker.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('Expense', 'Income')),
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def create_user(username: str, password: str) -> int:
    salt = os.urandom(16).hex()
    password_hash = _hash_password(password, salt)
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username.strip(), password_hash, salt),
        )
        return cursor.lastrowid


def authenticate_user(username: str, password: str):
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, username, password_hash, salt FROM users WHERE username = ?",
            (username.strip(),),
        )
        row = cursor.fetchone()

    if not row:
        return None

    user_id, saved_username, saved_hash, salt = row
    if _hash_password(password, salt) != saved_hash:
        return None

    return {"id": user_id, "username": saved_username}


def add_transaction(user_id: int, transaction_type: str, category: str, amount: float, entry_date: str, description: str):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO expenses (user_id, type, category, amount, date, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, transaction_type, category, amount, entry_date, description),
        )


def update_transaction(transaction_id: int, transaction_type: str, category: str, amount: float, entry_date: str, description: str):
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE expenses
            SET type = ?, category = ?, amount = ?, date = ?, description = ?
            WHERE id = ?
            """,
            (transaction_type, category, amount, entry_date, description, transaction_id),
        )


def delete_transaction(transaction_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM expenses WHERE id = ?", (transaction_id,))


def list_transactions(user_id: int, search: str = ""):
    pattern = f"%{search.strip()}%"
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, type, category, amount, date, COALESCE(description, '')
            FROM expenses
            WHERE user_id = ?
              AND (category LIKE ? OR description LIKE ? OR date LIKE ? OR type LIKE ?)
            ORDER BY date DESC, id DESC
            """,
            (user_id, pattern, pattern, pattern, pattern),
        )
        return cursor.fetchall()


def dashboard_summary(user_id: int):
    current_month = date.today().strftime("%Y-%m")
    with get_connection() as conn:
        total_expense = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ? AND type = 'Expense'",
            (user_id,),
        ).fetchone()[0]
        total_income = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ? AND type = 'Income'",
            (user_id,),
        ).fetchone()[0]
        monthly_spending = conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM expenses
            WHERE user_id = ? AND type = 'Expense' AND substr(date, 1, 7) = ?
            """,
            (user_id, current_month),
        ).fetchone()[0]
        categories = conn.execute(
            """
            SELECT category, COALESCE(SUM(amount), 0)
            FROM expenses
            WHERE user_id = ? AND type = 'Expense'
            GROUP BY category
            ORDER BY 2 DESC
            """,
            (user_id,),
        ).fetchall()

    return {
        "total_expense": total_expense,
        "total_income": total_income,
        "balance": total_income - total_expense,
        "monthly_spending": monthly_spending,
        "categories": categories,
    }
