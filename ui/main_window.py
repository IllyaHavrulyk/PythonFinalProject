import ttkbootstrap as tb

from calculations.dashboard_utils import calculate_balance_forecast, get_future_month_labels
from calculations.expense_utils import get_expense_totals_by_category, filter_balance_snapshots
from config import APP_MODE, RESET_DATA_ON_START
from constants import (
    APP_MIN_HEIGHT,
    APP_MIN_WIDTH,
    APP_THEME,
    BALANCE_AXIS_LABEL,
    DATE_CONTROLS_MIN_HEIGHT,
    EXPENSE_CHART_TITLE,
    EXPENSE_CATEGORIES,
    EXPENSE_COLORS,
    FORECAST_CHART_FIGURE_SIZE,
    FORECAST_CHART_MIN_HEIGHT,
    FORECAST_CHART_PADDING,
    FORECAST_CHART_TITLE,
    FORECAST_LINE_WIDTH,
    LEFT_CHART_PADDING,
    RIGHT_PANEL_PADDING,
    SIDEBAR_MIN_WIDTH,
    TOP_CHART_FIGURE_SIZE,
    TOP_CHART_TITLE,
    CURRENCY_AXIS_LABEL,
)
from services.finance_service import FinanceService
from ui.charts.graph_chart import GraphChart
from ui.charts.pie.expense_table import ExpenseTable
from ui.charts.pie.pie_chart import PieChart
from ui.dashboard_alerts import DashboardAlerts
from ui.date_range_selector import DateRangeSelector
from ui.popup.initial_balance_window import InitialBalanceWindow
from ui.sidebar import Sidebar


class MainWindow:
    def __init__(
            self,
            app_name,
            geometry,
            finance_service: FinanceService,
            app_mode=APP_MODE,
            reset_data_on_start=RESET_DATA_ON_START):
        self.expense_end_date = None
        self.expense_start_date = None
        self.app_name = app_name
        self.geometry = geometry
        self.window = None
        self.balance = None
        self.sidebar = None
        self.pie_chart = None
        self.expense_table = None
        self.future_chart = None
        self.dashboard_alerts = None
        self.app_mode = app_mode
        self.reset_data_on_start = reset_data_on_start
        self.finance_service = finance_service

    def _init_window(self):
        self.window = tb.Window(themename=APP_THEME)
        self.window.title(self.app_name)
        self.window.geometry(self.geometry)
        self.window.minsize(APP_MIN_WIDTH, APP_MIN_HEIGHT)
        self.window.withdraw()

    def setup(self):
        self._init_window()
        self.balance = self.finance_service.initialize(
            self.app_mode,
            self.reset_data_on_start,
        )
        if self.balance is None:
            initial_balance = self._ask_initial_balance()
            if initial_balance is None:
                self.window.destroy()
                return False
            self.balance = self.finance_service.initialize(
                self.app_mode,
                self.reset_data_on_start,
                initial_balance,
            )
        self._configure_grid()
        self._draw_sidebar()
        self._draw_top_chart()

        self._draw_pie_chart()
        self._draw_date_selectors()
        self._draw_long_chart()
        self._draw_dashboard_alerts()

        self.window.deiconify()
        return True

    def _ask_initial_balance(self):
        initial_balance_window = InitialBalanceWindow(self.window).draw()
        return initial_balance_window.get_result()

    def _configure_grid(self):
        # Keep navigation in its own column. The chart columns are the only columns
        # that grow when the window is maximized.
        self.window.columnconfigure(0, weight=0, minsize=SIDEBAR_MIN_WIDTH)
        self.window.columnconfigure((1, 2), weight=1, uniform="charts")
        self.window.rowconfigure(0, weight=4)
        self.window.rowconfigure(1, weight=0, minsize=DATE_CONTROLS_MIN_HEIGHT)
        self.window.rowconfigure(2, weight=0, minsize=FORECAST_CHART_MIN_HEIGHT)
        self.window.rowconfigure((3, 4), weight=0)

    def _draw_sidebar(self):
        self.sidebar = Sidebar(
            self.window,
            finance_service=self.finance_service,
            expense_categories=self.finance_service.get_categories(),
            on_balance_changed=self.update_charts,
        )
        self.sidebar.draw()

    def update_charts(self):
        expense_totals, expense_categories, expense_colors = self._get_expense_chart_data()
        filtered_snapshots = filter_balance_snapshots(self.balance.get_value_snapshots())
        self.pie_chart.update(expense_totals, expense_categories, expense_colors)
        self.expense_table.update(self.balance.get_expenses(), self.expense_start_date, self.expense_end_date)
        self.top_chart.update(filtered_snapshots.keys(), filtered_snapshots.values())
        if self.future_chart is not None:
            future_balance = calculate_balance_forecast(self.balance)
            self.future_chart.update(range(len(future_balance)), future_balance)
        if self.dashboard_alerts is not None:
            self.dashboard_alerts.update()
    def _get_expense_chart_data(self):
        totals_by_category = get_expense_totals_by_category(
            self.balance.get_expenses(),
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

    def _draw_top_chart(self):
        filtered_snapshots = filter_balance_snapshots(self.balance.get_value_snapshots())
        self.top_chart = GraphChart(
            row=0,
            column=1,
            x_data=filtered_snapshots.keys(),
            y_data=filtered_snapshots.values(),
            master=self.window,
            title=TOP_CHART_TITLE,
            y_label=BALANCE_AXIS_LABEL,
            figsize=TOP_CHART_FIGURE_SIZE,
            padx=LEFT_CHART_PADDING,
        )
        self.top_chart.draw()

    def _draw_pie_chart(self):
        expense_totals, expense_categories, expense_colors = self._get_expense_chart_data()
        self.pie_chart = PieChart(
            row=0,
            column=2,
            sizes=expense_totals,
            master=self.window,
            categories=expense_categories,
            colors=expense_colors,
            title=EXPENSE_CHART_TITLE,
        ).draw()

    def _draw_date_selectors(self):
        # Date selector
        self.expense_date_selector = DateRangeSelector(
            self.window,
            row=1,
            column=2,
            padx=RIGHT_PANEL_PADDING,
            on_change=self._set_expense_filter,
            show_apply=True
        ).draw()
        self.expense_start_date, self.expense_end_date = self.expense_date_selector.get_date_range()
        self._draw_expense_table(self.expense_date_selector.tk_frame)
        self.update_charts()
        # Date selector

    def _draw_expense_table(self, master):
        self.expense_table = ExpenseTable(master, self.balance, self.expense_start_date, self.expense_end_date)
        self.expense_table.draw()

    def _set_expense_filter(self, start_date, end_date):
        self.expense_start_date = start_date
        self.expense_end_date = end_date
        self.update_charts()

    def _draw_long_chart(self):
        future_months = get_future_month_labels()
        month_numbers = range(len(future_months))
        future_balance = calculate_balance_forecast(self.balance)
        self.future_chart = GraphChart(
            row=2,
            column=1,
            columnspan=2,
            x_data=month_numbers,
            y_data=future_balance,
            master=self.window,
            title=FORECAST_CHART_TITLE,
            y_label=CURRENCY_AXIS_LABEL,
            figsize=FORECAST_CHART_FIGURE_SIZE,
            padx=FORECAST_CHART_PADDING,
            constrained_layout=True,
            fill_area=True,
            x_tick_labels=future_months,
            line_width=FORECAST_LINE_WIDTH,
        ).draw()

    def _draw_dashboard_alerts(self):
        self.dashboard_alerts = DashboardAlerts(self.window, self.balance)
        self.dashboard_alerts.draw()

    def start(self):
        if self.setup():
            self.window.mainloop()
