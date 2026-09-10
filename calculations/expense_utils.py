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
    current_month = date.today().replace(day=1)
    months = [
        current_month - relativedelta(months=offset)
        for offset in range(5, -1, -1)
    ]
    values_by_month = {month: 0 for month in months}

    def snapshot_date(snapshot):
        value = snapshot.date
        return value.date() if isinstance(value, datetime) else value

    filtered_snapshots = sorted(balance_snapshots, key=snapshot_date)

    for snapshot in filtered_snapshots:
        snapshot_month = snapshot_date(snapshot).replace(day=1)
        if snapshot_month in values_by_month:
            values_by_month[snapshot_month] = snapshot.value

    return {
        MONTHS_TRANSLATION[month.strftime("%b")]: value
        for month, value in values_by_month.items()
    }

