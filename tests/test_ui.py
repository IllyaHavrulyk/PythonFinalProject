import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import ttkbootstrap as tb

from constants import (
    APP_GEOMETRY,
    APP_MODE_DEV,
    APP_MODE_TEST,
    APP_TITLE,
    ALERT_POSITIONS,
    BALANCE_AXIS_LABEL,
    CHART_TICK_FONT_SIZE,
    EXPENSE_BUTTON_TEXT,
    EXPENSE_CHART_TITLE,
    EXPORT_BUTTON_TEXT,
    GREEN_ALERT_STYLE,
    INCOME_BUTTON_TEXT,
    NO_EXPENSES_TEXT,
    NO_GRAPH_DATA_TEXT,
    RED_ALERT_STYLE,
    SOLAR_PANEL,
    SOLAR_TEXT,
    TOP_CHART_FIGURE_SIZE,
    TOP_CHART_TITLE,
)
from domain.balance import Balance
from domain.expense import Expense
from domain.income import Income
from persistence.sqlite_repository import SQLiteBalanceRepository
from services.finance_service import FinanceService
from tests.support import TkTestCase
from ui.alert import Alert
from ui.charts.graph_chart import GraphChart
from ui.charts.pie.expense_table import ExpenseTable
from ui.charts.pie.pie_chart import PieChart
from ui.dashboard_alerts import DashboardAlerts
from ui.date_range_selector import DateRangeSelector
from ui.popup.initial_balance_window import InitialBalanceWindow
from ui.sidebar import Sidebar
from utils import style_chart

TODAY = date.today()


def service_with_demo_data(directory):
    service = FinanceService(SQLiteBalanceRepository(Path(directory) / "ui.db"))
    service.initialize(APP_MODE_TEST, True)
    return service


class StyleChartTests(unittest.TestCase):
    def setUp(self):
        self.figure, self.axis = plt.subplots()
        self.addCleanup(plt.close, self.figure)

    def test_applies_the_dark_panel_palette(self):
        style_chart(self.figure, self.axis)

        self.assertEqual(self.axis.get_facecolor(), matplotlib.colors.to_rgba(SOLAR_PANEL))
        self.assertEqual(self.axis.yaxis.label.get_color(), SOLAR_TEXT)

    def test_shrinks_the_tick_labels(self):
        style_chart(self.figure, self.axis)

        for label in self.axis.get_yticklabels():
            self.assertEqual(label.get_fontsize(), CHART_TICK_FONT_SIZE)

    def test_caps_the_number_of_value_ticks(self):
        self.axis.plot(range(100), range(100))
        style_chart(self.figure, self.axis)
        self.figure.canvas.draw()

        self.assertLessEqual(len(self.axis.get_yticks()), 8)


class AlertTests(TkTestCase):
    def test_draw_shows_the_text_and_style_it_was_given(self):
        alert = Alert(self.window, "Привіт", GREEN_ALERT_STYLE, 3, 1).draw()

        self.assertEqual(alert._tk_element.cget("text"), "Привіт")
        self.assertEqual(alert._tk_element.grid_info()["row"], 3)
        self.assertEqual(alert._tk_element.grid_info()["column"], 1)

    def test_update_replaces_both_text_and_style(self):
        alert = Alert(self.window, "Старе", GREEN_ALERT_STYLE, 3, 1).draw()

        alert.update("Нове", RED_ALERT_STYLE)

        self.assertEqual(alert.text, "Нове")
        self.assertEqual(alert.style, RED_ALERT_STYLE)
        self.assertEqual(alert._tk_element.cget("text"), "Нове")


class DashboardAlertsTests(TkTestCase):
    def setUp(self):
        self.frame = tb.Frame(self.window)
        self.addCleanup(self.frame.destroy)
        self.balance = Balance("1000.00")
        self.balance.add_income(Income(TODAY, "500.00"))

    def test_draw_creates_one_alert_per_configured_position(self):
        dashboard = DashboardAlerts(self.frame, self.balance).draw()

        self.assertEqual(len(dashboard.alerts), len(ALERT_POSITIONS))

    def test_update_refreshes_the_text_after_the_balance_moves(self):
        dashboard = DashboardAlerts(self.frame, self.balance).draw()
        before = [alert.text for alert in dashboard.alerts]

        self.balance.add_expense(Expense(TODAY, "Їжа", "400.00"))
        dashboard.update()

        self.assertNotEqual([alert.text for alert in dashboard.alerts], before)


class DateRangeSelectorTests(TkTestCase):
    def setUp(self):
        self.frame = tb.Frame(self.window)
        self.addCleanup(self.frame.destroy)
        self.changes = []
        self.selector = DateRangeSelector(
            self.frame, row=0, column=0, padx=0,
            on_change=lambda start, end: self.changes.append((start, end)),
            show_apply=True,
        ).draw()

    def _set(self, entry, text):
        entry.entry.delete(0, "end")
        entry.entry.insert(0, text)

    def test_returns_plain_dates_not_datetimes(self):
        start, end = self.selector.get_date_range()

        self.assertIs(type(start), date)
        self.assertIs(type(end), date)

    def test_defaults_to_a_single_day_window(self):
        # Documents current behaviour: both pickers open on today, so the
        # dashboard starts filtered to one day.
        self.assertEqual(self.selector.get_date_range(), (TODAY, TODAY))

    def test_reads_back_the_dates_that_were_entered(self):
        self._set(self.selector.from_date_entry, "2026-01-05")
        self._set(self.selector.to_date_entry, "2026-03-20")

        self.assertEqual(
            self.selector.get_date_range(), (date(2026, 1, 5), date(2026, 3, 20)),
        )

    def test_a_reversed_range_is_swapped_into_order(self):
        self._set(self.selector.from_date_entry, "2026-03-20")
        self._set(self.selector.to_date_entry, "2026-01-05")

        self.assertEqual(
            self.selector.get_date_range(), (date(2026, 1, 5), date(2026, 3, 20)),
        )

    def test_applying_notifies_the_listener_with_the_range(self):
        self._set(self.selector.from_date_entry, "2026-01-05")
        self._set(self.selector.to_date_entry, "2026-02-05")

        self.selector._notify_change()

        self.assertEqual(self.changes[-1], (date(2026, 1, 5), date(2026, 2, 5)))


class GraphChartTests(TkTestCase):
    def setUp(self):
        self.frame = tb.Frame(self.window)
        self.addCleanup(self.frame.destroy)

    def _chart(self, x_data, y_data, **kwargs):
        chart = GraphChart(
            row=0, column=0, x_data=x_data, y_data=y_data, master=self.frame,
            title=TOP_CHART_TITLE, y_label=BALANCE_AXIS_LABEL,
            figsize=TOP_CHART_FIGURE_SIZE, padx=0, **kwargs,
        )
        self.addCleanup(lambda: plt.close(chart.figure))
        return chart.draw()

    def test_draw_plots_the_data_into_a_canvas(self):
        chart = self._chart(["Кві", "Тра"], [Decimal("1.00"), Decimal("2.00")])

        self.assertIsNotNone(chart.tk_canvas)
        self.assertEqual(len(chart.axis.lines), 1)
        self.assertEqual(chart.axis.get_ylabel(), BALANCE_AXIS_LABEL)

    def test_decimal_values_are_converted_for_matplotlib(self):
        chart = self._chart(["Кві"], [Decimal("1.50")])

        self.assertEqual(list(chart.axis.lines[0].get_ydata()), [1.5])

    def test_update_replaces_the_plotted_series(self):
        chart = self._chart(["Кві", "Тра"], [Decimal("1.00"), Decimal("2.00")])

        chart.update(["Чер", "Лип", "Сер"], [Decimal("5.00")] * 3)

        self.assertEqual(len(chart.axis.lines[0].get_xdata()), 3)

    def test_empty_data_shows_a_placeholder_instead_of_an_empty_grid(self):
        chart = self._chart([], [])

        self.assertIn(NO_GRAPH_DATA_TEXT, [text.get_text() for text in chart.axis.texts])

    def test_a_chart_can_recover_from_empty_to_populated(self):
        chart = self._chart([], [])

        chart.update(["Кві"], [Decimal("1.00")])

        self.assertEqual(len(chart.axis.lines), 1)

    def test_an_explicit_chart_title_is_rendered_on_the_axes(self):
        chart = self._chart(
            ["Кві"], [Decimal("1.00")], chart_title="Заголовок",
        )

        self.assertEqual(chart.axis.get_title(), "Заголовок")

    def test_custom_tick_labels_are_applied_at_the_small_font_size(self):
        chart = self._chart(
            [0, 1], [Decimal("1.00"), Decimal("2.00")],
            x_tick_labels=["Жов", "Лис"], fill_area=True,
        )

        labels = [label.get_text() for label in chart.axis.get_xticklabels()]
        self.assertEqual(labels, ["Жов", "Лис"])
        for label in chart.axis.get_xticklabels():
            self.assertEqual(label.get_fontsize(), CHART_TICK_FONT_SIZE)


class PieChartTests(TkTestCase):
    def setUp(self):
        self.frame = tb.Frame(self.window)
        self.addCleanup(self.frame.destroy)

    def _chart(self, sizes, categories, colors):
        chart = PieChart(0, 0, sizes, self.frame, categories, colors, EXPENSE_CHART_TITLE)
        drawn = chart.draw()
        self.addCleanup(lambda: plt.close(chart.figure))
        return drawn

    def test_draw_creates_one_wedge_per_category(self):
        chart = self._chart([1.0, 3.0], ["Їжа", "Бенз"], ["#cb4b16", "#2aa198"])

        self.assertEqual(len(chart.pie_slices), 2)

    def test_update_redraws_with_new_data(self):
        chart = self._chart([1.0], ["Їжа"], ["#cb4b16"])

        chart.update([1.0, 2.0, 3.0], ["Їжа", "Бенз", "Розваги"], ["#cb4b16", "#2aa198", "#b58900"])

        self.assertEqual(len(chart.pie_slices), 3)

    def test_no_expenses_shows_a_placeholder(self):
        chart = self._chart([], [], [])

        self.assertIn(NO_EXPENSES_TEXT, [text.get_text() for text in chart.axis.texts])

    def test_all_zero_totals_also_show_the_placeholder(self):
        chart = self._chart([0.0, 0.0], ["Їжа", "Бенз"], ["#cb4b16", "#2aa198"])

        self.assertIn(NO_EXPENSES_TEXT, [text.get_text() for text in chart.axis.texts])


class ExpenseTableTests(TkTestCase):
    def setUp(self):
        self.frame = tb.Frame(self.window)
        self.addCleanup(self.frame.destroy)
        self.balance = Balance("1000.00")
        for day, category, amount in (
            (date(2026, 9, 1), "Їжа", "10.00"),
            (date(2026, 9, 10), "Бенз", "20.00"),
            (date(2026, 9, 20), "Квартира", "30.00"),
        ):
            self.balance.add_expense(Expense(day, category, amount))

    def _table(self, start=None, end=None):
        table = ExpenseTable(self.frame, self.balance, start, end)
        table.draw()
        return table

    def test_draw_lists_every_expense_when_unfiltered(self):
        table = self._table()

        self.assertEqual(len(table.expense_view.get_children()), 3)

    def test_the_initial_date_range_is_applied(self):
        table = self._table(date(2026, 9, 5), date(2026, 9, 15))

        self.assertEqual(len(table.expense_view.get_children()), 1)

    def test_update_reapplies_the_filter_and_clears_stale_rows(self):
        table = self._table()

        table.update(self.balance.get_expenses(), date(2026, 9, 1), date(2026, 9, 10))

        self.assertEqual(len(table.expense_view.get_children()), 2)

    def test_rows_show_the_date_category_and_formatted_amount(self):
        table = self._table(date(2026, 9, 1), date(2026, 9, 1))

        values = table.expense_view.item(table.expense_view.get_children()[0])["values"]
        self.assertEqual(values[1], "Їжа")
        self.assertIn("10.00", str(values[2]))

    def test_update_before_draw_is_a_no_op(self):
        table = ExpenseTable(self.frame, self.balance, None, None)

        table.update(self.balance.get_expenses())  # must not raise


class InitialBalanceWindowTests(TkTestCase):
    """Exercises submit() directly; draw() blocks on wait_window."""

    def setUp(self):
        self.dialog_window = InitialBalanceWindow(self.window)
        self.dialog_window.dialog = tb.Toplevel(self.window)
        self.dialog_window.dialog.withdraw()
        self.dialog_window.lbl_error = tb.Label(self.dialog_window.dialog)
        self.addCleanup(self._destroy_dialog)

    def _destroy_dialog(self):
        if self.dialog_window.dialog.winfo_exists():
            self.dialog_window.dialog.destroy()

    def test_a_valid_amount_is_accepted_and_closes_the_dialog(self):
        self.dialog_window.balance_var.set("250.50")

        self.dialog_window.submit()

        self.assertEqual(self.dialog_window.get_result(), Decimal("250.50"))

    def test_a_comma_decimal_is_accepted(self):
        self.dialog_window.balance_var.set("250,50")

        self.dialog_window.submit()

        self.assertEqual(self.dialog_window.get_result(), Decimal("250.50"))

    def test_zero_is_a_valid_opening_balance(self):
        self.dialog_window.balance_var.set("0")

        self.dialog_window.submit()

        self.assertEqual(self.dialog_window.get_result(), Decimal("0.00"))

    def test_rubbish_is_rejected_with_a_message_and_no_result(self):
        for value in ("", "abc", "-5", "1e100"):
            with self.subTest(value=value):
                self.dialog_window.result = None
                self.dialog_window.balance_var.set(value)

                self.dialog_window.submit()

                self.assertIsNone(self.dialog_window.get_result())
                self.assertTrue(self.dialog_window.lbl_error.cget("text"))

    def test_cancelling_leaves_no_result(self):
        self.dialog_window._cancel()

        self.assertIsNone(self.dialog_window.get_result())


class SidebarTests(TkTestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.service = service_with_demo_data(self.directory.name)
        self.frame = tb.Frame(self.window)
        self.addCleanup(self.frame.destroy)
        self.sidebar = Sidebar(
            self.frame, finance_service=self.service, on_balance_changed=lambda: None,
        )
        self.sidebar.draw()

    def _button(self, label):
        return next(
            child for child in self.sidebar.tk_frame.winfo_children()
            if isinstance(child, tb.Button) and child.cget("text") == label
        )

    def test_a_sidebar_without_a_service_is_refused(self):
        with self.assertRaises(ValueError):
            Sidebar(self.frame)

    def test_categories_fall_back_to_the_defaults(self):
        self.assertTrue(self.sidebar.expense_categories)

    def test_every_action_button_is_wired_to_a_command(self):
        for label in (EXPENSE_BUTTON_TEXT, INCOME_BUTTON_TEXT, EXPORT_BUTTON_TEXT):
            with self.subTest(label=label):
                self.assertTrue(self._button(label).cget("command"))

    def test_the_balance_label_shows_the_current_value(self):
        self.assertIn("50", self.sidebar.lbl_balance.cget("text"))

    def test_refreshing_the_label_picks_up_a_new_balance(self):
        self.service.add_income("1000.00")

        self.sidebar._refresh_balance()

        self.assertIn(
            str(self.service.balance.get_value().to_integral_value())[:3],
            self.sidebar.lbl_balance.cget("text").replace(",", ""),
        )

    def test_amounts_are_parsed_with_either_decimal_separator(self):
        self.assertEqual(self.sidebar._parse_amount(" 12,50 "), Decimal("12.50"))
        self.assertEqual(self.sidebar._parse_amount("12.50"), Decimal("12.50"))

    def test_unparseable_amounts_become_none_rather_than_raising(self):
        for value in ("", "   ", "abc", "0", "-5", "1e100"):
            with self.subTest(value=value):
                self.assertIsNone(self.sidebar._parse_amount(value))


class SidebarExportTests(TkTestCase):
    def setUp(self):
        import ui.sidebar as sidebar_module

        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.messages = {"info": [], "error": []}
        self.save_as_calls = []
        self.chosen_path = ""

        class RecordingMessagebox:
            @staticmethod
            def show_info(message, title=" ", **kwargs):
                self.messages["info"].append((title, message))

            @staticmethod
            def show_error(message, title=" ", **kwargs):
                self.messages["error"].append((title, message))

        def recording_save_as(**kwargs):
            self.save_as_calls.append(kwargs)
            return self.chosen_path

        original_messagebox = sidebar_module.Messagebox
        original_save_as = sidebar_module.filedialog.asksaveasfilename
        sidebar_module.Messagebox = RecordingMessagebox
        sidebar_module.filedialog.asksaveasfilename = recording_save_as

        def restore():
            sidebar_module.Messagebox = original_messagebox
            sidebar_module.filedialog.asksaveasfilename = original_save_as

        self.addCleanup(restore)
        self.frame = tb.Frame(self.window)
        self.addCleanup(self.frame.destroy)

    def _sidebar(self, mode=APP_MODE_TEST, initial=None):
        service = FinanceService(SQLiteBalanceRepository(Path(self.directory.name) / f"{mode}.db"))
        service.initialize(mode, True, initial)
        sidebar = Sidebar(self.frame, finance_service=service, on_balance_changed=lambda: None)
        sidebar.draw()
        return sidebar

    def test_exporting_writes_the_file_and_reports_success(self):
        sidebar = self._sidebar()
        target = Path(self.directory.name) / "out.csv"
        self.chosen_path = str(target)

        sidebar._export_to_csv()

        self.assertTrue(target.exists())
        self.assertEqual(len(self.messages["info"]), 1)
        self.assertFalse(self.messages["error"])

    def test_the_save_dialog_is_offered_a_csv_name_and_extension(self):
        sidebar = self._sidebar()
        self.chosen_path = str(Path(self.directory.name) / "out.csv")

        sidebar._export_to_csv()

        self.assertEqual(self.save_as_calls[0]["defaultextension"], ".csv")
        self.assertTrue(self.save_as_calls[0]["initialfile"].endswith(".csv"))

    def test_cancelling_writes_nothing_and_says_nothing(self):
        sidebar = self._sidebar()
        self.chosen_path = ""

        sidebar._export_to_csv()

        self.assertFalse(self.messages["info"])
        self.assertFalse(self.messages["error"])

    def test_an_unwritable_destination_is_reported_not_raised(self):
        sidebar = self._sidebar()
        self.chosen_path = str(Path(self.directory.name) / "missing" / "out.csv")

        sidebar._export_to_csv()

        self.assertEqual(len(self.messages["error"]), 1)
        self.assertFalse(self.messages["info"])

    def test_an_empty_balance_short_circuits_before_the_dialog(self):
        sidebar = self._sidebar(mode=APP_MODE_DEV, initial="100.00")

        sidebar._export_to_csv()

        self.assertEqual(len(self.messages["info"]), 1)
        self.assertFalse(self.save_as_calls)


class MainWindowTests(unittest.TestCase):
    """Builds the whole dashboard; creates its own Tk root, so no TkTestCase here."""

    def setUp(self):
        from ui.main_window import MainWindow

        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        service = FinanceService(
            SQLiteBalanceRepository(Path(self.directory.name) / "main.db"),
        )
        self.main_window = MainWindow(
            APP_TITLE, APP_GEOMETRY, finance_service=service,
            app_mode=APP_MODE_TEST, reset_data_on_start=True,
        )
        self.addCleanup(self._destroy)

    def _destroy(self):
        window = getattr(self.main_window, "window", None)
        if window is not None:
            try:
                window.destroy()
            except Exception:                 # pragma: no cover - already torn down
                pass
        plt.close("all")

    def test_setup_builds_every_dashboard_component(self):
        try:
            built = self.main_window.setup()
        except Exception as error:            # pragma: no cover - display-dependent
            self.skipTest(f"Tk is unavailable here: {error}")
        self.main_window.window.withdraw()

        self.assertTrue(built)
        self.assertIsNotNone(self.main_window.sidebar)
        self.assertIsNotNone(self.main_window.top_chart)
        self.assertIsNotNone(self.main_window.pie_chart)
        self.assertIsNotNone(self.main_window.expense_table)
        self.assertIsNotNone(self.main_window.future_chart)
        self.assertIsNotNone(self.main_window.dashboard_alerts)

    def test_update_charts_survives_a_new_transaction(self):
        try:
            self.main_window.setup()
        except Exception as error:            # pragma: no cover - display-dependent
            self.skipTest(f"Tk is unavailable here: {error}")
        self.main_window.window.withdraw()

        self.main_window.finance_service.add_expense("15.00", "Їжа")
        self.main_window.update_charts()      # must not raise

        self.assertIsNotNone(self.main_window.balance)


if __name__ == "__main__":
    unittest.main()
