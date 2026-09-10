from datetime import datetime

from domain.balance_snapshot import BalanceSnapshot


class Balance:
    def __init__(
            self,
            value,
            repository=None,
            expenses=None,
            incomes=None,
            value_snapshots=None):
        self.__value = value
        self.__repository = repository
        self.__expenses = list(expenses or [])
        self.__incomes = list(incomes or [])
        self.__value_snapshots = list(value_snapshots or [
            BalanceSnapshot(date=datetime.now(), value=value)
        ])

    def get_value(self):
        return self.__value

    def get_expenses(self):
        return self.__expenses

    def add_expense(self, expense):
        new_value = self.__value - expense.amount
        snapshot = BalanceSnapshot(expense.date, new_value)
        if self.__repository is not None:
            self.__repository.save_expense(expense, new_value, snapshot)
        self.__expenses.append(expense)
        self.__value = new_value
        self.__value_snapshots.append(snapshot)

    def add_income(self, income):
        new_value = self.__value + income.amount
        snapshot = BalanceSnapshot(income.date, new_value)
        if self.__repository is not None:
            self.__repository.save_income(income, new_value, snapshot)
        self.__incomes.append(income)
        self.__value = new_value
        self.__value_snapshots.append(snapshot)

    def get_value_snapshots(self):
        return self.__value_snapshots

    def get_incomes(self):
        return self.__incomes
