import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import date
from decimal import Decimal
from pathlib import Path

from persistence.sqlite_repository import SQLiteBalanceRepository
from services.finance_service import FinanceService


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temporary_directory.name) / "test.db"
        self.repository = SQLiteBalanceRepository(database_path)
        self.service = FinanceService(self.repository)
        self.service.initialize("dev", False, "100.10")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_round_trip_preserves_exact_money_values(self):
        self.service.add_income("0.20", date(2026, 9, 10))
        self.service.add_expense("0.10", "Їжа", date(2026, 9, 11))

        loaded = self.repository.load_balance()

        self.assertEqual(loaded.get_value(), Decimal("100.20"))
        self.assertEqual(loaded.get_incomes()[0].amount, Decimal("0.20"))
        self.assertEqual(loaded.get_expenses()[0].amount, Decimal("0.10"))
        self.assertTrue(all(type(item.date) is date for item in loaded.get_value_snapshots()))

    def test_database_stores_integer_kopecks(self):
        with closing(sqlite3.connect(self.repository.database_path)) as connection:
            current_balance = connection.execute(
                "SELECT current_balance FROM app_state WHERE id = 1"
            ).fetchone()[0]

        self.assertEqual(current_balance, 10010)

    def test_legacy_real_values_are_migrated_to_kopecks(self):
        legacy_path = Path(self.temporary_directory.name) / "legacy.db"
        with closing(sqlite3.connect(legacy_path)) as connection:
            connection.executescript(
                """
                CREATE TABLE app_state (
                    id INTEGER PRIMARY KEY,
                    initial_balance REAL NOT NULL,
                    current_balance REAL NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE categories (name TEXT PRIMARY KEY, description TEXT NOT NULL DEFAULT '');
                CREATE TABLE expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    occurred_on TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL
                );
                CREATE TABLE incomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    occurred_on TEXT NOT NULL,
                    amount REAL NOT NULL
                );
                CREATE TABLE balance_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    occurred_at TEXT NOT NULL,
                    value REAL NOT NULL
                );
                INSERT INTO app_state VALUES (1, 10.10, 10.20, '2026-09-11');
                INSERT INTO incomes (occurred_on, amount) VALUES ('2026-09-11', 0.10);
                INSERT INTO balance_snapshots (occurred_at, value) VALUES ('2026-09-11', 10.20);
                """
            )
            connection.commit()

        migrated = SQLiteBalanceRepository(legacy_path).load_balance()

        self.assertEqual(migrated.get_value(), Decimal("10.20"))
        self.assertEqual(migrated.get_incomes()[0].amount, Decimal("0.10"))


if __name__ == "__main__":
    unittest.main()
