import ttkbootstrap as tb
from ttkbootstrap.constants import *


class ExpenseList:
    def __init__(self, master, initial_balance, expense_start_date, expense_end_date):
        self.master = master
        self.initial_balance = initial_balance
        self.initial_expense_start_date = expense_start_date
        self.initial_expense_end_date = expense_end_date
        self.expense_view = None

    def draw(self):
        table_frame = tb.LabelFrame(self.master, text="Витрати за період", padding=5)
        table_frame.pack(fill=BOTH, expand=True)

        table_container = tb.Frame(table_frame)
        table_container.pack(fill=BOTH, expand=True)

        scrollbar = tb.Scrollbar(table_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.expense_view = tb.Treeview(
            table_container,
            columns=("date", "category", "amount"),
            show="headings",
            height=4,
            yscrollcommand=scrollbar.set,
        )
        scrollbar.configure(command=self.expense_view.yview)
        self.__init_headings()
        self.__init_columns()
        self.update(self.initial_expense_start_date, self.initial_expense_end_date)

    def update(self, start_date=None, end_date=None):
        if self.expense_view is None:
            return
        self.expense_view.delete(*self.expense_view.get_children())
        expenses = self.initial_balance.get_expenses_by_date_range(
            start_date,
            end_date
        )
        for expense in expenses:
            self.expense_view.insert(
                "",
                "end",
                values=(expense.date, expense.category, f"{expense.amount:,.2f} грн"),
            )

    def __init_headings(self):
        self.expense_view.heading("date", text="Дата")
        self.expense_view.heading("category", text="Категорія")
        self.expense_view.heading("amount", text="Сума")

    def __init_columns(self):
        self.expense_view.column("date", width=90, anchor=CENTER)
        self.expense_view.column("category", width=110, anchor=CENTER)
        self.expense_view.column("amount", width=90, anchor=E)
        self.expense_view.pack(side=LEFT, fill=BOTH, expand=True)
