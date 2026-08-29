import ttkbootstrap as tb
from ttkbootstrap import Messagebox


class Sidebar:
    def __init__(self, master, row=0, column=0, rowspan=5, balance=0):
        self.master = master
        self.row = row
        self.column = column
        self.rowspan = rowspan
        self.balance = balance
        self.tk_frame = None

    def __show_expense_info(self):
        Messagebox.show_info("Витрата", "Функція додавання витрати ще не реалізована.")

    def draw(self):
        self.tk_frame = tb.Frame(self.master, padding=(15, 18))
        self.tk_frame.grid(row=self.row, column=self.column, rowspan=self.rowspan, sticky="nsew")
        self.tk_frame.columnconfigure(0, weight=1)

        btn_expense = tb.Button(
            self.tk_frame,
            text="Витрата",
            bootstyle="danger-outline",
            command=self.__show_expense_info,
        )
        btn_expense.grid(row=0, column=0, pady=(0, 12), ipady=8, sticky="ew")

        btn_income = tb.Button(self.tk_frame, text="Дохід", bootstyle="success-outline")
        btn_income.grid(row=1, column=0, pady=12, ipady=8, sticky="ew")

        btn_export = tb.Button(self.tk_frame, text="Експорт (CSV)", bootstyle="warning-outline")
        btn_export.grid(row=2, column=0, pady=12, ipady=8, sticky="ew")

        lbl_balance = tb.Label(
            self.tk_frame,
            text=f"Баланс:\n{self.balance:,.2f} грн",
            font=("Helvetica", 12, "bold"),
            justify="center",
        )
        lbl_balance.grid(row=3, column=0, pady=(28, 10), sticky="ew")

        lbl_cushion = tb.Label(
            self.tk_frame,
            text="Подушка безпеки:\n1000 грн",
            font=("Helvetica", 12, "bold"),
            justify="center",
        )
        lbl_cushion.grid(row=4, column=0, pady=(16, 10), sticky="ew")
        return self
