import matplotlib.backends.backend_tkagg as tkAgg
import matplotlib.pyplot as plt
import ttkbootstrap as tb
from ttkbootstrap.constants import BOTH

from constants import *
from utils import style_chart


class GraphChart:
    def __init__(
        self,
        row,
        column,
        x_data,
        y_data,
        master,
        title,
        y_label,
        figsize,
        padx,
        columnspan=1,
        constrained_layout=False,
        fill_area=False,
        x_tick_labels=None,
        chart_title=None,
        line_width=2.5,
    ):
        self.row = row
        self.column = column
        self.x_data = x_data
        self.y_data = y_data
        self.master = master
        self.title = title
        self.y_label = y_label
        self.figsize = figsize
        self.padx = padx
        self.columnspan = columnspan
        self.constrained_layout = constrained_layout
        self.fill_area = fill_area
        self.x_tick_labels = x_tick_labels
        self.chart_title = chart_title
        self.line_width = line_width
        self.tk_canvas = None
        self.tk_frame = None
        self.figure = None
        self.axis = None

    def __prepare_plot(self):
        self.figure, self.axis = plt.subplots(
            figsize=self.figsize,
            dpi=100,
            constrained_layout=self.constrained_layout,
        )
        self.axis.plot(self.x_data, self.y_data, color=SOLAR_YELLOW, linewidth=self.line_width)

        if self.fill_area:
            self.axis.fill_between(self.x_data, self.y_data, color=SOLAR_YELLOW, alpha=0.3)

        if self.x_tick_labels is not None:
            self.axis.set_xticks(self.x_data, self.x_tick_labels)

        if self.chart_title:
            self.axis.set_title(self.chart_title, fontsize=10)
        self.axis.set_ylabel(self.y_label)
        style_chart(self.figure, self.axis)

    def draw(self):
        self.tk_frame = tb.LabelFrame(self.master, text=self.title, padding=5)
        self.tk_frame.grid(
            row=self.row,
            column=self.column,
            columnspan=self.columnspan,
            padx=self.padx,
            pady=10,
            sticky="nsew",
        )

        self.__prepare_plot()
        self.tk_canvas = tkAgg.FigureCanvasTkAgg(self.figure, master=self.tk_frame)
        self.tk_canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        return self
