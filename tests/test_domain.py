import unittest
from datetime import date, datetime
from decimal import Decimal

from domain.balance import Balance
from domain.balance_snapshot import BalanceSnapshot
from domain.category import Category
from domain.expense import Expense
from domain.income import Income


class CategoryTests(unittest.TestCase):
    def test_keeps_the_name_and_an_optional_description(self):
        category = Category("Їжа", "Продукти")

        self.assertEqual(category.name, "Їжа")
        self.assertEqual(category.description, "Продукти")

    def test_description_defaults_to_empty(self):
        self.assertEqual(Category("Їжа").description, "")

    def test_surrounding_whitespace_is_stripped(self):
        self.assertEqual(Category("  Їжа  ").name, "Їжа")

    def test_rejects_a_blank_or_non_string_name(self):
        for name in ("", "   ", None, 5):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    Category(name)

    def test_is_frozen_and_hashable(self):
        category = Category("Їжа")

        with self.assertRaises(Exception):
            category.name = "Бенз"
        self.assertEqual({category, Category("Їжа")}, {Category("Їжа")})


class ExpenseTests(unittest.TestCase):
    def test_normalises_datetime_to_date_and_rounds_the_amount(self):
        expense = Expense(datetime(2026, 9, 11, 12, 30), " Їжа ", "10.125")

        self.assertEqual(expense.date, date(2026, 9, 11))
        self.assertEqual(expense.category, "Їжа")
        self.assertEqual(expense.amount, Decimal("10.13"))

    def test_rejects_a_date_that_is_not_a_date(self):
        for value in ("2026-09-11", 20260911, None):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    Expense(value, "Їжа", "5.00")

    def test_rejects_a_blank_or_non_string_category(self):
        for category in ("", "   ", None, 7):
            with self.subTest(category=category):
                with self.assertRaises(ValueError):
                    Expense(date.today(), category, "5.00")

    def test_rejects_a_non_positive_amount(self):
        for amount in (0, "0.00", -1):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    Expense(date.today(), "Їжа", amount)


class IncomeTests(unittest.TestCase):
    def test_normalises_datetime_to_date_and_rounds_the_amount(self):
        income = Income(datetime(2026, 9, 11, 23, 59), "10.125")

        self.assertEqual(income.date, date(2026, 9, 11))
        self.assertEqual(income.amount, Decimal("10.13"))

    def test_rejects_a_date_that_is_not_a_date(self):
        with self.assertRaises(TypeError):
            Income("2026-09-11", "5.00")

    def test_rejects_invalid_amounts(self):
        for value in (0, -1, "NaN", "Infinity", "abc"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    Income(date.today(), value)


class BalanceSnapshotTests(unittest.TestCase):
    def test_always_stores_a_plain_date(self):
        snapshot = BalanceSnapshot(datetime(2026, 9, 11, 12), "5")

        self.assertEqual(snapshot.date, date(2026, 9, 11))
        self.assertEqual(snapshot.value, Decimal("5.00"))

    def test_rejects_a_date_that_is_not_a_date(self):
        with self.assertRaises(TypeError):
            BalanceSnapshot("2026-09-11", "5")

    def test_value_may_be_zero_or_negative(self):
        self.assertEqual(BalanceSnapshot(date.today(), "0").value, Decimal("0.00"))
        self.assertEqual(BalanceSnapshot(date.today(), "-5").value, Decimal("-5.00"))


class BalanceTests(unittest.TestCase):
    def test_a_new_balance_records_an_opening_snapshot_for_today(self):
        balance = Balance("100.00")

        snapshots = balance.get_value_snapshots()
        self.assertEqual(len(snapshots), 1)
        self.assertEqual(snapshots[0].date, date.today())
        self.assertEqual(snapshots[0].value, Decimal("100.00"))

    def test_accepts_prepared_history(self):
        expense = Expense(date.today(), "Їжа", "5.00")
        income = Income(date.today(), "7.00")
        snapshot = BalanceSnapshot(date.today(), "100.00")

        balance = Balance("100.00", [expense], [income], [snapshot])

        self.assertEqual(balance.get_expenses(), (expense,))
        self.assertEqual(balance.get_incomes(), (income,))
        self.assertEqual(balance.get_value_snapshots(), (snapshot,))

    def test_rejects_wrongly_typed_history(self):
        cases = (
            {"expenses": ["not an expense"]},
            {"incomes": ["not an income"]},
            {"value_snapshots": ["not a snapshot"]},
        )
        for kwargs in cases:
            with self.subTest(**kwargs):
                with self.assertRaises(TypeError):
                    Balance("100.00", **kwargs)

    def test_adding_an_expense_lowers_the_value_and_records_a_snapshot(self):
        balance = Balance("100.00")
        expense = Expense(date(2026, 9, 11), "Їжа", "25.50")

        snapshot = balance.add_expense(expense)

        self.assertEqual(balance.get_value(), Decimal("74.50"))
        self.assertEqual(snapshot.value, Decimal("74.50"))
        self.assertEqual(snapshot.date, date(2026, 9, 11))
        self.assertIn(expense, balance.get_expenses())
        self.assertIs(balance.get_value_snapshots()[-1], snapshot)

    def test_adding_an_income_raises_the_value_and_records_a_snapshot(self):
        balance = Balance("100.00")

        snapshot = balance.add_income(Income(date(2026, 9, 11), "25.50"))

        self.assertEqual(balance.get_value(), Decimal("125.50"))
        self.assertEqual(snapshot.value, Decimal("125.50"))

    def test_spending_past_zero_is_allowed(self):
        balance = Balance("10.00")

        balance.add_expense(Expense(date.today(), "Їжа", "25.00"))

        self.assertEqual(balance.get_value(), Decimal("-15.00"))

    def test_rejects_adding_the_wrong_type(self):
        balance = Balance("100.00")

        with self.assertRaises(TypeError):
            balance.add_expense(Income(date.today(), "5.00"))
        with self.assertRaises(TypeError):
            balance.add_income(Expense(date.today(), "Їжа", "5.00"))

    def test_collections_are_returned_as_tuples_callers_cannot_mutate(self):
        balance = Balance("100.00")
        balance.add_income(Income(date.today(), "25.00"))

        for collection in (
            balance.get_incomes(),
            balance.get_expenses(),
            balance.get_value_snapshots(),
        ):
            self.assertIsInstance(collection, tuple)
        self.assertEqual(balance.get_value(), Decimal("125.00"))

    def test_history_passed_in_is_copied_not_aliased(self):
        expenses = []
        balance = Balance("100.00", expenses)

        balance.add_expense(Expense(date.today(), "Їжа", "5.00"))

        self.assertEqual(expenses, [], "caller's list must not be mutated")

    def test_money_stays_exact_across_many_small_movements(self):
        balance = Balance("0.00")
        for _ in range(10):
            balance.add_income(Income(date.today(), "0.10"))

        self.assertEqual(balance.get_value(), Decimal("1.00"))


if __name__ == "__main__":
    unittest.main()
