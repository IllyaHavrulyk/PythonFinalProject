from datetime import date
from decimal import Decimal

from constants import APP_MODE_TEST
from domain.balance import Balance
from domain.balance_snapshot import BalanceSnapshot
from domain.expense import Expense
from domain.income import Income
from domain.money import to_money
from persistence.mock_data import load_mock_data
from persistence.repository import BalanceRepository


class FinanceService:
    """Coordinates domain changes and persistence for the user interface."""

    def __init__(self, repository: BalanceRepository) -> None:
        self._repository = repository
        self._balance: Balance | None = None

    @property
    def balance(self) -> Balance:
        if self._balance is None:
            raise RuntimeError("Finance service has not been initialized.")
        return self._balance

    def initialize(
            self,
            app_mode: str,
            reset_data_on_start: bool,
            initial_balance: Decimal | str | int | float | None = None,
    ) -> Balance | None:
        stored_balance = self._repository.load_balance()
        if app_mode == APP_MODE_TEST and (reset_data_on_start or stored_balance is None):
            self._balance = load_mock_data(self._repository)
        elif stored_balance is not None:
            self._balance = stored_balance
        elif initial_balance is not None:
            starting_balance = to_money(initial_balance)
            if starting_balance < 0:
                raise ValueError("Initial balance cannot be negative.")
            self._balance = self._repository.create_balance(starting_balance)
        return self._balance

    def add_expense(
            self,
            amount,
            category: str,
            occurred_on: date | None = None,
    ) -> Expense:
        expense = Expense(occurred_on or date.today(), category, amount)
        new_balance = to_money(self.balance.get_value() - expense.amount)
        snapshot = BalanceSnapshot(expense.date, new_balance)
        self._repository.save_expense(expense, new_balance, snapshot)
        self.balance.add_expense(expense)
        return expense

    def add_income(self, amount, occurred_on: date | None = None) -> Income:
        income = Income(occurred_on or date.today(), amount)
        new_balance = to_money(self.balance.get_value() + income.amount)
        snapshot = BalanceSnapshot(income.date, new_balance)
        self._repository.save_income(income, new_balance, snapshot)
        self.balance.add_income(income)
        return income

    def get_categories(self) -> list[str]:
        return [category.name for category in self._repository.load_categories()]
