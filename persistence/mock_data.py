from datetime import date, datetime, time

from dateutil.relativedelta import relativedelta

from constants import (
    BALANCE_HISTORY_MONTHS,
    MOCK_INITIAL_BALANCE,
    MOCK_MONTHLY_EXPENSES,
    MOCK_MONTHLY_INCOMES,
    MOCK_TRANSACTION_DAY,
)
from domain.expense import Expense
from domain.income import Income


def load_mock_data(repository):
    """Reset the test database and return a balance with six months of demo data."""
    repository.clear_financial_data()
    current_month = date.today().replace(day=1)
    first_month = current_month - relativedelta(months=BALANCE_HISTORY_MONTHS - 1)
    created_at = datetime.combine(first_month, time.min)
    balance = repository.create_balance(MOCK_INITIAL_BALANCE, created_at=created_at)

    for index, income_amount in enumerate(MOCK_MONTHLY_INCOMES):
        month = first_month + relativedelta(months=index)
        transaction_date = (
            date.today()
            if month == current_month
            else month.replace(day=MOCK_TRANSACTION_DAY)
        )
        income = Income(transaction_date, income_amount)
        snapshot = balance.add_income(income)
        repository.save_income(income, balance.get_value(), snapshot)
        for category, expense_amount in MOCK_MONTHLY_EXPENSES[index]:
            expense = Expense(transaction_date, category, expense_amount)
            snapshot = balance.add_expense(expense)
            repository.save_expense(expense, balance.get_value(), snapshot)

    return balance
