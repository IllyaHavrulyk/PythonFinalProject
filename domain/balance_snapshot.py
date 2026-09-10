from dataclasses import dataclass
from datetime import date as Date, datetime
from decimal import Decimal

from domain.money import to_money


@dataclass(frozen=True)
class BalanceSnapshot:
    date: Date
    value: Decimal

    def __post_init__(self) -> None:
        snapshot_date = self.date.date() if isinstance(self.date, datetime) else self.date
        if not isinstance(snapshot_date, Date):
            raise TypeError("Snapshot date must be a date.")
        object.__setattr__(self, "date", snapshot_date)
        object.__setattr__(self, "value", to_money(self.value))
