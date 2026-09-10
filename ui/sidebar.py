import tkinter as tk

import ttkbootstrap as tb

from constants import (
    ADD_BUTTON_TEXT,
    BALANCE_TEXT_TEMPLATE,
    BODY_FONT_SIZE,
    CATEGORY_ENTRY_WIDTH,
    CATEGORY_LABEL,
    CURRENCY_LABEL,
    DANGER_STYLE,
    DEFAULT_EXPENSE_CATEGORY,
    DIALOG_BUTTON_INTERNAL_PADDING,
    DIALOG_ENTRY_WIDTH,
    DIALOG_PADDING,
    ENTER_KEY_EVENT,
    ENTER_AMOUNT_ERROR,
    ENTER_VALID_AMOUNT_ERROR,
    EXPENSE_AMOUNT_LABEL,
    EXPENSE_BUTTON_STYLE,
    EXPENSE_BUTTON_TEXT,
    EXPENSE_CATEGORIES,
    EXPENSE_DIALOG_TITLE,
    EXPORT_BUTTON_STYLE,
    EXPORT_BUTTON_TEXT,
    FIELD_LABEL_PADDING,
    FONT_FAMILY,
    FONT_WEIGHT_BOLD,
    INPUT_DECIMAL_SEPARATOR,
    INCOME_AMOUNT_LABEL,
    INCOME_BUTTON_STYLE,
    INCOME_BUTTON_TEXT,
    INCOME_DIALOG_TITLE,
    INTEGER_AMOUNT_FORMAT_SPEC,
    NORMALIZED_DECIMAL_SEPARATOR,
    SAFETY_CUSHION,
    SAFETY_CUSHION_TEXT_TEMPLATE,
    SIDEBAR_BUTTON_INTERNAL_PADDING,
    SIDEBAR_BUTTON_PADDING,
    SIDEBAR_FIRST_BUTTON_PADDING,
    SIDEBAR_INFO_PADDING,
    SIDEBAR_PADDING,
    THOUSANDS_SEPARATOR,
)
from domain.money import positive_money
from services.finance_service import FinanceService


class Sidebar:
    def __init__(
            self,
            master,
            row=0,
            column=0,
            rowspan=5,
            finance_service: FinanceService = None,
            expense_categories=None,
            on_balance_changed=None, ):
        self.master = master
        self.row = row
        self.column = column
        self.rowspan = rowspan
        self.tk_frame = None
        if finance_service is None:
            raise ValueError("finance_service is required")
        self.finance_service = finance_service
        self.expense_categories = expense_categories or EXPENSE_CATEGORIES
        self.on_balance_changed = on_balance_changed
        self.lbl_balance = None

    def _format_balance(self):
        return BALANCE_TEXT_TEMPLATE.format(
            balance=self.finance_service.balance.get_value(),
            currency=CURRENCY_LABEL,
        )

    def _parse_amount(self, value):
        try:
            return positive_money(
                value.strip().replace(
                    INPUT_DECIMAL_SEPARATOR,
                    NORMALIZED_DECIMAL_SEPARATOR,
                )
            )
        except (TypeError, ValueError):
            return None

    def _center_dialog(self, dialog):
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) / 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) / 2
        dialog.geometry(f"+{int(x)}+{int(y)}")

    def _refresh_balance(self):
        self.lbl_balance.configure(text=self._format_balance())

    def _show_income_dialog(self):
        amount_var = tk.StringVar()
        dialog = tb.Toplevel(self.master)
        dialog.title(INCOME_DIALOG_TITLE)
        dialog.resizable(False, False)
        dialog.transient(self.master)
        dialog.grab_set()

        container = tb.Frame(dialog, padding=DIALOG_PADDING)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)

        tb.Label(
            container,
            text=INCOME_AMOUNT_LABEL,
            font=(FONT_FAMILY, BODY_FONT_SIZE, FONT_WEIGHT_BOLD),
        ).grid(
            row=0, column=0, sticky="w", pady=FIELD_LABEL_PADDING,
        )
        entry_amount = tb.Entry(
            container,
            textvariable=amount_var,
            width=DIALOG_ENTRY_WIDTH,
        )
        entry_amount.grid(row=1, column=0, sticky="w")

        lbl_error = tb.Label(container, bootstyle=DANGER_STYLE)
        lbl_error.grid(row=2, column=0, sticky="w")

        def submit():
            amount = self._parse_amount(amount_var.get())

            if amount is None:
                lbl_error.configure(text=ENTER_AMOUNT_ERROR)
                return
            self.finance_service.add_income(amount)
            self._refresh_balance()
            if self.on_balance_changed:
                self.on_balance_changed()
            dialog.destroy()

        tb.Button(
            container,
            text=ADD_BUTTON_TEXT,
            bootstyle=INCOME_BUTTON_STYLE,
            command=submit,
        ).grid(
            row=3, column=0, ipady=DIALOG_BUTTON_INTERNAL_PADDING, sticky="ew",
        )
        dialog.bind(ENTER_KEY_EVENT, lambda e: submit())
        self._center_dialog(dialog)
        entry_amount.focus_set()
        self.master.wait_window(dialog)

    def _show_expense_dialog(self):
        amount_var = tk.StringVar()
        category_var = tk.StringVar(value=DEFAULT_EXPENSE_CATEGORY)
        dialog = tb.Toplevel(self.master)
        dialog.title(EXPENSE_DIALOG_TITLE)
        dialog.resizable(False, False)
        dialog.transient(self.master)
        dialog.grab_set()

        container = tb.Frame(dialog, padding=DIALOG_PADDING)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)

        tb.Label(
            container,
            text=CATEGORY_LABEL,
            font=(FONT_FAMILY, BODY_FONT_SIZE, FONT_WEIGHT_BOLD),
        ).grid(
            row=0, column=0, sticky="ew", pady=FIELD_LABEL_PADDING,
        )

        category_box = tb.Combobox(
            container,
            textvariable=category_var,
            values=self.expense_categories,
            state="readonly",
            width=CATEGORY_ENTRY_WIDTH,
        )
        category_box.grid(row=1, column=0, sticky="ew", pady=SIDEBAR_FIRST_BUTTON_PADDING)

        tb.Label(
            container,
            text=EXPENSE_AMOUNT_LABEL,
            font=(FONT_FAMILY, BODY_FONT_SIZE, FONT_WEIGHT_BOLD),
        ).grid(
            row=2, column=0, sticky="w", pady=FIELD_LABEL_PADDING,
        )

        entry_amount = tb.Entry(
            container,
            textvariable=amount_var,
            width=DIALOG_ENTRY_WIDTH,
        )
        entry_amount.grid(row=3, column=0, sticky="w")

        lbl_error = tb.Label(container, bootstyle=DANGER_STYLE)
        lbl_error.grid(row=4, column=0, sticky="w")

        def submit():
            amount = self._parse_amount(amount_var.get())

            if amount is None:
                lbl_error.configure(text=ENTER_VALID_AMOUNT_ERROR)
                return
            self.finance_service.add_expense(amount, category_var.get())
            self._refresh_balance()
            if self.on_balance_changed:
                self.on_balance_changed()
            dialog.destroy()

        tb.Button(
            container,
            text=ADD_BUTTON_TEXT,
            bootstyle=DANGER_STYLE,
            command=submit,
        ).grid(
            row=5, column=0, ipady=DIALOG_BUTTON_INTERNAL_PADDING, sticky="ew",
        )
        dialog.bind(ENTER_KEY_EVENT, lambda e: submit())
        self._center_dialog(dialog)
        entry_amount.focus_set()
        self.master.wait_window(dialog)

    def draw(self):
        # Buttons and cushion text
        self.tk_frame = tb.Frame(self.master, padding=SIDEBAR_PADDING)
        self.tk_frame.grid(row=0, column=0, rowspan=5, sticky="nsew")
        self.tk_frame.columnconfigure(0, weight=1)

        btn_expense = tb.Button(self.tk_frame, text=EXPENSE_BUTTON_TEXT,
                                bootstyle=EXPENSE_BUTTON_STYLE,
                                command=self._show_expense_dialog)
        btn_expense.grid(
            row=0, column=0, pady=SIDEBAR_FIRST_BUTTON_PADDING,
            ipady=SIDEBAR_BUTTON_INTERNAL_PADDING, sticky="ew",
        )

        btn_income = tb.Button(self.tk_frame,
                               text=INCOME_BUTTON_TEXT,
                               bootstyle=INCOME_BUTTON_STYLE,
                               command=self._show_income_dialog)
        btn_income.grid(
            row=1, column=0, pady=SIDEBAR_BUTTON_PADDING,
            ipady=SIDEBAR_BUTTON_INTERNAL_PADDING, sticky="ew",
        )

        btn_export = tb.Button(
            self.tk_frame,
            text=EXPORT_BUTTON_TEXT,
            bootstyle=EXPORT_BUTTON_STYLE,
        )
        btn_export.grid(
            row=2, column=0, pady=SIDEBAR_BUTTON_PADDING,
            ipady=SIDEBAR_BUTTON_INTERNAL_PADDING, sticky="ew",
        )

        self.lbl_balance = tb.Label(
            self.tk_frame,
            text=self._format_balance(),
            font=(FONT_FAMILY, BODY_FONT_SIZE, FONT_WEIGHT_BOLD),
            justify="center",
        )
        self.lbl_balance.grid(row=3, column=0, pady=SIDEBAR_INFO_PADDING, sticky="ew")

        lbl_cushion = tb.Label(
            self.tk_frame,
            text=SAFETY_CUSHION_TEXT_TEMPLATE.format(
                amount=format(SAFETY_CUSHION, INTEGER_AMOUNT_FORMAT_SPEC).replace(
                    ",",
                    THOUSANDS_SEPARATOR,
                ),
                currency=CURRENCY_LABEL,
            ),
            font=(FONT_FAMILY, BODY_FONT_SIZE, FONT_WEIGHT_BOLD),
            justify="center",
        )
        lbl_cushion.grid(row=4, column=0, pady=SIDEBAR_INFO_PADDING, sticky="ew")
        return self
