import ttkbootstrap as tb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg as tkAgg
import numpy as np
from constants import *
from utils import style_chart
from ui.alert import Alert
from ttkbootstrap import Messagebox

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
        self.__draw_sidebar()
        self.__draw_top_chart()
        self.__draw_pie_chart()
        self.__draw_date_selectors()
        self.__draw_long_chart()
        self.__draw_alerts(self.__app_window)

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

    def __draw_sidebar(self):
        
        
        # Buttons and cushion text
        sidebar = tb.Frame(self.__app_window, padding=(15, 18))
        sidebar.grid(row=0, column=0, rowspan=5, sticky="nsew")
        sidebar.columnconfigure(0, weight=1)

        btn_expense = tb.Button(sidebar, text="Витрата", bootstyle="danger-outline", command=lambda: Messagebox.show_info("Витрата", "Функція додавання витрати ще не реалізована."))
        btn_expense.grid(row=0, column=0, pady=(0, 12), ipady=8, sticky="ew")

        btn_income = tb.Button(sidebar, text="Дохід", bootstyle="success-outline")
        btn_income.grid(row=1, column=0, pady=12, ipady=8, sticky="ew")

        btn_export = tb.Button(sidebar, text="Експорт (CSV)", bootstyle="warning-outline")
        btn_export.grid(row=2, column=0, pady=12, ipady=8, sticky="ew")

        lbl_cushion = tb.Label(
            sidebar,
            text="Подушка безпеки:\n1000 грн",
            font=("Helvetica", 12, "bold"),
            justify="center",
        )
        lbl_cushion.grid(row=3, column=0, pady=(28, 10), sticky="ew")

    def __draw_top_chart(self):
        # Top dashboard matplotlib charts
        frame_top_chart = tb.LabelFrame(self.__app_window, text="Динаміка балансу", padding=5)
        frame_top_chart.grid(row=0, column=1, padx=(0, 8), pady=10, sticky="nsew")

        # Matplotlib line chart figure and axis
        fig_line, ax_line = plt.subplots(figsize=(4, 2), dpi=100)
        x_data = ["Лют", "Бер", "Кві", "Тра", "Чер", "Лип", "Сер"]
        y_data = np.array([14500, 13200, 15800, 12100, 13900, 16700, 18400])
        ax_line.plot(x_data, y_data, color=SOLAR_YELLOW, linewidth=2.5)
        ax_line.set_title("Динаміка балансу", fontsize=10)
        ax_line.set_ylabel("Баланс, грн")
        style_chart(fig_line, ax_line)

        # Render line chart figure into tkinter
        canvas_line = tkAgg.FigureCanvasTkAgg(fig_line, master=frame_top_chart)
        canvas_line.get_tk_widget().pack(fill=BOTH, expand=True)

    def __draw_pie_chart(self):
        # Pie chart frame
        frame_pie_chart = tb.LabelFrame(self.__app_window, text="Розподіл витрат", padding=5)
        frame_pie_chart.grid(row=0, column=2, padx=(8, 15), pady=10, sticky="nsew")

        # Matplotlib pie chart figure and axis
        fig_pie, ax_pie = plt.subplots(figsize=(3, 2), dpi=100)
        labels = ["Їжа", "Утиль", "Бенз", "Розваги", "Квартира"]
        colors = ["#cb4b16", "#2aa198", "#b58900", "#6c71c4", "#d33682"]
        sizes = [30, 20, 15, 15, 20]
        _, pie_labels, percentages = ax_pie.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct="%1.0f%%",
            startangle=90,
            wedgeprops={"edgecolor": SOLAR_PANEL},
        )
        fig_pie.patch.set_facecolor(SOLAR_PANEL)
        ax_pie.set_facecolor(SOLAR_PANEL)
        for pie_text in pie_labels + percentages:
            pie_text.set_color(SOLAR_TEXT)
        ax_pie.axis("equal")

        # Render pie figure
        canvas_pie = tkAgg.FigureCanvasTkAgg(fig_pie, master=frame_pie_chart)
        canvas_pie.get_tk_widget().pack(fill=BOTH, expand=True)

    def __draw_date_selectors(self):
        # Date selector
        frame_dates_center = tb.Frame(self.__app_window)
        frame_dates_center.grid(row=1, column=1, padx=(0, 8), pady=5, sticky="ew")
        tb.Label(frame_dates_center, text="від").pack(side=LEFT)
        tb.DateEntry(frame_dates_center, width=10).pack(side=LEFT, expand=True, padx=5)
        tb.Label(frame_dates_center, text="до").pack(side=LEFT)
        tb.DateEntry(frame_dates_center, width=10).pack(side=LEFT, expand=True, padx=5)

        # Date selector
        frame_dates_pie = tb.Frame(self.__app_window)
        frame_dates_pie.grid(row=1, column=2, padx=(8, 15), pady=5, sticky="ew")
        tb.Label(frame_dates_pie, text="від").pack(side=LEFT)
        tb.DateEntry(frame_dates_pie, width=10).pack(side=LEFT, expand=True, padx=5)
        tb.Label(frame_dates_pie, text="до").pack(side=LEFT)
        tb.DateEntry(frame_dates_pie, width=10).pack(side=LEFT, expand=True, padx=5)

    def __draw_long_chart(self):
        # Create frame for long chart
        frame_long_chart = tb.LabelFrame(self.__app_window, text="Майбутній баланс", padding=5)
        frame_long_chart.grid(row=2, column=1, columnspan=2, padx=(0, 15), pady=10, sticky="nsew")

        # Create figure and axis for long chart
        fig_long, ax_long = plt.subplots(figsize=(8, 1.5), dpi=100, constrained_layout=True)
        future_months = ["Вер", "Жов", "Лис", "Гру", "Січ", "Лют"]
        month_numbers = np.arange(len(future_months))
        monthly_changes = np.random.default_rng().integers(-1500, 2500, size=6)
        future_balance = 18400 + np.cumsum(monthly_changes)
        ax_long.plot(month_numbers, future_balance, color=SOLAR_YELLOW, linewidth=2)
        ax_long.fill_between(month_numbers, future_balance, color=SOLAR_YELLOW, alpha=0.3)
        ax_long.set_xticks(month_numbers, future_months)
        ax_long.set_ylabel("грн")
        style_chart(fig_long, ax_long)

        # Render long canvas
        canvas_long = tkAgg.FigureCanvasTkAgg(fig_long, master=frame_long_chart)
        canvas_long.get_tk_widget().pack(fill=BOTH, expand=TRUE)

    def __draw_alerts(self, app):
        # Render alerts
        spend_income_diff_alert = Alert(app, SPEND_INCOME_DIFF_TEXT_TEMPLATE, ORANGE_ALERT_STYLE, 3, 1).draw()
        spend_increase_alert = Alert(app, SPEND_DIFF_TEXT_TEMPLATE, ORANGE_ALERT_STYLE, 3, 2).draw()
        balance_growth_alert = Alert(app, BALANCE_GROWTH_TEXT_TEMPLATE, RED_ALERT_STYLE, 4, 1).draw()
        spend_decrease_alert = Alert(app, SPEND_DIFF_TEXT_TEMPLATE, GREEN_ALERT_STYLE, 4, 2).draw()
