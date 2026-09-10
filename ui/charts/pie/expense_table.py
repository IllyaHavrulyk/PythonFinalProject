import ttkbootstrap as tb
from ttkbootstrap.constants import *

from calculations.expense_utils import get_expenses_by_date_range
from constants import (
    AMOUNT_COLUMN_WIDTH,
    AMOUNT_HEADING,
    CATEGORY_COLUMN_WIDTH,
    CATEGORY_HEADING,
    CURRENCY_LABEL,
    DATE_COLUMN_WIDTH,
    DATE_HEADING,
    EXPENSE_AMOUNT_TEXT_TEMPLATE,
    EXPENSE_TABLE_HEIGHT,
    EXPENSE_TABLE_TITLE,
    PANEL_PADDING,
)


class ExpenseTable:
    def __init__(self, master, initial_balance, expense_start_date, expense_end_date):
        self.initial_expense_start_date = expense_start_date
        self.initial_expense_end_date = expense_end_date
        self.initial_balance = initial_balance
        self.master = master
        self.expense_view = None

    def draw(self):
        table_frame = tb.LabelFrame(
            self.master,
            text=EXPENSE_TABLE_TITLE,
            padding=PANEL_PADDING,
        )
        table_frame.pack(fill=BOTH, expand=True)

        table_container = tb.Frame(table_frame)
        table_container.pack(fill=BOTH, expand=True)

        scrollbar = tb.Scrollbar(table_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.expense_view = tb.Treeview(
            table_container,
            columns=("date", "category", "amount"),
            show="headings",
            height=EXPENSE_TABLE_HEIGHT,
            yscrollcommand=scrollbar.set,
        )
        scrollbar.configure(command=self.expense_view.yview)
        self.__init_headings()
        self.__init_columns()
        self.update(self.initial_balance.get_expenses(), self.initial_expense_start_date, self.initial_expense_end_date)

    def __init_headings(self):
        self.expense_view.heading("date", text=DATE_HEADING)
        self.expense_view.heading("category", text=CATEGORY_HEADING)
        self.expense_view.heading("amount", text=AMOUNT_HEADING)

    def __init_columns(self):
        self.expense_view.column("date", width=DATE_COLUMN_WIDTH, anchor=CENTER)
        self.expense_view.column("category", width=CATEGORY_COLUMN_WIDTH, anchor=CENTER)
        self.expense_view.column("amount", width=AMOUNT_COLUMN_WIDTH, anchor=E)
        self.expense_view.pack(side=LEFT, fill=BOTH, expand=True)

    def update(self, filtered_expenses, start_date=None, end_date=None):
        if self.expense_view is None:
            return
        self.expense_view.delete(*self.expense_view.get_children())
        filtered_expenses = get_expenses_by_date_range(
            filtered_expenses,
            start_date,
            end_date
        )
        for expense in filtered_expenses:
            self.expense_view.insert(
                "",
                "end",
                values=(
                    expense.date,
                    expense.category,
                    EXPENSE_AMOUNT_TEXT_TEMPLATE.format(
                        amount=expense.amount,
                        currency=CURRENCY_LABEL,
                    ),
                ),
            )
