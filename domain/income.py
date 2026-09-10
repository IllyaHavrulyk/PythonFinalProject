from dataclasses import dataclass
from datetime import date as Date, datetime
from decimal import Decimal

from domain.money import positive_money


@dataclass(frozen=True)
class Income:
    date: Date
    amount: Decimal

    def __post_init__(self) -> None:
        occurred_on = self.date.date() if isinstance(self.date, datetime) else self.date
        if not isinstance(occurred_on, Date):
            raise TypeError("Income date must be a date.")
        object.__setattr__(self, "date", occurred_on)
        object.__setattr__(self, "amount", positive_money(self.amount))
