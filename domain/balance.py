from datetime import datetime

from domain.balance_snapshot import BalanceSnapshot


class Balance:
    def __init__(self, value):
        self.__value = value
        self.__expenses = []
        self.__incomes = []
        self.__value_snapshots = [BalanceSnapshot(date=datetime.now(), value=value)]

    def get_value(self):
        return self.__value

    def get_expenses(self):
        return self.__expenses

    def add_expense(self, expense):
        self.__expenses.append(expense)
        self.__value -= expense.amount
        self.__value_snapshots.append(BalanceSnapshot(expense.date, self.__value))

    def add_income(self, income):
        self.__incomes.append(income)
        self.__value += income.amount
        self.__value_snapshots.append(BalanceSnapshot(income.date, self.__value))

    def get_value_snapshots(self):
        return self.__value_snapshots
    def get_incomes(self):
        return self.__incomes
