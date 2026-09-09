import numpy as np
import ttkbootstrap as tb

from calculations.expense_utils import get_expense_totals_by_category
from constants import EXPENSE_CATEGORIES, EXPENSE_COLORS
from domain.balance import Balance
from ui.charts.graph_chart import GraphChart
from ui.charts.pie.expense_table import ExpenseTable
from ui.charts.pie.pie_chart import PieChart
from ui.dashboard_alerts import DashboardAlerts
from ui.date_range_selector import DateRangeSelector
from ui.popup.initial_balance_window import InitialBalanceWindow
from ui.sidebar import Sidebar


class MainWindow:
    def __init__(self, app_name, geometry):
        self.expense_end_date = None
        self.expense_start_date = None
        self.app_name = app_name
        self.geometry = geometry
        self.window = None
        self.initial_balance = None
        self.sidebar = None
        self.pie_chart = None
        self.expense_table = None


    def init_window(self):
        self.window = tb.Window(themename="solar")
        self.window.title(self.app_name)
        self.window.geometry(self.geometry)
        self.window.minsize(1050, 700)
        self.window.withdraw()

    def setup(self):
        self.init_window()
        self.initial_balance = Balance(self.__ask_initial_balance())
        self.__configure_grid()
        self.__draw_sidebar()
        self.__draw_top_chart()

        self.__draw_pie_chart()
        self.__draw_date_selectors()
        self.__draw_long_chart()
        self.__draw_dashboard_alerts()

        self.window.deiconify()

    def __ask_initial_balance(self):
        initial_balance_window = InitialBalanceWindow(self.window).draw()
        return initial_balance_window.get_result()
    
    def __configure_grid(self):
        # Keep navigation in its own column. The chart columns are the only columns
        # that grow when the window is maximized.
        self.window.columnconfigure(0, weight=0, minsize=220)
        self.window.columnconfigure((1, 2), weight=1, uniform="charts")
        self.window.rowconfigure(0, weight=4)
        self.window.rowconfigure(1, weight=0, minsize=150)
        self.window.rowconfigure(2, weight=0, minsize=180)
        self.window.rowconfigure((3, 4), weight=0)

    def __draw_sidebar(self):
        self.sidebar = Sidebar(
            self.window,
            balance=self.initial_balance,
            expense_categories=EXPENSE_CATEGORIES,
            on_expense_added=self.__update_pie_chart
        )
        self.sidebar.draw()

    def __update_pie_chart(self):
        expense_totals, expense_categories, expense_colors = self.__get_expense_chart_data()
        self.pie_chart.update_data(expense_totals, expense_categories, expense_colors)
        self.expense_table.update(self.initial_balance.get_expenses(), self.expense_start_date, self.expense_end_date)

    def __get_expense_chart_data(self):
        totals_by_category = get_expense_totals_by_category(
            self.initial_balance.get_expenses(),
            self.expense_start_date,
            self.expense_end_date
        )

        categories = [
            category
            for category in EXPENSE_CATEGORIES
            if totals_by_category.get(category, 0) > 0
        ]

        sizes = [totals_by_category[category] for category in categories]
        colors = [EXPENSE_COLORS[category] for category in categories]
        return sizes, categories, colors

    def __draw_top_chart(self):
        x_data = ["Лют", "Бер", "Кві", "Тра", "Чер", "Лип", "Сер"]
        y_data = np.array([14500, 13200, 15800, 12100, 13900, 16700, 18400])
        self.top_chart = GraphChart(
            row=0,
            column=1,
            x_data=x_data,
            y_data=y_data,
            master=self.window,
            title="Динаміка балансу",
            y_label="Баланс, грн",
            figsize=(4, 2),
            padx=(0, 8),
            chart_title="Динаміка балансу"
        )
        self.top_chart.draw()

    def __draw_pie_chart(self):
        expense_totals, expense_categories, expense_colors = self.__get_expense_chart_data()
        self.pie_chart = PieChart(
            row=0,
            column=2,
            sizes=expense_totals,
            master=self.window,
            categories=expense_categories,
            colors=expense_colors,
            title="Розподіл витрат"
        ).draw()

    def __draw_date_selectors(self):
        # Date selector
        DateRangeSelector(self.window, row=1, column=1, padx=(0, 8)).draw()
        self.pie_date_selector = DateRangeSelector(
            self.window,
            row=1,
            column=2,
            padx=(8, 15),
            on_change=self.__set_expense_filter,
            show_apply=True
        ).draw()
        self.expense_start_date, self.expense_end_date = self.pie_date_selector.get_date_range()
        self.__draw_expense_table(self.pie_date_selector.tk_frame)
        self.__update_pie_chart()
        # Date selector

    def __draw_expense_table(self, master):
        self.expense_table = ExpenseTable(master, self.initial_balance, self.expense_start_date, self.expense_end_date)
        self.expense_table.draw()

    def __set_expense_filter(self, start_date, end_date):
        self.expense_start_date = start_date
        self.expense_end_date = end_date
        self.__update_pie_chart()

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
            master=self.window,
            title="Майбутній баланс",
            y_label="грн",
            figsize=(8, 1.5),
            padx=(0, 15),
            constrained_layout=True,
            fill_area=True,
            x_tick_labels=future_months,
            line_width=2,
        ).draw()

    def __draw_dashboard_alerts(self):
        self.dashboard_alerts = DashboardAlerts(self.window)
        self.dashboard_alerts.draw()

    def start(self):
        self.setup()
        self.window.mainloop()
