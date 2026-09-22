import calendar
import unittest
from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta

from constants import (
    BALANCE_HISTORY_MONTHS,
    EXPENSE_CATEGORIES,
    MOCK_INITIAL_BALANCE,
    MOCK_MONTHLY_EXPENSES,
    MOCK_MONTHLY_INCOMES,
)
from persistence.mock_data import _scheduled_transactions, _transaction_date, load_mock_data
from tests.support import TemporaryDatabaseTestCase

TODAY = date.today()
MONTH_START = TODAY.replace(day=1)


class TransactionDateTests(unittest.TestCase):
    def test_a_day_inside_a_past_month_is_kept(self):
        past = date(2026, 1, 1)

        self.assertEqual(_transaction_date(past, 15, TODAY), date(2026, 1, 15))

    def test_a_day_past_the_end_of_the_month_is_clamped(self):
        february = date(2026, 2, 1)

        self.assertEqual(_transaction_date(february, 30, TODAY), date(2026, 2, 28))

    def test_a_leap_february_keeps_its_29th(self):
        self.assertEqual(_transaction_date(date(2028, 2, 1), 30, TODAY), date(2028, 2, 29))

    def test_a_future_day_in_the_current_month_is_clamped_to_today(self):
        self.assertEqual(_transaction_date(MONTH_START, 28, TODAY), TODAY)

    def test_an_already_passed_day_in_the_current_month_is_kept(self):
        if TODAY.day == 1:
            self.skipTest("no earlier day available on the 1st")

        self.assertEqual(_transaction_date(MONTH_START, 1, TODAY), MONTH_START)


class ScheduleTests(unittest.TestCase):
    def test_incomes_and_expenses_are_merged_in_day_order(self):
        for index in range(len(MOCK_MONTHLY_INCOMES)):
            with self.subTest(month=index):
                days = [day for day, _, _ in _scheduled_transactions(index)]
                self.assertEqual(days, sorted(days))

    def test_income_rows_carry_no_category(self):
        categories = [category for _, category, _ in _scheduled_transactions(0)]

        self.assertIn(None, categories)

    def test_an_income_sorts_ahead_of_an_expense_on_the_same_day(self):
        schedule = _scheduled_transactions(0)
        by_day = {}
        for day, category, _ in schedule:
            by_day.setdefault(day, []).append(category)
        for day, categories in by_day.items():
            if None in categories and len(categories) > 1:
                self.assertIsNone(categories[0], f"day {day} should pay in before it pays out")

    def test_every_month_has_matching_income_and_expense_data(self):
        self.assertEqual(len(MOCK_MONTHLY_INCOMES), len(MOCK_MONTHLY_EXPENSES))
        self.assertEqual(len(MOCK_MONTHLY_INCOMES), BALANCE_HISTORY_MONTHS)

    def test_every_mock_category_is_a_real_category(self):
        for month in MOCK_MONTHLY_EXPENSES:
            for _, category, _ in month:
                with self.subTest(category=category):
                    self.assertIn(category, EXPENSE_CATEGORIES)


class LoadMockDataTests(TemporaryDatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.balance = load_mock_data(self.repository)

    def test_seeds_every_scheduled_transaction(self):
        expected_incomes = sum(len(month) for month in MOCK_MONTHLY_INCOMES)
        expected_expenses = sum(len(month) for month in MOCK_MONTHLY_EXPENSES)

        self.assertEqual(len(self.balance.get_incomes()), expected_incomes)
        self.assertEqual(len(self.balance.get_expenses()), expected_expenses)

    def test_the_balance_equals_the_opening_value_plus_every_movement(self):
        expected = Decimal(MOCK_INITIAL_BALANCE)
        expected += sum(income.amount for income in self.balance.get_incomes())
        expected -= sum(expense.amount for expense in self.balance.get_expenses())

        self.assertEqual(self.balance.get_value(), expected)

    def test_nothing_is_dated_in_the_future(self):
        latest = max(
            [item.date for item in self.balance.get_expenses()]
            + [item.date for item in self.balance.get_incomes()]
        )

        self.assertLessEqual(latest, TODAY)

    def test_data_spans_the_whole_history_window(self):
        earliest = min(item.date for item in self.balance.get_expenses())
        expected_first_month = MONTH_START - relativedelta(months=BALANCE_HISTORY_MONTHS - 1)

        self.assertEqual(earliest.replace(day=1), expected_first_month)

    def test_transactions_are_spread_over_several_days_per_month(self):
        first_month = MONTH_START - relativedelta(months=BALANCE_HISTORY_MONTHS - 1)
        days = {
            expense.date
            for expense in self.balance.get_expenses()
            if expense.date.replace(day=1) == first_month
        }

        self.assertGreater(len(days), 1, "a month on a single date looks unrealistic")

    def test_every_day_is_valid_for_its_month(self):
        for expense in self.balance.get_expenses():
            last_day = calendar.monthrange(expense.date.year, expense.date.month)[1]
            self.assertLessEqual(expense.date.day, last_day)

    def test_the_seed_survives_a_reload_from_disk(self):
        reloaded = self.repository.load_balance()

        self.assertEqual(reloaded.get_value(), self.balance.get_value())
        self.assertEqual(len(reloaded.get_expenses()), len(self.balance.get_expenses()))

    def test_re_seeding_replaces_rather_than_appends(self):
        again = load_mock_data(self.repository)

        self.assertEqual(again.get_value(), self.balance.get_value())
        self.assertEqual(len(again.get_expenses()), len(self.balance.get_expenses()))


if __name__ == "__main__":
    unittest.main()
