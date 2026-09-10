import unittest
from datetime import date, datetime
from decimal import Decimal

from domain.balance import Balance
from domain.balance_snapshot import BalanceSnapshot
from domain.expense import Expense
from domain.income import Income


class DomainTests(unittest.TestCase):
    def test_entities_normalize_money_and_dates(self):
        expense = Expense(datetime(2026, 9, 11, 12, 30), " Їжа ", "10.125")

        self.assertEqual(expense.date, date(2026, 9, 11))
        self.assertEqual(expense.category, "Їжа")
        self.assertEqual(expense.amount, Decimal("10.13"))

    def test_invalid_transaction_amounts_are_rejected(self):
        for value in (0, -1, "NaN", "Infinity"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    Income(date.today(), value)

    def test_balance_collections_cannot_be_modified_by_callers(self):
        balance = Balance("100.00")
        balance.add_income(Income(date.today(), "25.00"))

        incomes = balance.get_incomes()
        self.assertIsInstance(incomes, tuple)
        with self.assertRaises(AttributeError):
            incomes.append(Income(date.today(), "1.00"))
        self.assertEqual(balance.get_value(), Decimal("125.00"))

    def test_snapshot_always_uses_date(self):
        snapshot = BalanceSnapshot(datetime(2026, 9, 11, 12), "5")
        self.assertEqual(snapshot.date, date(2026, 9, 11))


if __name__ == "__main__":
    unittest.main()
