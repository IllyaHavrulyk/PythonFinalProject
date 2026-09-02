from domain import expense


class Balance:
    def __init__(self, value):
        self.__value = value
        self.__expenses = []
        self.__incomes = []

    def get_value(self):
        return self.__value

    def get_expenses(self):
        return self.__expenses

    def add_expense(self, expense):
        self.__expenses.append(expense)
        self.__value -= expense.amount

    def add_income(self, income):
        self.__incomes.append(income)
        self.__value += income.amount

    def get_incomes(self):
        return self.__incomes

    def get_expenses_by_date_range(self, start_date=None, end_date=None):
        return [
            expense
            for expense in self.get_expenses()
            if (start_date is None or expense.date >= start_date)
            and (end_date is None or expense.date <= end_date)
        ]

    def get_expense_totals_by_category(self, start_date=None, end_date=None):
        totals = {}
        for expense in self.get_expenses_by_date_range(start_date, end_date):
            totals[expense.category] = totals.get(expense.category, 0) + expense.amount
        return totals