import calendar
from datetime import date, datetime, time
from operator import itemgetter

from dateutil.relativedelta import relativedelta

from constants import (
    BALANCE_HISTORY_MONTHS,
    MOCK_INITIAL_BALANCE,
    MOCK_MONTHLY_EXPENSES,
    MOCK_MONTHLY_INCOMES,
)
from domain.expense import Expense
from domain.income import Income


def _transaction_date(month, day, today):
    """Place a scheduled day inside `month`, never past the end of it or past today."""
    day = min(day, calendar.monthrange(month.year, month.month)[1])
    if month == today.replace(day=1):
        day = min(day, today.day)
    return month.replace(day=day)


def _scheduled_transactions(index):
    """Merge one month of incomes and expenses into a single day-ordered list.

    A category of None marks an income; sorting on the day alone keeps incomes
    ahead of the expenses they pay for when both fall on the same day.
    """
    incomes = [(day, None, amount) for day, amount in MOCK_MONTHLY_INCOMES[index]]
    expenses = [
        (day, category, amount)
        for day, category, amount in MOCK_MONTHLY_EXPENSES[index]
    ]
    return sorted(incomes + expenses, key=itemgetter(0))


def load_mock_data(repository):
    """Reset the test database and return a balance with six months of demo data."""
    repository.clear_financial_data()
    today = date.today()
    current_month = today.replace(day=1)
    first_month = current_month - relativedelta(months=BALANCE_HISTORY_MONTHS - 1)
    created_at = datetime.combine(first_month, time.min)
    balance = repository.create_balance(MOCK_INITIAL_BALANCE, created_at=created_at)

    for index in range(len(MOCK_MONTHLY_INCOMES)):
        month = first_month + relativedelta(months=index)
        for day, category, amount in _scheduled_transactions(index):
            occurred_on = _transaction_date(month, day, today)
            if category is None:
                income = Income(occurred_on, amount)
                snapshot = balance.add_income(income)
                repository.save_income(income, balance.get_value(), snapshot)
            else:
                expense = Expense(occurred_on, category, amount)
                snapshot = balance.add_expense(expense)
                repository.save_expense(expense, balance.get_value(), snapshot)

    return balance
