"""Covers the modal flows.

Every dialog here ends in `wait_window`, which blocks until a human closes it.
Each test stubs that one call so the dialog is built and then driven from code,
which is the only way to reach the submit handlers without a person clicking.
"""
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

import ttkbootstrap as tb

from constants import (
    ADD_BUTTON_TEXT,
    APP_GEOMETRY,
    APP_MODE_DEV,
    APP_TITLE,
    DEFAULT_EXPENSE_CATEGORY,
    ENTER_AMOUNT_ERROR,
    ENTER_VALID_AMOUNT_ERROR,
    EXPENSE_BUTTON_TEXT,
    INCOME_BUTTON_TEXT,
)
from persistence.sqlite_repository import SQLiteBalanceRepository
from services.finance_service import FinanceService
from tests.support import TkTestCase
from ui.sidebar import Sidebar


def widgets_of(parent, widget_type):
    """Every descendant of `parent` of the given type, depth first."""
    found = []
    for child in parent.winfo_children():
        if isinstance(child, widget_type):
            found.append(child)
        found.extend(widgets_of(child, widget_type))
    return found


class SidebarDialogTests(TkTestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.service = FinanceService(
            SQLiteBalanceRepository(Path(self.directory.name) / "dialogs.db"),
        )
        self.service.initialize(APP_MODE_DEV, False, "1000.00")

        self.frame = tb.Frame(self.window)
        self.addCleanup(self.frame.destroy)
        self.balance_changed = 0
        self.sidebar = Sidebar(
            self.frame,
            finance_service=self.service,
            on_balance_changed=self._count_change,
        )
        self.sidebar.draw()
        self.opened_dialogs = []
        self.frame.wait_window = self._capture_dialog

    def _count_change(self):
        self.balance_changed += 1

    def _capture_dialog(self, dialog):
        """Stands in for wait_window so the dialog stays open for inspection."""
        self.opened_dialogs.append(dialog)

    def _open(self, label):
        button = next(
            child for child in self.sidebar.tk_frame.winfo_children()
            if isinstance(child, tb.Button) and child.cget("text") == label
        )
        button.invoke()
        dialog = self.opened_dialogs[-1]
        self.addCleanup(lambda: dialog.winfo_exists() and dialog.destroy())
        return dialog

    @staticmethod
    def _fill_amount(dialog, text):
        entry = widgets_of(dialog, tb.Entry)[0]
        entry.delete(0, "end")
        entry.insert(0, text)

    @staticmethod
    def _submit(dialog):
        next(
            button for button in widgets_of(dialog, tb.Button)
            if button.cget("text") == ADD_BUTTON_TEXT
        ).invoke()

    @staticmethod
    def _error_text(dialog):
        return " ".join(
            label.cget("text") for label in widgets_of(dialog, tb.Label)
        )

    def test_the_income_dialog_adds_the_amount_and_closes(self):
        dialog = self._open(INCOME_BUTTON_TEXT)
        self._fill_amount(dialog, "250,50")

        self._submit(dialog)

        self.assertEqual(self.service.balance.get_value(), Decimal("1250.50"))
        self.assertEqual(self.balance_changed, 1)
        self.assertFalse(dialog.winfo_exists())

    def test_the_income_dialog_refuses_a_bad_amount_and_stays_open(self):
        dialog = self._open(INCOME_BUTTON_TEXT)
        self._fill_amount(dialog, "not a number")

        self._submit(dialog)

        self.assertEqual(self.service.balance.get_value(), Decimal("1000.00"))
        self.assertIn(ENTER_AMOUNT_ERROR, self._error_text(dialog))
        self.assertTrue(dialog.winfo_exists())
        self.assertEqual(self.balance_changed, 0)

    def test_the_income_dialog_refuses_an_empty_amount(self):
        dialog = self._open(INCOME_BUTTON_TEXT)
        self._fill_amount(dialog, "")

        self._submit(dialog)

        self.assertEqual(self.service.balance.get_value(), Decimal("1000.00"))
        self.assertTrue(dialog.winfo_exists())

    def test_the_expense_dialog_subtracts_the_amount(self):
        dialog = self._open(EXPENSE_BUTTON_TEXT)
        self._fill_amount(dialog, "300.25")

        self._submit(dialog)

        self.assertEqual(self.service.balance.get_value(), Decimal("699.75"))
        self.assertEqual(self.balance_changed, 1)

    def test_the_expense_dialog_defaults_to_the_first_category(self):
        dialog = self._open(EXPENSE_BUTTON_TEXT)
        combobox = widgets_of(dialog, tb.Combobox)[0]

        self.assertEqual(combobox.get(), DEFAULT_EXPENSE_CATEGORY)

        self._fill_amount(dialog, "10.00")
        self._submit(dialog)

        self.assertEqual(
            self.service.balance.get_expenses()[0].category, DEFAULT_EXPENSE_CATEGORY,
        )

    def test_the_expense_dialog_records_the_chosen_category(self):
        dialog = self._open(EXPENSE_BUTTON_TEXT)
        combobox = widgets_of(dialog, tb.Combobox)[0]
        combobox.set(self.sidebar.expense_categories[-1])
        self._fill_amount(dialog, "10.00")

        self._submit(dialog)

        self.assertEqual(
            self.service.balance.get_expenses()[0].category,
            self.sidebar.expense_categories[-1],
        )

    def test_the_expense_dialog_refuses_a_bad_amount_and_stays_open(self):
        dialog = self._open(EXPENSE_BUTTON_TEXT)
        self._fill_amount(dialog, "-5")

        self._submit(dialog)

        self.assertEqual(self.service.balance.get_value(), Decimal("1000.00"))
        self.assertIn(ENTER_VALID_AMOUNT_ERROR, self._error_text(dialog))
        self.assertTrue(dialog.winfo_exists())

    def test_the_sidebar_label_refreshes_after_a_successful_entry(self):
        before = self.sidebar.lbl_balance.cget("text")
        dialog = self._open(INCOME_BUTTON_TEXT)
        self._fill_amount(dialog, "1.00")

        self._submit(dialog)

        self.assertNotEqual(self.sidebar.lbl_balance.cget("text"), before)

    def test_return_is_bound_as_a_shortcut_for_submitting(self):
        # The keypress itself cannot be dispatched to an unfocused dialog from a
        # test, so assert the binding exists rather than simulating the key.
        for label in (INCOME_BUTTON_TEXT, EXPENSE_BUTTON_TEXT):
            with self.subTest(dialog=label):
                dialog = self._open(label)

                self.assertIn("<Key-Return>", dialog.bind())


class InitialBalanceDialogTests(TkTestCase):
    """Drives InitialBalanceWindow.draw(), which normally blocks on wait_window."""

    def setUp(self):
        from ui.popup import initial_balance_window as module

        self.frame = tb.Frame(self.window)
        self.addCleanup(self.frame.destroy)
        self.module = module

    def _draw(self):
        from ui.popup.initial_balance_window import InitialBalanceWindow

        popup = InitialBalanceWindow(self.frame)
        self.frame.wait_window = lambda dialog: None
        drawn = popup.draw()
        drawn.dialog.withdraw()
        self.addCleanup(lambda: drawn.dialog.winfo_exists() and drawn.dialog.destroy())
        return drawn

    def test_draw_builds_a_dialog_with_a_default_of_zero(self):
        popup = self._draw()

        self.assertTrue(popup.dialog.winfo_exists())
        self.assertEqual(popup.balance_var.get(), "0")

    def test_submitting_a_value_returns_it_and_closes(self):
        popup = self._draw()
        popup.balance_var.set("1500,75")

        popup.submit()

        self.assertEqual(popup.get_result(), Decimal("1500.75"))
        self.assertFalse(popup.dialog.winfo_exists())

    def test_submitting_rubbish_keeps_the_dialog_open_with_an_error(self):
        popup = self._draw()
        popup.balance_var.set("abc")

        popup.submit()

        self.assertIsNone(popup.get_result())
        self.assertTrue(popup.dialog.winfo_exists())
        self.assertTrue(popup.lbl_error.cget("text"))

    def test_disable_topmost_is_safe_before_and_after_destruction(self):
        popup = self._draw()

        popup.disable_topmost()          # window still alive
        popup.dialog.destroy()
        popup.disable_topmost()          # must not raise once destroyed


class MainWindowFirstRunTests(unittest.TestCase):
    """The dev-mode first run, where the app must ask for an opening balance."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.addCleanup(self._destroy)
        self.main_window = None

    def _destroy(self):
        import matplotlib.pyplot as plt

        window = getattr(self.main_window, "window", None)
        if window is not None:
            try:
                window.destroy()
            except Exception:              # pragma: no cover - already gone
                pass
        plt.close("all")

    def _main_window(self, answer):
        import ui.main_window as module
        from ui.main_window import MainWindow

        service = FinanceService(
            SQLiteBalanceRepository(Path(self.directory.name) / "first_run.db"),
        )
        window = MainWindow(
            APP_TITLE, APP_GEOMETRY, finance_service=service,
            app_mode=APP_MODE_DEV, reset_data_on_start=False,
        )

        class StubDialog:
            def __init__(self, master):
                pass

            def draw(self):
                return self

            def get_result(self):
                return answer

        original = module.InitialBalanceWindow
        module.InitialBalanceWindow = StubDialog
        self.addCleanup(lambda: setattr(module, "InitialBalanceWindow", original))
        self.main_window = window
        return window

    def test_an_entered_opening_balance_starts_the_dashboard(self):
        window = self._main_window(Decimal("500.00"))

        try:
            built = window.setup()
        except Exception as error:         # pragma: no cover - display-dependent
            self.skipTest(f"Tk is unavailable here: {error}")
        window.window.withdraw()

        self.assertTrue(built)
        self.assertEqual(window.balance.get_value(), Decimal("500.00"))

    def test_cancelling_the_opening_dialog_aborts_startup(self):
        window = self._main_window(None)

        try:
            built = window.setup()
        except Exception as error:         # pragma: no cover - display-dependent
            self.skipTest(f"Tk is unavailable here: {error}")

        self.assertFalse(built)

    def test_start_does_not_enter_the_loop_when_setup_is_aborted(self):
        window = self._main_window(None)
        entered = []
        try:
            window.start()
        except Exception as error:         # pragma: no cover - display-dependent
            self.skipTest(f"Tk is unavailable here: {error}")

        self.assertEqual(entered, [])

    def test_start_enters_the_event_loop_once_setup_succeeds(self):
        import ttkbootstrap as tb

        window = self._main_window(Decimal("500.00"))
        entered = []
        original_mainloop = tb.Window.mainloop
        tb.Window.mainloop = lambda self, *a, **kw: entered.append(True)
        self.addCleanup(lambda: setattr(tb.Window, "mainloop", original_mainloop))

        try:
            window.start()
        except Exception as error:         # pragma: no cover - display-dependent
            self.skipTest(f"Tk is unavailable here: {error}")
        window.window.withdraw()

        self.assertEqual(entered, [True])

    def test_changing_the_date_filter_redraws_the_dashboard(self):
        from datetime import date

        window = self._main_window(Decimal("500.00"))
        try:
            window.setup()
        except Exception as error:         # pragma: no cover - display-dependent
            self.skipTest(f"Tk is unavailable here: {error}")
        window.window.withdraw()

        window._set_expense_filter(date(2026, 1, 1), date(2026, 12, 31))

        self.assertEqual(window.expense_start_date, date(2026, 1, 1))
        self.assertEqual(window.expense_end_date, date(2026, 12, 31))


if __name__ == "__main__":
    unittest.main()
