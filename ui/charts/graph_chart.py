import matplotlib.backends.backend_tkagg as tkAgg
import matplotlib.pyplot as plt
import ttkbootstrap as tb
from ttkbootstrap.constants import *

from constants import (
    CHART_DPI,
    CHART_FILL_ALPHA,
    CHART_TITLE_FONT_SIZE,
    CHART_VERTICAL_PADDING,
    DEFAULT_LINE_WIDTH,
    NO_GRAPH_DATA_TEXT,
    PANEL_PADDING,
    SOLAR_TEXT,
    SOLAR_YELLOW,
)
from utils import style_chart


class GraphChart:
    def __init__(self, row, column, x_data,
                 y_data, master, title,
                 y_label, figsize, padx,
                 columnspan=1,
                 constrained_layout=False,
                 line_width=DEFAULT_LINE_WIDTH,
                 fill_area=False,
                 x_tick_labels=None,
                 chart_title=None
                 ):
        self.y_label = y_label
        self.chart_title = chart_title
        self.x_tick_labels = x_tick_labels
        self.fill_area = fill_area
        self.line_width = line_width
        self.constrained_layout = constrained_layout
        self.figsize = figsize
        self.padx = padx
        self.column = column
        self.row = row
        self.columnspan = columnspan
        self.initial_x_data = x_data
        self.initial_y_data = y_data
        self.title = title
        self.master = master
        self.tk_frame = None
        self.tk_canvas = None
        self.figure = None
        self.axis = None

    def draw(self):
        # Top dashboard matplotlib charts
        self.tk_frame = tb.LabelFrame(
            self.master,
            text=self.title,
            padding=PANEL_PADDING,
        )
        self.tk_frame.grid(
            row=self.row,
            column=self.column,
            columnspan=self.columnspan,
            padx=self.padx,
            pady=CHART_VERTICAL_PADDING,
            sticky="nsew"
        )

        self.__prepare_plot()
        self.__plot_data(self.initial_x_data, self.initial_y_data)
        # Render line chart figure into tkinter
        self.tk_canvas = tkAgg.FigureCanvasTkAgg(self.figure, master=self.tk_frame)
        self.tk_canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        return self

    def update(self, x_data, y_data):
        self.initial_x_data = list(x_data)
        self.initial_y_data = list(y_data)
        self.__plot_data(self.initial_x_data, self.initial_y_data)
        self.tk_canvas.draw_idle()

    def __prepare_plot(self):
        # Matplotlib line chart figure and axis
        self.figure, self.axis = plt.subplots(
            figsize=self.figsize,
            dpi=CHART_DPI,
            constrained_layout=self.constrained_layout
        )

    def __plot_data(self, x_data, y_data):
        self.axis.clear()
        style_chart(self.figure, self.axis)

        if len(x_data) == 0 or len(y_data) == 0:
            self.axis.text(
                0.5,
                0.5,
                NO_GRAPH_DATA_TEXT,
                color=SOLAR_TEXT,
                ha="center",
                va="center",
                transform=self.axis.transAxes,
            )
            self.axis.set_xticks([])
            self.axis.set_yticks([])
            self.axis.axis("off")
            return

        self.axis.set_axis_on()
        self.axis.plot(
            x_data,
            y_data,
            color=SOLAR_YELLOW,
            linewidth=self.line_width,
            marker="o",
        )

        if self.fill_area:
            self.axis.fill_between(
                x_data,
                y_data,
                color=SOLAR_YELLOW,
                alpha=CHART_FILL_ALPHA,
            )

        if self.x_tick_labels is not None:
            self.axis.set_xticks(x_data, self.x_tick_labels)

        if self.chart_title:
            self.axis.set_title(self.chart_title, fontsize=CHART_TITLE_FONT_SIZE)
        self.axis.set_ylabel(self.y_label)
