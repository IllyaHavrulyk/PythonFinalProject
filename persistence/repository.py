from datetime import date
from decimal import Decimal
from typing import Protocol

from domain.balance import Balance
from domain.balance_snapshot import BalanceSnapshot
from domain.category import Category
from domain.expense import Expense
from domain.income import Income


class BalanceRepository(Protocol):
    def create_balance(self, value: Decimal, created_at: date | None = None) -> Balance: ...

    def load_balance(self) -> Balance | None: ...

    def save_expense(
            self,
            expense: Expense,
            new_balance: Decimal,
            snapshot: BalanceSnapshot) -> None: ...

    def save_income(
            self,
            income: Income,
            new_balance: Decimal,
            snapshot: BalanceSnapshot) -> None: ...

    def load_categories(self) -> list[Category]: ...

    def clear_financial_data(self) -> None: ...
