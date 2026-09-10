import sqlite3
import unittest

from constants import APP_MODE_DEV
from domain.balance import Balance
from services.finance_service import FinanceService


class FailingRepository:
    def __init__(self):
        self.stored_balance = Balance("100.00")

    def load_balance(self):
        return self.stored_balance

    def save_expense(self, expense, new_balance, snapshot):
        raise sqlite3.OperationalError("simulated database failure")

    def load_categories(self):
        return []


class FinanceServiceTests(unittest.TestCase):
    def test_failed_save_does_not_change_in_memory_balance(self):
        service = FinanceService(FailingRepository())
        service.initialize(APP_MODE_DEV, False)

        with self.assertRaises(sqlite3.OperationalError):
            service.add_expense("10.00", "Їжа")

        self.assertEqual(str(service.balance.get_value()), "100.00")
        self.assertEqual(service.balance.get_expenses(), ())


if __name__ == "__main__":
    unittest.main()
