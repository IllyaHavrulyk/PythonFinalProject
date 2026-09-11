import locale
import unittest
from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta

from calculations.dashboard_utils import build_dashboard_alerts, calculate_balance_forecast
from calculations.expense_utils import filter_balance_snapshots
from constants import (
    BALANCE_HISTORY_MONTHS,
    BALANCE_INCREASED_TEXT,
    BALANCE_TREND_MONTHS,
    FORECAST_MONTHS,
)
from domain.balance import Balance
from domain.balance_snapshot import BalanceSnapshot
from domain.income import Income


class CalculationTests(unittest.TestCase):
    def test_forecast_uses_decimal_values(self):
        balance = Balance("100.00")
        balance.add_income(Income(date.today(), "10.00"))

        forecast = calculate_balance_forecast(balance)

        self.assertEqual(len(forecast), FORECAST_MONTHS)
        self.assertEqual(forecast[0], Decimal("120.00"))
        self.assertTrue(all(isinstance(value, Decimal) for value in forecast))

    def test_history_contains_all_six_months(self):
        history = filter_balance_snapshots(Balance("50.00").get_value_snapshots())

        self.assertEqual(len(history), BALANCE_HISTORY_MONTHS)
        self.assertEqual(list(history.values())[-1], Decimal("50.00"))
        self.assertTrue(all(value == 0 for value in list(history.values())[:-1]))

    def test_history_carries_the_balance_across_inactive_months(self):
        first_month = date.today().replace(day=1) - relativedelta(
            months=BALANCE_HISTORY_MONTHS - 1,
        )
        history = filter_balance_snapshots([
            BalanceSnapshot(first_month, Decimal("5000.00")),
            BalanceSnapshot(date.today(), Decimal("5200.00")),
        ])

        values = list(history.values())
        self.assertEqual(values[0], Decimal("5000.00"))
        # The months in between saw no transaction, so the balance stood still.
        self.assertTrue(all(value == Decimal("5000.00") for value in values[1:-1]))
        self.assertEqual(values[-1], Decimal("5200.00"))

    def test_month_labels_do_not_depend_on_the_time_locale(self):
        previous_locale = locale.setlocale(locale.LC_TIME)
        try:
            try:
                locale.setlocale(locale.LC_TIME, "uk_UA.UTF-8")
            except locale.Error:
                self.skipTest("uk_UA.UTF-8 is not installed on this machine")
            history = filter_balance_snapshots(Balance("50.00").get_value_snapshots())
        finally:
            locale.setlocale(locale.LC_TIME, previous_locale)

        self.assertEqual(len(history), BALANCE_HISTORY_MONTHS)

    def test_balance_trend_is_measured_from_the_balance_carried_into_the_window(self):
        month_start = date.today().replace(day=1)
        balance = Balance(
            "12000.00",
            value_snapshots=[
                BalanceSnapshot(
                    month_start - relativedelta(months=BALANCE_TREND_MONTHS),
                    Decimal("10000.00"),
                ),
                # First transaction inside the window; not the baseline.
                BalanceSnapshot(
                    month_start - relativedelta(months=BALANCE_TREND_MONTHS - 2),
                    Decimal("11000.00"),
                ),
                BalanceSnapshot(date.today(), Decimal("12000.00")),
            ],
        )

        balance_alert = build_dashboard_alerts(balance)[2][0]

        self.assertIn(BALANCE_INCREASED_TEXT, balance_alert)
        self.assertIn("20.0", balance_alert)

    def test_alerts_survive_a_balance_with_no_recent_activity(self):
        stale_date = date.today().replace(day=1) - relativedelta(months=5)
        balance = Balance(
            "5000.00",
            value_snapshots=[BalanceSnapshot(stale_date, Decimal("5000.00"))],
        )

        alerts = build_dashboard_alerts(balance)

        self.assertEqual(len(alerts), 4)
        self.assertIn("0.00", alerts[2][0])


if __name__ == "__main__":
    unittest.main()
