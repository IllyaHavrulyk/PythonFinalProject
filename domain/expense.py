from dataclasses import dataclass
from datetime import date as Date, datetime
from decimal import Decimal

from domain.money import positive_money


@dataclass(frozen=True)
class Expense:
    date: Date
    category: str
    amount: Decimal

    def __post_init__(self) -> None:
        occurred_on = self.date.date() if isinstance(self.date, datetime) else self.date
        if not isinstance(occurred_on, Date):
            raise TypeError("Expense date must be a date.")
        category = self.category.strip() if isinstance(self.category, str) else ""
        if not category:
            raise ValueError("Expense category cannot be empty.")
        object.__setattr__(self, "date", occurred_on)
        object.__setattr__(self, "category", category)
        object.__setattr__(self, "amount", positive_money(self.amount))
