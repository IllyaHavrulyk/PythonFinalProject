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
