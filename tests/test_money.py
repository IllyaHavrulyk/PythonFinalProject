import unittest
from decimal import Decimal

from domain.money import MONEY_QUANTUM, positive_money, to_money


class ToMoneyTests(unittest.TestCase):
    def test_accepts_the_types_the_ui_and_database_hand_it(self):
        for value, expected in (
            (10, "10.00"),
            (10.5, "10.50"),
            ("10.5", "10.50"),
            (Decimal("10.5"), "10.50"),
        ):
            with self.subTest(value=value):
                self.assertEqual(to_money(value), Decimal(expected))

    def test_rounds_half_up_rather_than_to_even(self):
        # Decimal's default is ROUND_HALF_EVEN, which would give 10.12 here.
        self.assertEqual(to_money("10.125"), Decimal("10.13"))
        self.assertEqual(to_money("10.135"), Decimal("10.14"))

    def test_result_always_has_two_decimal_places(self):
        for value in ("1", "1.5", "1.234", 0, -3):
            with self.subTest(value=value):
                self.assertEqual(to_money(value).as_tuple().exponent, MONEY_QUANTUM.as_tuple().exponent)

    def test_negative_values_are_allowed(self):
        # A balance may legitimately go negative, unlike a transaction amount.
        self.assertEqual(to_money("-25.50"), Decimal("-25.50"))

    def test_rejects_values_that_are_not_numbers(self):
        for value in ("", "abc", None, object(), [1]):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    to_money(value)

    def test_rejects_non_finite_values(self):
        for value in ("NaN", "Infinity", "-Infinity", float("inf"), float("nan")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    to_money(value)

    def test_rejects_values_too_large_to_quantize(self):
        # quantize() raises decimal.InvalidOperation here; it must surface as ValueError
        # so callers catching (TypeError, ValueError) are not bypassed.
        for value in ("1e100", "1E+40", "9" * 32):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    to_money(value)


class PositiveMoneyTests(unittest.TestCase):
    def test_accepts_values_above_zero(self):
        self.assertEqual(positive_money("0.01"), Decimal("0.01"))

    def test_rejects_zero_and_negative_values(self):
        for value in (0, "0", "0.00", -1, "-0.01"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    positive_money(value)

    def test_a_value_that_rounds_down_to_zero_is_rejected(self):
        with self.assertRaises(ValueError):
            positive_money("0.004")


if __name__ == "__main__":
    unittest.main()
