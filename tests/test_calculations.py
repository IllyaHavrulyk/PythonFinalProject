import locale
import unittest
from datetime import date, datetime
from decimal import Decimal

from dateutil.relativedelta import relativedelta

from calculations.dashboard_utils import (
    build_dashboard_alerts,
    calculate_average_monthly_change,
    calculate_balance_forecast,
    get_future_month_labels,
)
from calculations.expense_utils import (
    filter_balance_snapshots,
    get_expense_totals_by_category,
    get_expenses_by_date_range,
)
from constants import (
    BALANCE_DECREASED_TEXT,
    BALANCE_HISTORY_MONTHS,
    BALANCE_INCREASED_TEXT,
    BALANCE_TREND_MONTHS,
    FORECAST_MONTHS,
    GREEN_ALERT_STYLE,
    MONTHS_TRANSLATION,
    NO_ACTIVITY_TEXT,
    NO_MONTHLY_EXPENSES_TEXT,
    ORANGE_ALERT_STYLE,
    RED_ALERT_STYLE,
)
from domain.balance import Balance
from domain.balance_snapshot import BalanceSnapshot
from domain.expense import Expense
from domain.income import Income

TODAY = date.today()
MONTH_START = TODAY.replace(day=1)

SPEND_ALERT, CATEGORY_ALERT, BALANCE_ALERT, FORECAST_ALERT = range(4)


def balance_with(incomes=(), expenses=(), opening="1000.00"):
    """Build a balance whose activity all sits inside the current month."""
    balance = Balance(opening)
    for amount in incomes:
        balance.add_income(Income(TODAY, amount))
    for category, amount in expenses:
        balance.add_expense(Expense(TODAY, category, amount))
    return balance


class ExpenseFilterTests(unittest.TestCase):
    def setUp(self):
        self.expenses = [
            Expense(date(2026, 9, 1), "Їжа", "10.00"),
            Expense(date(2026, 9, 10), "Бенз", "20.00"),
            Expense(date(2026, 9, 20), "Їжа", "30.00"),
        ]

    def test_without_bounds_everything_is_returned(self):
        self.assertEqual(get_expenses_by_date_range(self.expenses), self.expenses)

    def test_start_and_end_bounds_are_inclusive(self):
        selected = get_expenses_by_date_range(
            self.expenses, date(2026, 9, 1), date(2026, 9, 10),
        )

        self.assertEqual(len(selected), 2)

    def test_only_a_start_bound(self):
        selected = get_expenses_by_date_range(self.expenses, date(2026, 9, 10), None)

        self.assertEqual([item.amount for item in selected], [Decimal("20.00"), Decimal("30.00")])

    def test_only_an_end_bound(self):
        selected = get_expenses_by_date_range(self.expenses, None, date(2026, 9, 1))

        self.assertEqual([item.amount for item in selected], [Decimal("10.00")])

    def test_a_range_matching_nothing_returns_empty(self):
        self.assertEqual(
            get_expenses_by_date_range(self.expenses, date(2026, 10, 1), date(2026, 10, 31)),
            [],
        )

    def test_totals_are_summed_per_category(self):
        totals = get_expense_totals_by_category(self.expenses)

        self.assertEqual(totals, {"Їжа": Decimal("40.00"), "Бенз": Decimal("20.00")})

    def test_totals_honour_the_date_range(self):
        totals = get_expense_totals_by_category(
            self.expenses, date(2026, 9, 5), date(2026, 9, 15),
        )

        self.assertEqual(totals, {"Бенз": Decimal("20.00")})

    def test_totals_of_nothing_is_an_empty_mapping(self):
        self.assertEqual(get_expense_totals_by_category([]), {})


class BalanceHistoryTests(unittest.TestCase):
    def test_always_returns_one_entry_per_month_in_the_window(self):
        history = filter_balance_snapshots(Balance("50.00").get_value_snapshots())

        self.assertEqual(len(history), BALANCE_HISTORY_MONTHS)
        self.assertEqual(list(history), [
            MONTHS_TRANSLATION[(MONTH_START - relativedelta(months=offset)).month]
            for offset in range(BALANCE_HISTORY_MONTHS - 1, -1, -1)
        ])

    def test_months_before_the_first_snapshot_are_zero(self):
        history = filter_balance_snapshots(Balance("50.00").get_value_snapshots())

        values = list(history.values())
        self.assertTrue(all(value == 0 for value in values[:-1]))
        self.assertEqual(values[-1], Decimal("50.00"))

    def test_the_balance_is_carried_across_inactive_months(self):
        first_month = MONTH_START - relativedelta(months=BALANCE_HISTORY_MONTHS - 1)

        history = filter_balance_snapshots([
            BalanceSnapshot(first_month, Decimal("5000.00")),
            BalanceSnapshot(TODAY, Decimal("5200.00")),
        ])

        values = list(history.values())
        self.assertEqual(values[0], Decimal("5000.00"))
        self.assertTrue(all(value == Decimal("5000.00") for value in values[1:-1]))
        self.assertEqual(values[-1], Decimal("5200.00"))

    def test_a_snapshot_before_the_window_seeds_the_first_month(self):
        history = filter_balance_snapshots([
            BalanceSnapshot(MONTH_START - relativedelta(months=24), Decimal("777.00")),
        ])

        self.assertTrue(all(value == Decimal("777.00") for value in history.values()))

    def test_the_last_snapshot_of_a_month_wins(self):
        history = filter_balance_snapshots([
            BalanceSnapshot(MONTH_START, Decimal("100.00")),
            BalanceSnapshot(TODAY, Decimal("300.00")),
        ])

        self.assertEqual(list(history.values())[-1], Decimal("300.00"))

    def test_snapshots_after_the_current_month_are_ignored(self):
        history = filter_balance_snapshots([
            BalanceSnapshot(TODAY, Decimal("100.00")),
            BalanceSnapshot(MONTH_START + relativedelta(months=2), Decimal("999.00")),
        ])

        self.assertEqual(list(history.values())[-1], Decimal("100.00"))

    def test_no_snapshots_at_all_gives_zeroes(self):
        history = filter_balance_snapshots([])

        self.assertEqual(len(history), BALANCE_HISTORY_MONTHS)
        self.assertTrue(all(value == 0 for value in history.values()))

    def test_datetime_valued_snapshots_are_accepted(self):
        history = filter_balance_snapshots([
            BalanceSnapshot(datetime(TODAY.year, TODAY.month, TODAY.day, 13), Decimal("42.00")),
        ])

        self.assertEqual(list(history.values())[-1], Decimal("42.00"))

    def test_month_labels_do_not_depend_on_the_time_locale(self):
        previous = locale.setlocale(locale.LC_TIME)
        try:
            try:
                locale.setlocale(locale.LC_TIME, "uk_UA.UTF-8")
            except locale.Error:
                self.skipTest("uk_UA.UTF-8 is not installed on this machine")
            history = filter_balance_snapshots(Balance("50.00").get_value_snapshots())
        finally:
            locale.setlocale(locale.LC_TIME, previous)

        self.assertEqual(len(history), BALANCE_HISTORY_MONTHS)


class ForecastTests(unittest.TestCase):
    def test_no_transactions_means_no_average_change(self):
        self.assertEqual(calculate_average_monthly_change(Balance("100.00")), Decimal("0.00"))

    def test_average_uses_income_minus_expenses(self):
        balance = balance_with(incomes=["300.00"], expenses=[("Їжа", "100.00")])

        self.assertEqual(calculate_average_monthly_change(balance), Decimal("200.00"))

    def test_transactions_older_than_the_window_are_ignored(self):
        balance = Balance("100.00")
        balance.add_income(Income(MONTH_START - relativedelta(months=FORECAST_MONTHS + 2), "900.00"))

        self.assertEqual(calculate_average_monthly_change(balance), Decimal("0.00"))

    def test_the_average_is_spread_over_the_months_that_have_data(self):
        balance = Balance("0.00")
        for offset in range(3):
            balance.add_income(Income(MONTH_START - relativedelta(months=offset), "300.00"))

        # 900 across the three months from the earliest transaction to now.
        self.assertEqual(calculate_average_monthly_change(balance), Decimal("300.00"))

    def test_forecast_has_one_decimal_entry_per_month(self):
        forecast = calculate_balance_forecast(balance_with(incomes=["10.00"], opening="100.00"))

        self.assertEqual(len(forecast), FORECAST_MONTHS)
        self.assertTrue(all(isinstance(value, Decimal) for value in forecast))
        self.assertEqual(forecast[0], Decimal("120.00"))

    def test_forecast_declines_when_spending_outruns_income(self):
        forecast = calculate_balance_forecast(
            balance_with(expenses=[("Їжа", "50.00")], opening="1000.00"),
        )

        self.assertLess(forecast[-1], forecast[0])

    def test_future_month_labels_follow_the_current_month(self):
        labels = get_future_month_labels()

        self.assertEqual(len(labels), FORECAST_MONTHS)
        self.assertEqual(
            labels,
            [
                MONTHS_TRANSLATION[(MONTH_START + relativedelta(months=offset)).month]
                for offset in range(1, FORECAST_MONTHS + 1)
            ],
        )


class DashboardAlertTests(unittest.TestCase):
    def test_always_returns_four_alerts_of_text_and_style(self):
        alerts = build_dashboard_alerts(balance_with(incomes=["100.00"]))

        self.assertEqual(len(alerts), 4)
        for text, style in alerts:
            self.assertIsInstance(text, str)
            self.assertIsInstance(style, str)

    def test_a_month_with_no_activity_invites_the_user_to_add_some(self):
        text, style = build_dashboard_alerts(Balance("100.00"))[SPEND_ALERT]

        self.assertEqual(text, NO_ACTIVITY_TEXT)
        self.assertEqual(style, ORANGE_ALERT_STYLE)

    def test_expenses_without_income_are_flagged_red(self):
        text, style = build_dashboard_alerts(
            balance_with(expenses=[("Їжа", "40.00")]),
        )[SPEND_ALERT]

        self.assertIn("40.00", text)
        self.assertEqual(style, RED_ALERT_STYLE)

    def test_spending_well_within_income_is_green(self):
        text, style = build_dashboard_alerts(
            balance_with(incomes=["1000.00"], expenses=[("Їжа", "700.00")]),
        )[SPEND_ALERT]

        self.assertIn("70.0", text)
        self.assertEqual(style, GREEN_ALERT_STYLE)

    def test_spending_at_the_warning_threshold_is_orange(self):
        _, style = build_dashboard_alerts(
            balance_with(incomes=["1000.00"], expenses=[("Їжа", "800.00")]),
        )[SPEND_ALERT]

        self.assertEqual(style, ORANGE_ALERT_STYLE)

    def test_spending_exactly_all_the_income_is_still_orange(self):
        _, style = build_dashboard_alerts(
            balance_with(incomes=["1000.00"], expenses=[("Їжа", "1000.00")]),
        )[SPEND_ALERT]

        self.assertEqual(style, ORANGE_ALERT_STYLE)

    def test_spending_beyond_income_is_red(self):
        _, style = build_dashboard_alerts(
            balance_with(incomes=["1000.00"], expenses=[("Їжа", "1100.00")]),
        )[SPEND_ALERT]

        self.assertEqual(style, RED_ALERT_STYLE)

    def test_the_largest_category_is_named(self):
        text, style = build_dashboard_alerts(
            balance_with(
                incomes=["5000.00"],
                expenses=[("Їжа", "100.00"), ("Квартира", "900.00"), ("Їжа", "150.00")],
            ),
        )[CATEGORY_ALERT]

        self.assertIn("Квартира", text)
        self.assertIn("900.00", text)
        self.assertEqual(style, ORANGE_ALERT_STYLE)

    def test_a_month_without_expenses_says_so(self):
        text, style = build_dashboard_alerts(balance_with(incomes=["100.00"]))[CATEGORY_ALERT]

        self.assertEqual(text, NO_MONTHLY_EXPENSES_TEXT)
        self.assertEqual(style, GREEN_ALERT_STYLE)

    def test_a_growing_balance_is_reported_as_growth(self):
        text, style = build_dashboard_alerts(
            balance_with(incomes=["500.00"], opening="1000.00"),
        )[BALANCE_ALERT]

        self.assertIn(BALANCE_INCREASED_TEXT, text)
        self.assertIn("50.0", text)
        self.assertEqual(style, GREEN_ALERT_STYLE)

    def test_a_shrinking_balance_is_reported_in_red(self):
        text, style = build_dashboard_alerts(
            balance_with(expenses=[("Їжа", "400.00")], opening="1000.00"),
        )[BALANCE_ALERT]

        self.assertIn(BALANCE_DECREASED_TEXT, text)
        self.assertIn("40.0", text)
        self.assertEqual(style, RED_ALERT_STYLE)

    def test_an_unchanged_balance_is_reported_as_an_amount(self):
        stale = MONTH_START - relativedelta(months=BALANCE_TREND_MONTHS + 1)
        balance = Balance("5000.00", value_snapshots=[BalanceSnapshot(stale, Decimal("5000.00"))])

        text, style = build_dashboard_alerts(balance)[BALANCE_ALERT]

        self.assertIn("0.00", text)
        self.assertEqual(style, GREEN_ALERT_STYLE)

    def test_the_trend_is_measured_from_the_balance_carried_into_the_window(self):
        balance = Balance("12000.00", value_snapshots=[
            BalanceSnapshot(MONTH_START - relativedelta(months=BALANCE_TREND_MONTHS), Decimal("10000.00")),
            BalanceSnapshot(MONTH_START - relativedelta(months=BALANCE_TREND_MONTHS - 2), Decimal("11000.00")),
            BalanceSnapshot(TODAY, Decimal("12000.00")),
        ])

        text, _ = build_dashboard_alerts(balance)[BALANCE_ALERT]

        self.assertIn(BALANCE_INCREASED_TEXT, text)
        self.assertIn("20.0", text)

    def test_a_balance_starting_from_zero_reports_the_amount_not_a_percentage(self):
        balance = Balance("0.00")
        balance.add_income(Income(TODAY, "250.00"))

        text, _ = build_dashboard_alerts(balance)[BALANCE_ALERT]

        self.assertIn("250.00", text)

    def test_an_improving_forecast_is_green_and_a_worsening_one_is_red(self):
        growing = build_dashboard_alerts(balance_with(incomes=["500.00"]))[FORECAST_ALERT]
        shrinking = build_dashboard_alerts(
            balance_with(expenses=[("Їжа", "100.00")], opening="5000.00"),
        )[FORECAST_ALERT]

        self.assertEqual(growing[1], GREEN_ALERT_STYLE)
        self.assertEqual(shrinking[1], RED_ALERT_STYLE)

    def test_thousands_are_separated_for_readability(self):
        text, _ = build_dashboard_alerts(
            balance_with(incomes=["50000.00"], expenses=[("Квартира", "12345.00")]),
        )[CATEGORY_ALERT]

        self.assertIn("12 345.00", text)


if __name__ == "__main__":
    unittest.main()
