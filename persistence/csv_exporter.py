import csv
from operator import itemgetter

from constants import (
    CSV_DECIMAL_SEPARATOR,
    CSV_DELIMITER,
    CSV_ENCODING,
    CSV_EXPENSE_LABEL,
    CSV_HEADERS,
    CSV_INCOME_LABEL,
    CSV_NO_CATEGORY,
    DATE_FORMAT,
)


def _format_amount(amount):
    """Render a money value with the separator the target spreadsheet expects."""
    # "{:.2f}" always emits a dot, whatever the process locale happens to be.
    return f"{amount:.2f}".replace(".", CSV_DECIMAL_SEPARATOR)


def export_transactions(balance, path):
    """Write every income and expense of `balance` to `path`, oldest first.

    Returns the number of transaction rows written, not counting the header.
    """
    transactions = sorted(
        [
            (income.date, CSV_INCOME_LABEL, CSV_NO_CATEGORY, income.amount)
            for income in balance.get_incomes()
        ]
        + [
            (expense.date, CSV_EXPENSE_LABEL, expense.category, expense.amount)
            for expense in balance.get_expenses()
        ],
        key=itemgetter(0),
    )

    # newline="" keeps csv from doubling the line endings on Windows, and the BOM
    # in CSV_ENCODING is what makes Excel read the Cyrillic headers correctly.
    with open(path, "w", encoding=CSV_ENCODING, newline="") as csv_file:
        writer = csv.writer(csv_file, delimiter=CSV_DELIMITER)
        writer.writerow(CSV_HEADERS)
        writer.writerows(
            (occurred_on.strftime(DATE_FORMAT), kind, category, _format_amount(amount))
            for occurred_on, kind, category, amount in transactions
        )
    return len(transactions)
