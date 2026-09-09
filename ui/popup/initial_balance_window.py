import numpy as np
import ttkbootstrap as tb
from ttkbootstrap.constants import *

import tkinter as tk

from calculations.expense_utils import get_expense_totals_by_category
from constants import *
from domain.balance import Balance
from ui.charts.graph_chart import GraphChart
from ui.charts.pie.expense_table import ExpenseTable
from ui.charts.pie.pie_chart import PieChart
from ui.dashboard_alerts import DashboardAlerts
from ui.date_range_selector import DateRangeSelector
from ui.sidebar import Sidebar


class InitialBalanceWindow():
    def __init__(self, master):
        self.master = master
        self.balance_var = tb.StringVar(value="0")
        self.result = {"balance": float(0)}
        self.lbl_error = None
        self.dialog = None

    def draw(self):
        self.dialog = tb.Toplevel(self.master)
        self.dialog.withdraw()
        self.dialog.title("Початковий баланс")
        self.dialog.resizable(False, False)

        container = tb.Frame(self.dialog, padding=24)
        container.grid(column=0, row=0, sticky="nsew")
        container.columnconfigure(0, weight=1)

        lbl_title = tb.Label(
            container,
            text="Введіть початковий баланс",
            font=("Helvetica", 13, "bold"),
        )
        lbl_title.grid(column=0, row=0, pady=(0, 12), sticky="nsew")

        entry_balance = tb.Entry(container, textvariable=self.balance_var, width=28)
        entry_balance.grid(column=1, row=0, pady=(0, 8), sticky="ew")

        self.lbl_error = tb.Label(
            container,
            bootstyle="danger"
        )
        self.lbl_error.grid(column=0, row=1, pady=(0, 12), sticky="w")

        btn_start = tb.Button(
            container,
            text="Почати",
            bootstyle="success",
            command=self.submit
        )
        btn_start.grid(row=3, column=0, ipady=4, sticky="ew")

        self.dialog.bind("<Return>", lambda _event: self.submit())
        self.dialog.protocol("WM_DELETE_WINDOW", self.dialog.destroy)

        entry_balance.focus_set()
        entry_balance.selection_range(0, tk.END)

        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_width()) // 2
        y = (self.dialog.winfo_screenheight() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"{int(x)}x{int(y)}")
        self.dialog.deiconify()
        self.dialog.lift()

        try:
            self.dialog.attributes("-topmost", True)
            self.dialog.after(250, self.disable_topmost)
        except tk.TclError:
            pass

        self.dialog.grab_set()
        entry_balance.focus_force()
        self.master.wait_window(self.dialog)
        return self

    def get_result(self):
        return self.result["balance"]

    def submit(self):
        entered_balance = self.balance_var.get().strip().replace(",", ".")
        try:
            self.result["balance"] = float(entered_balance)
        except ValueError:
            self.lbl_error.configure(text="Введіть коректне число")
            return
        self.dialog.destroy()

    def disable_topmost(self):
        if self.dialog.winfo_exists():
            self.dialog.attributes("-topmost", False)

