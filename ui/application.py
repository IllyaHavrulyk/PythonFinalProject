import matplotlib.backends.backend_tkagg as tkAgg
import matplotlib.pyplot as plt
import numpy as np
import ttkbootstrap as tb
from ttkbootstrap import Messagebox
from ttkbootstrap.constants import *

import tkinter as tk

from constants import *
from ui.alert import Alert
from ui.charts.graph_chart import GraphChart
from ui.charts.pie_chart import PieChart
from ui.dashboard_alerts import DashboardAlerts
from ui.date_range_selector import DateRangeSelector
from ui.sidebar import Sidebar
from utils import style_chart


class Application:
    def __init__(self, app_name, geometry):
        self.__app_window = None
        self.app_name = app_name
        self.geometry = geometry

    # Initializing graphic elements
    def initialize(self):
        app_window = tb.Window(themename="solar")
        app_window.title(self.app_name)
        app_window.geometry(self.geometry)
        app_window.minsize(1050, 700)
        self.__app_window = app_window

    def __initialize_balance(self):
        self.initial_balance = self.__ask_initial_balance()
        self.__configure_grid()
        Sidebar(self.__app_window, balance=self.initial_balance).draw()
        self.__draw_top_chart()
        self.__draw_pie_chart()
        self.__draw_date_selectors()
        self.__draw_long_chart()
        DashboardAlerts(self.__app_window).draw()
        self.__app_window.deiconify()


    def __ask_initial_balance(self):
        balance_var = tb.StringVar(value="0")
        result = {"balance": float(0)}

        dialog = tb.Toplevel(self.__app_window)
        dialog.withdraw()
        dialog.title("Початковий баланс")
        dialog.resizable(False, False)

        container = tb.Frame(dialog, padding=24)
        container.grid(column=0, row=0, sticky="nsew")
        container.columnconfigure(0, weight=1)

        lbl_title = tb.Label(
            container,
            text="Введіть початковий баланс",
            font=("Helvetica", 13, "bold"),
        )
        lbl_title.grid(column=0, row=0, pady=(0,12), sticky="nsew")

        entry_balance = tb.Entry(container, textvariable=balance_var, width=28)
        entry_balance.grid(column=1, row=0, pady=(0,8), sticky="ew")

        lbl_error = tb.Label(
            container,
            bootstyle="danger"
        )
        lbl_error.grid(column=0, row=1, pady=(0,12), sticky="w")

        def submit():
            entered_balance = balance_var.get().strip().replace(",", ".")
            try:
                result["balance"] = float(entered_balance)
            except ValueError:
                lbl_error.configure(text="Введіть коректне число")
            dialog.destroy()

        btn_start = tb.Button(
            container,
            text="Почати",
            bootstyle="success",
            command=submit
        )
        btn_start.grid(row=3, column=0, ipady=4, sticky="ew")

        dialog.bind("<Return>", lambda _event: submit())
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

        entry_balance.focus_set()
        entry_balance.selection_range(0, tk.END)

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry("+{}+{}".format(x, y))
        dialog.deiconify()
        dialog.lift()

        def disable_topmost():
            if dialog.winfo_exists():
                dialog.attributes("-topmost", False)

        try:
            dialog.attributes("-topmost", True)
            dialog.after(250, disable_topmost)
        except tk.TclError:
            pass

        dialog.grab_set()
        entry_balance.focus_force()
        self.__app_window.wait_window(dialog)
        return result["balance"]

    def start(self):
        self.__app_window.after(100, self.__initialize_balance)
        self.__app_window.mainloop()

    def __configure_grid(self):
        # Keep navigation in its own column. The chart columns are the only columns
        # that grow when the window is maximized.
        self.__app_window.columnconfigure(0, weight=0, minsize=220)
        self.__app_window.columnconfigure((1, 2), weight=1, uniform="charts")
        self.__app_window.rowconfigure(0, weight=4)
        self.__app_window.rowconfigure(1, weight=0)
        self.__app_window.rowconfigure(2, weight=0, minsize=180)
        self.__app_window.rowconfigure((3, 4), weight=0)

    def __draw_top_chart(self):
        x_data = ["Лют", "Бер", "Кві", "Тра", "Чер", "Лип", "Сер"]
        y_data = np.array([14500, 13200, 15800, 12100, 13900, 16700, 18400])
        GraphChart(
            row=0,
            column=1,
            x_data=x_data,
            y_data=y_data,
            master=self.__app_window,
            title="Динаміка балансу",
            y_label="Баланс, грн",
            figsize=(4, 2),
            padx=(0, 8),
            chart_title="Динаміка балансу"
        ).draw()

    def __draw_pie_chart(self):
        expense_categories = ["Їжа", "Утиль", "Бенз", "Розваги", "Квартира"]
        expense_colors = [PIE_RED, PIE_BLUE, PIE_YELLOW, PIE_PURPLE, PIE_PINK]
        expense_percentages = [30, 20, 15, 15, 20]
        PieChart(
            row=0,
            column=2,
            sizes=expense_percentages,
            master=self.__app_window,
            categories=expense_categories,
            colors=expense_colors,
            title="Розподіл витрат"
        ).draw()

    def __draw_date_selectors(self):
        # Date selector
        DateRangeSelector(self.__app_window, row=1, column=1, padx=(0, 8)).draw()
        DateRangeSelector(self.__app_window, row=1, column=2, padx=(8, 15)).draw()
        # Date selector

    def __draw_long_chart(self):
        future_months = ["Вер", "Жов", "Лис", "Гру", "Січ", "Лют"]
        month_numbers = np.arange(len(future_months))
        monthly_changes = np.random.default_rng().integers(-1500, 2500, size=6)
        future_balance = 18400 + np.cumsum(monthly_changes)
        GraphChart(
            row=2,
            column=1,
            columnspan=2,
            x_data=month_numbers,
            y_data=future_balance,
            master=self.__app_window,
            title="Майбутній баланс",
            y_label="грн",
            figsize=(8, 1.5),
            padx=(0, 15),
            constrained_layout=True,
            fill_area=True,
            x_tick_labels=future_months,
            line_width=2,
        ).draw()


