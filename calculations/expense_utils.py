from datetime import date, datetime
from decimal import Decimal

from dateutil.relativedelta import relativedelta

from constants import BALANCE_HISTORY_MONTHS, MONTHS_TRANSLATION


def _as_date(value):
    return value.date() if isinstance(value, datetime) else value


def get_expenses_by_date_range(expenses, start_date=None, end_date=None):
    return [
        expense
        for expense in expenses
        if (start_date is None or expense.date >= start_date)
           and (end_date is None or expense.date <= end_date)
    ]


def get_expense_totals_by_category(expenses, start_date=None, end_date=None):
    totals = {}
    for expense in get_expenses_by_date_range(expenses, start_date, end_date):
        totals[expense.category] = totals.get(expense.category, 0) + expense.amount
    return totals


def filter_balance_snapshots(balance_snapshots):
    """Return the closing balance of each of the last months, keyed by month label.

    A month without its own snapshot keeps the balance it was carrying, because a
    balance is a running total and not a per-month amount. Months before the very
    first snapshot have nothing to carry and stay at zero.
    """
    current_month = date.today().replace(day=1)
    months = [
        current_month - relativedelta(months=offset)
        for offset in range(BALANCE_HISTORY_MONTHS - 1, -1, -1)
    ]

    closing_value_by_month = {}
    carried_value = Decimal("0.00")
    for snapshot in sorted(balance_snapshots, key=lambda item: _as_date(item.date)):
        snapshot_month = _as_date(snapshot.date).replace(day=1)
        if snapshot_month < months[0]:
            carried_value = snapshot.value
        elif snapshot_month <= current_month:
            closing_value_by_month[snapshot_month] = snapshot.value

    history = {}
    for month in months:
        carried_value = closing_value_by_month.get(month, carried_value)
        history[MONTHS_TRANSLATION[month.month]] = carried_value
    return history
