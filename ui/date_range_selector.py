import ttkbootstrap as tb
from ttkbootstrap.constants import LEFT, X

from constants import (
    APPLY_BUTTON_STYLE,
    APPLY_BUTTON_TEXT,
    CONTROL_GAP,
    DATE_ENTRY_WIDTH,
    DATE_FORMAT,
    DATE_FROM_TEXT,
    DATE_SELECTED_EVENT,
    DATE_TO_TEXT,
    ENTER_KEY_EVENT,
    FOCUS_OUT_EVENT,
)

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
        self.tk_frame.grid(
            row=self.row,
            column=self.column,
            padx=self.padx,
            pady=CONTROL_GAP,
            sticky="nsew",
        )

        controls_frame = tb.Frame(self.tk_frame)
        controls_frame.pack(fill=X)

        tb.Label(controls_frame, text=DATE_FROM_TEXT).pack(side=LEFT)
        self.from_date_entry = tb.DateEntry(
            controls_frame,
            width=DATE_ENTRY_WIDTH,
            date_format=DATE_FORMAT,
        )
        self.from_date_entry.pack(side=LEFT, expand=True, padx=CONTROL_GAP)

        tb.Label(controls_frame, text=DATE_TO_TEXT).pack(side=LEFT)
        self.to_date_entry = tb.DateEntry(
            controls_frame,
            width=DATE_ENTRY_WIDTH,
            date_format=DATE_FORMAT,
        )
        self.to_date_entry.pack(side=LEFT, expand=True, padx=CONTROL_GAP)

        if self.show_apply:
            tb.Button(
                controls_frame,
                text=APPLY_BUTTON_TEXT,
                bootstyle=APPLY_BUTTON_STYLE,
                command=self.__notify_change
            ).pack(side=LEFT, padx=(CONTROL_GAP, 0))

        for date_entry in (self.from_date_entry, self.to_date_entry):
            date_entry.bind(DATE_SELECTED_EVENT, self.__notify_change)
            date_entry.bind(ENTER_KEY_EVENT, self.__notify_change)
            date_entry.bind(FOCUS_OUT_EVENT, self.__notify_change)
        return self
