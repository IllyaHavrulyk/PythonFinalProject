import matplotlib.backends.backend_tkagg as tkAgg
import matplotlib.pyplot as plt
import ttkbootstrap as tb
from ttkbootstrap.constants import *

from constants import *


class PieChart:
    def __init__(self, row, column, sizes, master, categories, colors, title):
        # Pie chart frame
        self.sizes = sizes
        self.row = row
        self.column = column
        self.master = master
        self.categories = categories
        self.colors = colors
        self.title = title
        self.tk_canvas = None
        self.tk_frame = None
        self.figure = None
        self.axis = None
        self.pie_slices = None
        # Matplotlib pie chart figure and axis

    def __prepare_plot(self):
        self.figure, self.axis = plt.subplots(figsize=(3, 2), dpi=100)
        self.__plot_data()

    def draw(self):
        self.tk_frame = tb.LabelFrame(self.master, text=self.title, padding=5)
        self.tk_frame.grid(row=self.row, column=self.column, padx=(8, 15), pady=10, sticky="nsew")

        self.__prepare_plot()
        self.tk_canvas = tkAgg.FigureCanvasTkAgg(self.figure, master=self.tk_frame)
        self.tk_canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        return self

    def __plot_data(self):
        self.axis.clear()
        self.figure.patch.set_facecolor(SOLAR_PANEL)
        self.axis.set_facecolor(SOLAR_PANEL)

        if not self.sizes or sum(self.sizes) == 0:
            self.axis.text(
                0.5,
                0.5,
                "Немає витрат",
                color=SOLAR_TEXT,
                ha="center",
                va="center",
                transform=self.axis.transAxes,
            )
            self.axis.set_xticks([])
            self.axis.set_yticks([])
            self.axis.axis("off")
            return

        self.axis.axis("on")
        self.pie_slices, category_labels, percentage_labels = self.axis.pie(
            self.sizes,
            labels=self.categories,
            colors=self.colors,
            autopct="%1.0f%%",
            startangle=90,
            wedgeprops={"edgecolor": SOLAR_PANEL},
        )
        for pie_text in category_labels + percentage_labels:
            pie_text.set_color(SOLAR_TEXT)
        self.axis.axis("equal")

    def update_data(self, sizes, categories, colors):
        self.sizes = sizes
        self.categories = categories
        self.colors = colors
        self.__plot_data()
        self.tk_canvas.draw_idle()