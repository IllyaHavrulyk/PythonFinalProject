import unittest
from datetime import date
from decimal import Decimal

from calculations.dashboard_utils import calculate_balance_forecast
from calculations.expense_utils import filter_balance_snapshots
from constants import BALANCE_HISTORY_MONTHS, FORECAST_MONTHS
from domain.balance import Balance
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


if __name__ == "__main__":
    unittest.main()
