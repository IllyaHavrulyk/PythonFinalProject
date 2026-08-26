import matplotlib.backends.backend_tkagg as tkAgg
import matplotlib.pyplot as plt
import ttkbootstrap as tb
from ttkbootstrap.constants import BOTH

from constants import *


class PieChart:
    def __init__(self, row, column, sizes, master, categories, colors, title):
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

    def __prepare_plot(self):
        self.figure, self.axis = plt.subplots(figsize=(3, 2), dpi=100)
        self.pie_slices, category_labels, percentage_labels = self.axis.pie(
            self.sizes,
            labels=self.categories,
            colors=self.colors,
            autopct="%1.0f%%",
            startangle=90,
            wedgeprops={"edgecolor": SOLAR_PANEL},
        )
        self.figure.patch.set_facecolor(SOLAR_PANEL)
        self.axis.set_facecolor(SOLAR_PANEL)
        for pie_text in category_labels + percentage_labels:
            pie_text.set_color(SOLAR_TEXT)
        self.axis.axis("equal")

    def draw(self):
        self.tk_frame = tb.LabelFrame(self.master, text=self.title, padding=5)
        self.tk_frame.grid(row=self.row, column=self.column, padx=(8, 15), pady=10, sticky="nsew")

        self.__prepare_plot()
        self.tk_canvas = tkAgg.FigureCanvasTkAgg(self.figure, master=self.tk_frame)
        self.tk_canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        return self
