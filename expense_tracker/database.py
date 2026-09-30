import sqlite3
from datetime import date
from pathlib import Path

DEFAULT_DB = Path.home() / ".expense_tracker.db"


class ExpenseDB:
    def __init__(self, path=DEFAULT_DB):
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount_cents INTEGER NOT NULL,
                category TEXT NOT NULL,
                note TEXT DEFAULT '',
                spent_on TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def add(self, amount, category, note="", spent_on=None):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        spent_on = spent_on or date.today().isoformat()
        date.fromisoformat(spent_on)  # raises ValueError if the date is invalid
        cursor = self.conn.execute(
            "INSERT INTO expenses (amount_cents, category, note, spent_on) "
            "VALUES (?, ?, ?, ?)",
            (round(amount * 100), category.lower(), note, spent_on),
        )
        self.conn.commit()
        return cursor.lastrowid

    def list(self, category=None, month=None):
        query = "SELECT * FROM expenses WHERE 1=1"
        params = []
        if category:
            query += " AND category = ?"
            params.append(category.lower())
        if month:
            query += " AND spent_on LIKE ?"
            params.append(f"{month}%")
        query += " ORDER BY spent_on DESC, id DESC"
        return self.conn.execute(query, params).fetchall()

    def delete(self, expense_id):
        cursor = self.conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def summary(self, month=None):
        query = "SELECT category, SUM(amount_cents) AS total FROM expenses"
        params = []
        if month:
            query += " WHERE spent_on LIKE ?"
            params.append(f"{month}%")
        query += " GROUP BY category ORDER BY total DESC"
        return [(r["category"], r["total"]) for r in self.conn.execute(query, params)]

    def close(self):
        self.conn.close()