from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from constants import (
    AMOUNT_FORMAT_SPEC,
    BALANCE_DECREASED_TEXT,
    BALANCE_GROWTH_TEXT_TEMPLATE,
    BALANCE_INCREASED_TEXT,
    BALANCE_TREND_MONTHS,
    BALANCE_UNCHANGED_TEXT,
    FORECAST_MONTHS,
    FORECAST_TEXT_TEMPLATE,
    GREEN_ALERT_STYLE,
    MONTHS_TRANSLATION,
    NO_ACTIVITY_TEXT,
    NO_INCOME_TEXT_TEMPLATE,
    NO_MONTHLY_EXPENSES_TEXT,
    ORANGE_ALERT_STYLE,
    PERCENT_FORMAT_SPEC,
    RED_ALERT_STYLE,
    SPEND_DIFF_TEXT_TEMPLATE,
    SPEND_DANGER_PERCENTAGE,
    SPEND_INCOME_DIFF_TEXT_TEMPLATE,
    SPEND_WARNING_PERCENTAGE,
    THOUSANDS_SEPARATOR,
    ZERO_BALANCE_CHANGE_TEXT_TEMPLATE,
)


def _as_date(value):
    return value.date() if isinstance(value, datetime) else value


def _month_start(value):
    value = _as_date(value)
    return value.replace(day=1)


def _format_amount(value):
    return format(value, AMOUNT_FORMAT_SPEC).replace(",", THOUSANDS_SEPARATOR)


def calculate_average_monthly_change(balance, months=FORECAST_MONTHS):
    """Return the average net change across the available recent month span."""
    current_month = date.today().replace(day=1)
    cutoff = current_month - relativedelta(months=months - 1)
    transactions = [
        (income.date, income.amount)
        for income in balance.get_incomes()
        if _as_date(income.date) >= cutoff
    ] + [
        (expense.date, -expense.amount)
        for expense in balance.get_expenses()
        if _as_date(expense.date) >= cutoff
    ]

    if not transactions:
        return 0.0

    earliest_month = min(_month_start(transaction_date) for transaction_date, _ in transactions)
    month_count = (
        (current_month.year - earliest_month.year) * 12
        + current_month.month
        - earliest_month.month
        + 1
    )
    average = sum(amount for _, amount in transactions) / min(months, max(1, month_count))
    return round(average, 2)


def calculate_balance_forecast(balance, months=FORECAST_MONTHS):
    monthly_change = calculate_average_monthly_change(balance, months)
    current_balance = balance.get_value()
    return [round(current_balance + monthly_change * offset, 2) for offset in range(1, months + 1)]


def get_future_month_labels(months=FORECAST_MONTHS):
    current_month = date.today().replace(day=1)
    labels = []
    for offset in range(1, months + 1):
        future_month = current_month + relativedelta(months=offset)
        labels.append(MONTHS_TRANSLATION[future_month.strftime("%b")])
    return labels


def build_dashboard_alerts(balance):
    """Build four (text, style) alert configurations from current balance data."""
    today = date.today()
    current_month_expenses = [
        expense
        for expense in balance.get_expenses()
        if _month_start(expense.date) == today.replace(day=1)
    ]
    current_month_incomes = [
        income
        for income in balance.get_incomes()
        if _month_start(income.date) == today.replace(day=1)
    ]
    total_expenses = sum(expense.amount for expense in current_month_expenses)
    total_income = sum(income.amount for income in current_month_incomes)

    if total_expenses == 0 and total_income == 0:
        income_comparison = (NO_ACTIVITY_TEXT, ORANGE_ALERT_STYLE)
    elif total_income == 0:
        income_comparison = (
            NO_INCOME_TEXT_TEMPLATE.format(amount=_format_amount(total_expenses)),
            RED_ALERT_STYLE,
        )
    else:
        spend_percentage = total_expenses / total_income * 100
        if spend_percentage > SPEND_DANGER_PERCENTAGE:
            comparison_style = RED_ALERT_STYLE
        elif spend_percentage >= SPEND_WARNING_PERCENTAGE:
            comparison_style = ORANGE_ALERT_STYLE
        else:
            comparison_style = GREEN_ALERT_STYLE
        income_comparison = (
            SPEND_INCOME_DIFF_TEXT_TEMPLATE.format(
                percentage=format(spend_percentage, PERCENT_FORMAT_SPEC),
            ),
            comparison_style,
        )

    if current_month_expenses:
        totals_by_category = {}
        for expense in current_month_expenses:
            totals_by_category[expense.category] = (
                totals_by_category.get(expense.category, 0) + expense.amount
            )
        category, amount = max(totals_by_category.items(), key=lambda item: item[1])
        category_alert = (
            SPEND_DIFF_TEXT_TEMPLATE.format(category=category, number=_format_amount(amount)),
            ORANGE_ALERT_STYLE,
        )
    else:
        category_alert = (NO_MONTHLY_EXPENSES_TEXT, GREEN_ALERT_STYLE)

    three_month_cutoff = today.replace(day=1) - relativedelta(
        months=BALANCE_TREND_MONTHS - 1,
    )
    recent_snapshots = sorted(
        [
            snapshot
            for snapshot in balance.get_value_snapshots()
            if _as_date(snapshot.date) >= three_month_cutoff
        ],
        key=lambda snapshot: _as_date(snapshot.date),
    )
    starting_balance = recent_snapshots[0].value
    current_balance = balance.get_value()
    balance_change = current_balance - starting_balance
    if starting_balance:
        balance_percentage = abs(balance_change / starting_balance * 100)
        direction = (
            BALANCE_INCREASED_TEXT
            if balance_change > 0
            else BALANCE_DECREASED_TEXT
            if balance_change < 0
            else BALANCE_UNCHANGED_TEXT
        )
        balance_text = BALANCE_GROWTH_TEXT_TEMPLATE.format(
            diff=direction,
            percentage=format(balance_percentage, PERCENT_FORMAT_SPEC),
            months=BALANCE_TREND_MONTHS,
        )
    else:
        balance_text = ZERO_BALANCE_CHANGE_TEXT_TEMPLATE.format(
            amount=_format_amount(balance_change),
            months=BALANCE_TREND_MONTHS,
        )
    balance_alert = (
        balance_text,
        GREEN_ALERT_STYLE if balance_change >= 0 else RED_ALERT_STYLE,
    )

    forecast_balance = calculate_balance_forecast(balance)[-1]
    forecast_alert = (
        FORECAST_TEXT_TEMPLATE.format(
            balance=_format_amount(forecast_balance),
            months=FORECAST_MONTHS,
        ),
        GREEN_ALERT_STYLE if forecast_balance >= current_balance else RED_ALERT_STYLE,
    )

    return [income_comparison, category_alert, balance_alert, forecast_alert]
