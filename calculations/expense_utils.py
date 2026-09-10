from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from constants import MONTHS_TRANSLATION


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
    result = {}
    first_day_of_last_6_months = date.today().replace(day=1) - relativedelta(months=5)

    def snapshot_date(snapshot):
        value = snapshot.date
        return value.date() if isinstance(value, datetime) else value

    filtered_snapshots = sorted([
        snapshot
        for snapshot in balance_snapshots
        if snapshot_date(snapshot) >= first_day_of_last_6_months
    ], key=snapshot_date)

    for snapshot in filtered_snapshots:
        month = MONTHS_TRANSLATION[snapshot_date(snapshot).strftime("%b")]
        result[month] = snapshot.value
    return result

