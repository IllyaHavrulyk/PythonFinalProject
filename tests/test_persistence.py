import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from constants import EXPENSE_CATEGORIES
from domain.balance_snapshot import BalanceSnapshot
from domain.expense import Expense
from domain.income import Income
from persistence.sqlite_repository import MONEY_STORAGE_VERSION, SQLiteBalanceRepository
from tests.support import TemporaryDatabaseTestCase


class RepositorySetupTests(TemporaryDatabaseTestCase):
    def test_creates_missing_parent_directories(self):
        nested = self.directory / "a" / "b" / "nested.db"

        SQLiteBalanceRepository(nested)

        self.assertTrue(nested.exists())

    def test_seeds_the_default_categories(self):
        names = [category.name for category in self.repository.load_categories()]

        self.assertEqual(names, EXPENSE_CATEGORIES)

    def test_opening_the_same_database_twice_does_not_duplicate_categories(self):
        SQLiteBalanceRepository(self.directory / "test.db")

        self.assertEqual(len(self.repository.load_categories()), len(EXPENSE_CATEGORIES))

    def test_records_the_money_storage_version(self):
        with closing(sqlite3.connect(self.repository.database_path)) as connection:
            stored = connection.execute(
                "SELECT value FROM schema_metadata WHERE key = 'money_storage_version'"
            ).fetchone()

        self.assertEqual(stored[0], MONEY_STORAGE_VERSION)


class BalanceLifecycleTests(TemporaryDatabaseTestCase):
    def test_load_balance_is_none_before_anything_is_created(self):
        self.assertIsNone(self.repository.load_balance())

    def test_create_balance_stores_state_and_an_opening_snapshot(self):
        balance = self.repository.create_balance("100.10")

        self.assertEqual(balance.get_value(), Decimal("100.10"))
        reloaded = self.repository.load_balance()
        self.assertEqual(reloaded.get_value(), Decimal("100.10"))
        self.assertEqual(len(reloaded.get_value_snapshots()), 1)

    def test_create_balance_accepts_an_explicit_creation_date(self):
        self.repository.create_balance("50.00", created_at=datetime(2026, 1, 5, 9, 30))

        snapshot = self.repository.load_balance().get_value_snapshots()[0]
        self.assertEqual(snapshot.date, date(2026, 1, 5))

    def test_money_is_stored_as_integer_kopecks(self):
        self.repository.create_balance("100.10")

        with closing(sqlite3.connect(self.repository.database_path)) as connection:
            stored = connection.execute(
                "SELECT current_balance, typeof(current_balance) FROM app_state WHERE id = 1"
            ).fetchone()

        self.assertEqual(stored[0], 10010)
        self.assertEqual(stored[1], "integer")

    def test_round_trip_preserves_exact_money_and_plain_dates(self):
        balance = self.repository.create_balance("100.10")
        expense = Expense(date(2026, 9, 11), "Їжа", "0.10")
        income = Income(date(2026, 9, 10), "0.20")
        self.repository.save_income(income, Decimal("100.30"), BalanceSnapshot(income.date, "100.30"))
        self.repository.save_expense(expense, Decimal("100.20"), BalanceSnapshot(expense.date, "100.20"))

        loaded = self.repository.load_balance()

        self.assertEqual(loaded.get_value(), Decimal("100.20"))
        self.assertEqual(loaded.get_incomes()[0].amount, Decimal("0.20"))
        self.assertEqual(loaded.get_expenses()[0].amount, Decimal("0.10"))
        self.assertEqual(loaded.get_expenses()[0].category, "Їжа")
        self.assertTrue(all(type(item.date) is date for item in loaded.get_value_snapshots()))
        self.assertEqual(balance.get_value(), Decimal("100.10"), "in-memory object is untouched")

    def test_clear_financial_data_empties_money_tables_but_keeps_categories(self):
        self.repository.create_balance("100.00")
        income = Income(date.today(), "5.00")
        self.repository.save_income(income, Decimal("105.00"), BalanceSnapshot(income.date, "105.00"))

        self.repository.clear_financial_data()

        self.assertIsNone(self.repository.load_balance())
        self.assertEqual(len(self.repository.load_categories()), len(EXPENSE_CATEGORIES))


class SchemaConstraintTests(TemporaryDatabaseTestCase):
    def test_an_expense_in_an_unknown_category_is_rejected(self):
        self.repository.create_balance("100.00")

        with closing(sqlite3.connect(self.repository.database_path)) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO expenses (occurred_on, category, amount) VALUES (?, ?, ?)",
                    ("2026-09-11", "Не існує", 100),
                )

    def test_a_non_positive_amount_is_rejected(self):
        with closing(sqlite3.connect(self.repository.database_path)) as connection:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO incomes (occurred_on, amount) VALUES (?, ?)",
                    ("2026-09-11", 0),
                )

    def test_only_one_app_state_row_can_exist(self):
        self.repository.create_balance("100.00")

        with closing(sqlite3.connect(self.repository.database_path)) as connection:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO app_state (id, initial_balance, current_balance, created_at)"
                    " VALUES (2, 1, 1, '2026-09-11')",
                )


class ConversionTests(unittest.TestCase):
    def test_dates_are_parsed_from_both_date_and_datetime_text(self):
        self.assertEqual(SQLiteBalanceRepository._parse_date("2026-09-11"), date(2026, 9, 11))
        self.assertEqual(
            SQLiteBalanceRepository._parse_date("2026-09-11T08:30:00"), date(2026, 9, 11),
        )

    def test_kopecks_round_trip_without_loss(self):
        for value in ("0.01", "0.10", "1.00", "1234.56", "-5.25"):
            with self.subTest(value=value):
                cents = SQLiteBalanceRepository._to_cents(value)
                self.assertIsInstance(cents, int)
                self.assertEqual(SQLiteBalanceRepository._from_cents(cents), Decimal(value))

    def test_fractional_kopecks_are_rounded_before_storage(self):
        self.assertEqual(SQLiteBalanceRepository._to_cents("1.005"), 101)


class LegacyMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.legacy_path = Path(self.temporary_directory.name) / "legacy.db"
        with closing(sqlite3.connect(self.legacy_path)) as connection:
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

    def test_legacy_real_values_are_migrated_to_kopecks(self):
        migrated = SQLiteBalanceRepository(self.legacy_path).load_balance()

        self.assertEqual(migrated.get_value(), Decimal("10.20"))
        self.assertEqual(migrated.get_incomes()[0].amount, Decimal("0.10"))

    def test_the_migration_runs_only_once(self):
        SQLiteBalanceRepository(self.legacy_path)
        SQLiteBalanceRepository(self.legacy_path)

        # A second multiplication by 100 would turn 10.20 into 1020.00.
        self.assertEqual(
            SQLiteBalanceRepository(self.legacy_path).load_balance().get_value(),
            Decimal("10.20"),
        )


if __name__ == "__main__":
    unittest.main()
