import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from constants import EXPENSE_CATEGORIES, KOPECKS_PER_HRYVNIA
from domain.balance import Balance
from domain.balance_snapshot import BalanceSnapshot
from domain.category import Category
from domain.expense import Expense
from domain.income import Income
from domain.money import to_money


MONEY_STORAGE_VERSION = "2"

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
                    initial_balance INTEGER NOT NULL,
                    current_balance INTEGER NOT NULL,
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
                    amount INTEGER NOT NULL CHECK (amount > 0),
                    FOREIGN KEY (category) REFERENCES categories(name)
                );

                CREATE TABLE IF NOT EXISTS incomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    occurred_on TEXT NOT NULL,
                    amount INTEGER NOT NULL CHECK (amount > 0)
                );

                CREATE TABLE IF NOT EXISTS balance_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    occurred_at TEXT NOT NULL,
                    value INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS schema_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )
            connection.executemany(
                "INSERT OR IGNORE INTO categories (name) VALUES (?)",
                [(category,) for category in EXPENSE_CATEGORIES],
            )
            self._migrate_money_storage(connection)

    @staticmethod
    def _migrate_money_storage(connection):
        """Convert databases created before lection9 from units to integer kopecks."""
        version = connection.execute(
            "SELECT value FROM schema_metadata WHERE key = 'money_storage_version'"
        ).fetchone()
        if version is not None:
            return

        connection.execute(
            "UPDATE app_state SET initial_balance = ROUND(initial_balance * 100), "
            "current_balance = ROUND(current_balance * 100)"
        )
        connection.execute("UPDATE expenses SET amount = ROUND(amount * 100)")
        connection.execute("UPDATE incomes SET amount = ROUND(amount * 100)")
        connection.execute("UPDATE balance_snapshots SET value = ROUND(value * 100)")
        connection.execute(
            "INSERT INTO schema_metadata (key, value) VALUES (?, ?)",
            ("money_storage_version", MONEY_STORAGE_VERSION),
        )

    def create_balance(self, value, created_at=None):
        value = to_money(value)
        created_at = created_at or date.today()
        snapshot = BalanceSnapshot(created_at, value)
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO app_state (id, initial_balance, current_balance, created_at)
                VALUES (1, ?, ?, ?)
                """,
                (self._to_cents(value), self._to_cents(value), snapshot.date.isoformat()),
            )
            connection.execute(
                "INSERT INTO balance_snapshots (occurred_at, value) VALUES (?, ?)",
                (snapshot.date.isoformat(), self._to_cents(value)),
            )
        return Balance(value, value_snapshots=[snapshot])

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
                Expense(self._parse_date(row[0]), row[1], self._from_cents(row[2]))
                for row in connection.execute(
                    "SELECT occurred_on, category, amount FROM expenses ORDER BY id"
                )
            ]
            incomes = [
                Income(self._parse_date(row[0]), self._from_cents(row[1]))
                for row in connection.execute(
                    "SELECT occurred_on, amount FROM incomes ORDER BY id"
                )
            ]
            snapshots = [
                BalanceSnapshot(self._parse_date(row[0]), self._from_cents(row[1]))
                for row in connection.execute(
                    "SELECT occurred_at, value FROM balance_snapshots ORDER BY id"
                )
            ]

        return Balance(
            self._from_cents(state[0]),
            expenses=expenses,
            incomes=incomes,
            value_snapshots=snapshots,
        )

    def save_expense(self, expense, new_balance, snapshot):
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO expenses (occurred_on, category, amount) VALUES (?, ?, ?)",
                (expense.date.isoformat(), expense.category, self._to_cents(expense.amount)),
            )
            self._save_balance_change(connection, new_balance, snapshot)

    def save_income(self, income, new_balance, snapshot):
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO incomes (occurred_on, amount) VALUES (?, ?)",
                (income.date.isoformat(), self._to_cents(income.amount)),
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
            (SQLiteBalanceRepository._to_cents(new_balance),),
        )
        connection.execute(
            "INSERT INTO balance_snapshots (occurred_at, value) VALUES (?, ?)",
            (snapshot.date.isoformat(), SQLiteBalanceRepository._to_cents(snapshot.value)),
        )

    @staticmethod
    def _parse_date(value):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return datetime.fromisoformat(value).date()

    @staticmethod
    def _to_cents(value) -> int:
        return int(to_money(value) * KOPECKS_PER_HRYVNIA)

    @staticmethod
    def _from_cents(value) -> Decimal:
        return (
            Decimal(int(round(value))) / Decimal(KOPECKS_PER_HRYVNIA)
        ).quantize(Decimal("0.01"))
