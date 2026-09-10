import tkinter as tk

import ttkbootstrap as tb

from constants import (
    CLOSE_WINDOW_EVENT,
    DANGER_STYLE,
    DEFAULT_BALANCE,
    DIALOG_BUTTON_INTERNAL_PADDING,
    DIALOG_ENTRY_WIDTH,
    DIALOG_PADDING,
    DIALOG_TITLE_FONT_SIZE,
    DIALOG_TITLE_PADDING,
    ENTER_KEY_EVENT,
    FIELD_LABEL_PADDING,
    FONT_FAMILY,
    FONT_WEIGHT_BOLD,
    INITIAL_BALANCE_DIALOG_TITLE,
    INITIAL_BALANCE_PROMPT,
    INVALID_NUMBER_ERROR,
    INPUT_DECIMAL_SEPARATOR,
    NORMALIZED_DECIMAL_SEPARATOR,
    START_BUTTON_TEXT,
    SUCCESS_STYLE,
    TOPMOST_DELAY_MS,
)

class InitialBalanceWindow():
    def __init__(self, master):
        self.master = master
        self.balance_var = tb.StringVar(value=str(DEFAULT_BALANCE))
        self.result = {"balance": float(DEFAULT_BALANCE)}
        self.lbl_error = None
        self.dialog = None

    def draw(self):
        self.dialog = tb.Toplevel(self.master)
        self.dialog.withdraw()
        self.dialog.title(INITIAL_BALANCE_DIALOG_TITLE)
        self.dialog.resizable(False, False)

        container = tb.Frame(self.dialog, padding=DIALOG_PADDING)
        container.grid(column=0, row=0, sticky="nsew")
        container.columnconfigure(0, weight=1)

        lbl_title = tb.Label(
            container,
            text=INITIAL_BALANCE_PROMPT,
            font=(FONT_FAMILY, DIALOG_TITLE_FONT_SIZE, FONT_WEIGHT_BOLD),
        )
        lbl_title.grid(column=0, row=0, pady=DIALOG_TITLE_PADDING, sticky="nsew")

        entry_balance = tb.Entry(
            container,
            textvariable=self.balance_var,
            width=DIALOG_ENTRY_WIDTH,
        )
        entry_balance.grid(column=1, row=0, pady=FIELD_LABEL_PADDING, sticky="ew")

        self.lbl_error = tb.Label(
            container,
            bootstyle=DANGER_STYLE,
        )
        self.lbl_error.grid(column=0, row=1, pady=DIALOG_TITLE_PADDING, sticky="w")

        btn_start = tb.Button(
            container,
            text=START_BUTTON_TEXT,
            bootstyle=SUCCESS_STYLE,
            command=self.submit
        )
        btn_start.grid(
            row=3,
            column=0,
            ipady=DIALOG_BUTTON_INTERNAL_PADDING,
            sticky="ew",
        )

        self.dialog.bind(ENTER_KEY_EVENT, lambda _event: self.submit())
        self.dialog.protocol(CLOSE_WINDOW_EVENT, self.dialog.destroy)

        entry_balance.focus_set()
        entry_balance.selection_range(0, tk.END)

        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_width()) // 2
        y = (self.dialog.winfo_screenheight() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{int(x)}+{int(y)}")
        self.dialog.deiconify()
        self.dialog.lift()

        try:
            self.dialog.attributes("-topmost", True)
            self.dialog.after(TOPMOST_DELAY_MS, self.disable_topmost)
        except tk.TclError:
            pass

        self.dialog.grab_set()
        entry_balance.focus_force()
        self.master.wait_window(self.dialog)
        return self

    def get_result(self):
        return self.result["balance"]

    def submit(self):
        entered_balance = self.balance_var.get().strip().replace(
            INPUT_DECIMAL_SEPARATOR,
            NORMALIZED_DECIMAL_SEPARATOR,
        )
        try:
            self.result["balance"] = float(entered_balance)
        except ValueError:
            self.lbl_error.configure(text=INVALID_NUMBER_ERROR)
            return
        self.dialog.destroy()

    def disable_topmost(self):
        if self.dialog.winfo_exists():
            self.dialog.attributes("-topmost", False)
