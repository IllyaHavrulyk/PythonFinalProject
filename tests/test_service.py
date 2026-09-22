import sqlite3
import unittest
from datetime import date
from decimal import Decimal

from constants import APP_MODE_DEV, APP_MODE_TEST, EXPENSE_CATEGORIES
from domain.balance import Balance
from services.finance_service import FinanceService
from tests.support import TemporaryDatabaseTestCase


class FailingRepository:
    """Loads fine, but refuses to persist anything."""

    def __init__(self):
        self.stored_balance = Balance("100.00")

    def load_balance(self):
        return self.stored_balance

    def save_expense(self, expense, new_balance, snapshot):
        raise sqlite3.OperationalError("simulated database failure")

    def save_income(self, income, new_balance, snapshot):
        raise sqlite3.OperationalError("simulated database failure")

    def load_categories(self):
        return []


class InitializeTests(TemporaryDatabaseTestCase):
    def test_a_first_dev_run_without_a_starting_value_has_no_balance_yet(self):
        self.assertIsNone(self.service.initialize(APP_MODE_DEV, False))

    def test_a_first_dev_run_creates_the_balance_it_is_given(self):
        balance = self.service.initialize(APP_MODE_DEV, False, "250.50")

        self.assertEqual(balance.get_value(), Decimal("250.50"))
        self.assertEqual(self.repository.load_balance().get_value(), Decimal("250.50"))

    def test_an_opening_balance_of_zero_is_accepted(self):
        self.assertEqual(self.service.initialize(APP_MODE_DEV, False, 0).get_value(), Decimal("0.00"))

    def test_a_negative_opening_balance_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.initialize(APP_MODE_DEV, False, "-1.00")

    def test_a_later_dev_run_restores_the_stored_balance(self):
        self.service.initialize(APP_MODE_DEV, False, "250.50")

        restored = FinanceService(self.repository).initialize(APP_MODE_DEV, False)

        self.assertEqual(restored.get_value(), Decimal("250.50"))

    def test_a_stored_balance_is_not_overwritten_by_a_starting_value(self):
        self.service.initialize(APP_MODE_DEV, False, "250.50")

        restored = FinanceService(self.repository).initialize(APP_MODE_DEV, False, "999.00")

        self.assertEqual(restored.get_value(), Decimal("250.50"))

    def test_test_mode_seeds_demo_data(self):
        balance = self.service.initialize(APP_MODE_TEST, False)

        self.assertGreater(len(balance.get_expenses()), 0)

    def test_test_mode_reseeds_when_asked(self):
        first = self.service.initialize(APP_MODE_TEST, False)

        second = FinanceService(self.repository).initialize(APP_MODE_TEST, True)

        self.assertEqual(second.get_value(), first.get_value())
        self.assertEqual(len(second.get_expenses()), len(first.get_expenses()))

    def test_test_mode_keeps_existing_data_when_reset_is_off(self):
        self.service.initialize(APP_MODE_TEST, False)
        self.service.add_income("1000.00")
        expected = self.service.balance.get_value()

        restored = FinanceService(self.repository).initialize(APP_MODE_TEST, False)

        self.assertEqual(restored.get_value(), expected)


class BalancePropertyTests(TemporaryDatabaseTestCase):
    def test_reading_the_balance_before_initialising_is_an_error(self):
        with self.assertRaises(RuntimeError):
            self.service.balance

    def test_the_balance_is_available_once_initialised(self):
        self.service.initialize(APP_MODE_DEV, False, "10.00")

        self.assertEqual(self.service.balance.get_value(), Decimal("10.00"))


class TransactionTests(TemporaryDatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.service.initialize(APP_MODE_DEV, False, "100.00")

    def test_adding_an_expense_updates_memory_and_storage(self):
        expense = self.service.add_expense("25.50", "Їжа")

        self.assertEqual(expense.amount, Decimal("25.50"))
        self.assertEqual(self.service.balance.get_value(), Decimal("74.50"))
        self.assertEqual(self.repository.load_balance().get_value(), Decimal("74.50"))

    def test_adding_an_income_updates_memory_and_storage(self):
        income = self.service.add_income("25.50")

        self.assertEqual(income.amount, Decimal("25.50"))
        self.assertEqual(self.service.balance.get_value(), Decimal("125.50"))
        self.assertEqual(self.repository.load_balance().get_value(), Decimal("125.50"))

    def test_transactions_default_to_today(self):
        self.assertEqual(self.service.add_income("1.00").date, date.today())

    def test_an_explicit_date_is_honoured(self):
        expense = self.service.add_expense("1.00", "Їжа", date(2026, 1, 31))

        self.assertEqual(expense.date, date(2026, 1, 31))

    def test_an_invalid_amount_is_rejected_before_anything_is_stored(self):
        with self.assertRaises(ValueError):
            self.service.add_expense("0", "Їжа")

        self.assertEqual(self.service.balance.get_value(), Decimal("100.00"))
        self.assertEqual(self.service.balance.get_expenses(), ())

    def test_categories_come_from_the_repository(self):
        self.assertEqual(self.service.get_categories(), EXPENSE_CATEGORIES)

    def test_transactions_are_counted_across_both_kinds(self):
        self.assertEqual(self.service.count_transactions(), 0)

        self.service.add_income("5.00")
        self.service.add_expense("1.00", "Їжа")

        self.assertEqual(self.service.count_transactions(), 2)


class PersistenceFailureTests(unittest.TestCase):
    def setUp(self):
        self.service = FinanceService(FailingRepository())
        self.service.initialize(APP_MODE_DEV, False)

    def test_a_failed_expense_save_leaves_the_in_memory_balance_alone(self):
        with self.assertRaises(sqlite3.OperationalError):
            self.service.add_expense("10.00", "Їжа")

        self.assertEqual(self.service.balance.get_value(), Decimal("100.00"))
        self.assertEqual(self.service.balance.get_expenses(), ())

    def test_a_failed_income_save_leaves_the_in_memory_balance_alone(self):
        with self.assertRaises(sqlite3.OperationalError):
            self.service.add_income("10.00")

        self.assertEqual(self.service.balance.get_value(), Decimal("100.00"))
        self.assertEqual(self.service.balance.get_incomes(), ())


if __name__ == "__main__":
    unittest.main()
