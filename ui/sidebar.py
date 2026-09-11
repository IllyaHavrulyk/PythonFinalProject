import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap import Messagebox

from domain.balance import Balance
from domain.expense import Expense
from domain.income import Income
from datetime import date


class Sidebar:
    def __init__(
            self,
            master,
            row=0,
            column=0,
            rowspan=5,
            balance=0,
            expense_categories=None,
            on_expense_added=None,):
        self.master = master
        self.row = row
        self.column = column
        self.rowspan = rowspan
        self.tk_frame = None
        self.balance= balance if hasattr(balance, "get_value") else Balance(balance)
        self.expense_categories = expense_categories or ["Їжа", "Утиль", "Бенз", "Розваги", "Квартира"]
        self.on_expense_added = on_expense_added
        self.lbl_balance = None


    def __format_balance(self):
        return f"Баланс: \n {self.balance.get_value():,.2f} грн"

    def __parse_amount(self, value):
        try:
            amount = float(value.strip().replace(",", "."))
        except ValueError:
            return None
        return amount if amount > 0 else None

    def __center_dialog(self, dialog):
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) / 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) / 2
        dialog.geometry(f"{int(x)}x{int(y)}")

    def __refresh_balance(self):
        self.lbl_balance.configure(text=self.__format_balance())

    def __show_income_dialog(self):
        amount_var = tk.StringVar()
        dialog = tb.Toplevel(self.master)
        dialog.title("Додати дохід")
        dialog.resizable(False, False)
        dialog.transient(self.master)
        dialog.grab_set()

        container = tb.Frame(dialog, padding=24)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)

        tb.Label(container, text="Сума доходу", font=("Helvetica", 12, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )
        entry_amount = tb.Entry(
            container,
            textvariable=amount_var,
            width=28
        )
        entry_amount.grid(row=1, column=0, sticky="w")

        lbl_error = tb.Label(container, bootstyle="danger")
        lbl_error.grid(row=2, column=0, sticky="w")

        def submit():
            amount = self.__parse_amount(amount_var.get())

            if amount is None:
                lbl_error.configure(text="Введіть суму")
                return
            self.balance.add_income(Income(date.today(), amount))
            self.__refresh_balance()
            dialog.destroy()

        tb.Button(container, text="Додати", bootstyle="success-outline", command=submit).grid(
            row=3, column=0, ipady=4, sticky="ew"
        )
        dialog.bind("<Return>", lambda e: submit())
        self.__center_dialog(dialog)
        entry_amount.focus_set()
        self.master.wait_window(dialog)

    def __show_expense_dialog(self):
        amount_var = tk.StringVar()
        category_var = tk.StringVar(value="Їжа")
        dialog = tb.Toplevel(self.master)
        dialog.title("Додати витрату")
        dialog.resizable(False, False)
        dialog.transient(self.master)
        dialog.grab_set()

        container = tb.Frame(dialog, padding=24)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)

        tb.Label(container, text="Категорія", font=("Helvetica", 12, "bold")).grid(
            row=0, column=0, sticky="ew", pady=(0, 8)
        )

        category_box = tb.Combobox(
            container,
            textvariable=category_var,
            values=self.expense_categories,
            state="readonly",
            width=26,
        )
        category_box.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        tb.Label(container, text="Сума витрати", font=("Helvetica", 12, "bold")).grid(
            row=2, column=0, sticky="w", pady=(0, 8)
        )

        entry_amount = tb.Entry(
            container,
            textvariable=amount_var,
            width=28
        )
        entry_amount.grid(row=3, column=0, sticky="w")

        lbl_error = tb.Label(container, bootstyle="danger")
        lbl_error.grid(row=4, column=0, sticky="w")

        def submit():
            amount = self.__parse_amount(amount_var.get())

            if amount is None:
                lbl_error.configure(text="Введіть коректну суму")
                return
            expense = Expense(date.today(), category_var.get(), amount)
            self.balance.add_expense(expense)
            self.__refresh_balance()
            if self.on_expense_added:
                self.on_expense_added()
            dialog.destroy()

        tb.Button(container, text="Додати", bootstyle="danger", command=submit).grid(
            row=5, column=0, ipady=4, sticky="ew"
        )
        dialog.bind("<Return>", lambda e: submit())
        self.__center_dialog(dialog)
        entry_amount.focus_set()
        self.master.wait_window(dialog)

    def draw(self):
        # Buttons and cushion text
        self.tk_frame = tb.Frame(self.master, padding=(15, 18))
        self.tk_frame.grid(row=0, column=0, rowspan=5, sticky="nsew")
        self.tk_frame.columnconfigure(0, weight=1)

        btn_expense = tb.Button(self.tk_frame, text="Витрата",
                                bootstyle="danger-outline",
                                command=self.__show_expense_dialog)
        btn_expense.grid(row=0, column=0, pady=(0, 12), ipady=8, sticky="ew")

        btn_income = tb.Button(self.tk_frame,
                               text="Дохід",
                               bootstyle="success-outline",
                               command=self.__show_income_dialog)
        btn_income.grid(row=1, column=0, pady=12, ipady=8, sticky="ew")

        btn_export = tb.Button(self.tk_frame, text="Експорт (CSV)", bootstyle="warning-outline")
        btn_export.grid(row=2, column=0, pady=12, ipady=8, sticky="ew")

        self.lbl_balance = tb.Label(
            self.tk_frame,
            text=self.__format_balance(),
            font=("Helvetica", 12, "bold"),
            justify="center",
        )
        self.lbl_balance.grid(row=3, column=0, pady=(28, 10), sticky="ew")

        lbl_cushion = tb.Label(
            self.tk_frame,
            text="Подушка безпеки:\n1000 грн",
            font=("Helvetica", 12, "bold"),
            justify="center",
        )
        lbl_cushion.grid(row=4, column=0, pady=(28, 10), sticky="ew")
        return self
