from datetime import date
from decimal import Decimal

from domain.balance_snapshot import BalanceSnapshot
from domain.expense import Expense
from domain.income import Income
from domain.money import to_money


class Balance:
    def __init__(
            self,
            value,
            expenses=None,
            incomes=None,
            value_snapshots=None):
        self._value = to_money(value)
        self._expenses = list(expenses or [])
        self._incomes = list(incomes or [])
        self._value_snapshots = list(value_snapshots or [
            BalanceSnapshot(date=date.today(), value=self._value)
        ])
        if not all(isinstance(item, Expense) for item in self._expenses):
            raise TypeError("expenses must contain only Expense instances.")
        if not all(isinstance(item, Income) for item in self._incomes):
            raise TypeError("incomes must contain only Income instances.")
        if not all(isinstance(item, BalanceSnapshot) for item in self._value_snapshots):
            raise TypeError("value_snapshots must contain only BalanceSnapshot instances.")

    def get_value(self) -> Decimal:
        return self._value

    def get_expenses(self) -> tuple[Expense, ...]:
        return tuple(self._expenses)

    def add_expense(self, expense: Expense) -> BalanceSnapshot:
        if not isinstance(expense, Expense):
            raise TypeError("expense must be an Expense instance.")
        self._value = to_money(self._value - expense.amount)
        snapshot = BalanceSnapshot(expense.date, self._value)
        self._expenses.append(expense)
        self._value_snapshots.append(snapshot)
        return snapshot

    def add_income(self, income: Income) -> BalanceSnapshot:
        if not isinstance(income, Income):
            raise TypeError("income must be an Income instance.")
        self._value = to_money(self._value + income.amount)
        snapshot = BalanceSnapshot(income.date, self._value)
        self._incomes.append(income)
        self._value_snapshots.append(snapshot)
        return snapshot

    def get_value_snapshots(self) -> tuple[BalanceSnapshot, ...]:
        return tuple(self._value_snapshots)

    def get_incomes(self) -> tuple[Income, ...]:
        return tuple(self._incomes)
