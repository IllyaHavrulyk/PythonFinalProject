import ttkbootstrap as tb
from ttkbootstrap.constants import LEFT


class DateRangeSelector:
    def __init__(self, master, row, column, padx):
        self.master = master
        self.row = row
        self.column = column
        self.padx = padx
        self.tk_frame = None

    def draw(self):
        self.tk_frame = tb.Frame(self.master)
        self.tk_frame.grid(row=self.row, column=self.column, padx=self.padx, pady=5, sticky="ew")
        tb.Label(self.tk_frame, text="від").pack(side=LEFT)
        tb.DateEntry(self.tk_frame, width=10).pack(side=LEFT, expand=True, padx=5)
        tb.Label(self.tk_frame, text="до").pack(side=LEFT)
        tb.DateEntry(self.tk_frame, width=10).pack(side=LEFT, expand=True, padx=5)
        return self
