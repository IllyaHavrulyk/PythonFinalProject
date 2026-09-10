from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


MONEY_QUANTUM = Decimal("0.01")


def to_money(value) -> Decimal:
    """Return a finite monetary value rounded to two decimal places."""
    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("Amount must be a valid number.") from exc

    if not amount.is_finite():
        raise ValueError("Amount must be finite.")
    return amount.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)


def positive_money(value) -> Decimal:
    amount = to_money(value)
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    return amount
