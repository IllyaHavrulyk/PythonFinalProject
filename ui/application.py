import ttkbootstrap as tb
import numpy as np
from constants import *
from ui.charts.graph_chart import GraphChart
from ui.charts.pie_chart import PieChart
from ui.dashboard_alerts import DashboardAlerts
from ui.date_range_selector import DateRangeSelector
from ui.sidebar import Sidebar

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
        self.__configure_grid()
        Sidebar(self.__app_window).draw()
        self.__draw_top_chart()
        self.__draw_pie_chart()
        self.__draw_date_selectors()
        self.__draw_long_chart()
        DashboardAlerts(self.__app_window).draw()

    def start(self):
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
            chart_title="Динаміка балансу",
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
            title="Розподіл витрат",
        ).draw()

    def __draw_date_selectors(self):
        DateRangeSelector(self.__app_window, row=1, column=1, padx=(0, 8)).draw()
        DateRangeSelector(self.__app_window, row=1, column=2, padx=(8, 15)).draw()

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
