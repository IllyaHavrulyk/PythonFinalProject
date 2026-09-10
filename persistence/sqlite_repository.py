import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path

from constants import EXPENSE_CATEGORIES
from domain.balance import Balance
from domain.balance_snapshot import BalanceSnapshot
from domain.category import Category
from domain.expense import Expense
from domain.income import Income

class SQLiteBalanceRepository:
    def __init__(self, database_path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    @contextmanager
    def _connection(self):
        connection = sqlite3.connect(self.database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize_database(self):
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS app_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    initial_balance REAL NOT NULL,
                    current_balance REAL NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS categories (
                    name TEXT PRIMARY KEY,
                    description TEXT NOT NULL DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    occurred_on TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL CHECK (amount > 0),
                    FOREIGN KEY (category) REFERENCES categories(name)
                );

                CREATE TABLE IF NOT EXISTS incomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    occurred_on TEXT NOT NULL,
                    amount REAL NOT NULL CHECK (amount > 0)
                );

                CREATE TABLE IF NOT EXISTS balance_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    occurred_at TEXT NOT NULL,
                    value REAL NOT NULL
                );
                """
            )
            connection.executemany(
                "INSERT OR IGNORE INTO categories (name) VALUES (?)",
                [(category,) for category in EXPENSE_CATEGORIES],
            )

    def create_balance(self, value, created_at=None):
        created_at = created_at or datetime.now()
        snapshot = BalanceSnapshot(created_at, value)
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO app_state (id, initial_balance, current_balance, created_at)
                VALUES (1, ?, ?, ?)
                """,
                (value, value, created_at.isoformat()),
            )
            connection.execute(
                "INSERT INTO balance_snapshots (occurred_at, value) VALUES (?, ?)",
                (created_at.isoformat(), value),
            )
        return Balance(value, repository=self, value_snapshots=[snapshot])

    def clear_financial_data(self):
        with self._connection() as connection:
            connection.execute("DELETE FROM balance_snapshots")
            connection.execute("DELETE FROM expenses")
            connection.execute("DELETE FROM incomes")
            connection.execute("DELETE FROM app_state")

    def load_balance(self):
        with self._connection() as connection:
            state = connection.execute(
                "SELECT current_balance FROM app_state WHERE id = 1"
            ).fetchone()
            if state is None:
                return None

            expenses = [
                Expense(self._parse_date(row[0]), row[1], row[2])
                for row in connection.execute(
                    "SELECT occurred_on, category, amount FROM expenses ORDER BY id"
                )
            ]
            incomes = [
                Income(self._parse_date(row[0]), row[1])
                for row in connection.execute(
                    "SELECT occurred_on, amount FROM incomes ORDER BY id"
                )
            ]
            snapshots = [
                BalanceSnapshot(datetime.fromisoformat(row[0]), row[1])
                for row in connection.execute(
                    "SELECT occurred_at, value FROM balance_snapshots ORDER BY id"
                )
            ]

        return Balance(
            state[0],
            repository=self,
            expenses=expenses,
            incomes=incomes,
            value_snapshots=snapshots,
        )

    def save_expense(self, expense, new_balance, snapshot):
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO expenses (occurred_on, category, amount) VALUES (?, ?, ?)",
                (expense.date.isoformat(), expense.category, expense.amount),
            )
            self._save_balance_change(connection, new_balance, snapshot)

    def save_income(self, income, new_balance, snapshot):
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO incomes (occurred_on, amount) VALUES (?, ?)",
                (income.date.isoformat(), income.amount),
            )
            self._save_balance_change(connection, new_balance, snapshot)

    def load_categories(self):
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT name, description FROM categories ORDER BY rowid"
            ).fetchall()
        return [Category(name, description) for name, description in rows]

    @staticmethod
    def _save_balance_change(connection, new_balance, snapshot):
        connection.execute(
            "UPDATE app_state SET current_balance = ? WHERE id = 1",
            (new_balance,),
        )
        connection.execute(
            "INSERT INTO balance_snapshots (occurred_at, value) VALUES (?, ?)",
            (snapshot.date.isoformat(), snapshot.value),
        )

    @staticmethod
    def _parse_date(value):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return datetime.fromisoformat(value).date()
