def get_expenses_by_date_range(expenses, start_date=None, end_date=None):
    return [
        expense
        for expense in expenses
        if (start_date is None or expense.date >= start_date)
           and (end_date is None or expense.date <= end_date)
    ]

def get_expense_totals_by_category(expenses, start_date=None, end_date=None):
    totals = {}
    for expense in get_expenses_by_date_range(expenses, start_date, end_date):
        totals[expense.category] = totals.get(expense.category, 0) + expense.amount
    return totals



