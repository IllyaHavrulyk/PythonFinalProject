import ttkbootstrap as tb
from ttkbootstrap.constants import LEFT, X


class DateRangeSelector:
    def __init__(self, master, row, column, padx, on_change=None, show_apply=False):
        self.master = master
        self.row = row
        self.column = column
        self.padx = padx
        self.on_change = on_change
        self.show_apply = show_apply
        self.tk_frame = None
        self.from_date_entry = None
        self.to_date_entry = None

    def get_date_range(self):
        from_date = self.from_date_entry.get_date()
        to_date = self.to_date_entry.get_date()

        if hasattr(from_date, "date"):
            from_date = from_date.date()
        if hasattr(to_date, "date"):
            to_date = to_date.date()

        if from_date and to_date and from_date > to_date:
            from_date, to_date = to_date, from_date

        return from_date, to_date

    def __notify_change(self, _event=None):
        if self.on_change:
            self.on_change(*self.get_date_range())

    def draw(self):
        self.tk_frame = tb.Frame(self.master)
        self.tk_frame.grid(row=self.row, column=self.column, padx=self.padx, pady=5, sticky="nsew")

        controls_frame = tb.Frame(self.tk_frame)
        controls_frame.pack(fill=X)

        tb.Label(controls_frame, text="від").pack(side=LEFT)
        self.from_date_entry = tb.DateEntry(controls_frame, width=10, date_format="%Y-%m-%d")
        self.from_date_entry.pack(side=LEFT, expand=True, padx=5)

        tb.Label(controls_frame, text="до").pack(side=LEFT)
        self.to_date_entry = tb.DateEntry(controls_frame, width=10, date_format="%Y-%m-%d")
        self.to_date_entry.pack(side=LEFT, expand=True, padx=5)

        if self.show_apply:
            tb.Button(
                controls_frame,
                text="Застосувати",
                bootstyle="info-outline",
                command=self.__notify_change
            ).pack(side=LEFT, padx=(5,0))

        for date_entry in (self.from_date_entry, self.to_date_entry):
            date_entry.bind("<<DateEntrySelected>>", self.__notify_change)
            date_entry.bind("<Return>", self.__notify_change)
            date_entry.bind("<FocusOut>", self.__notify_change)
        return self
