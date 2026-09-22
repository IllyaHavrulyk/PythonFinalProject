"""Shared helpers for the test suite."""
import tempfile
import unittest
from pathlib import Path

from persistence.sqlite_repository import SQLiteBalanceRepository
from services.finance_service import FinanceService


class TemporaryDatabaseTestCase(unittest.TestCase):
    """Gives each test its own SQLite file, removed again on teardown."""

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.directory = Path(self.temporary_directory.name)
        self.repository = SQLiteBalanceRepository(self.directory / "test.db")
        self.service = FinanceService(self.repository)


class TkTestCase(unittest.TestCase):
    """Builds one hidden ttkbootstrap window per test.

    Tk needs a display, which a headless build server may not have, so the whole
    case skips rather than fails when the window cannot be created.
    """

    @classmethod
    def setUpClass(cls):
        import ttkbootstrap as tb

        from constants import APP_THEME

        try:
            cls.window = tb.Window(themename=APP_THEME)
        except Exception as error:            # pragma: no cover - display-dependent
            raise unittest.SkipTest(f"Tk is unavailable here: {error}")
        cls.window.withdraw()

    @classmethod
    def tearDownClass(cls):
        window = getattr(cls, "window", None)
        if window is not None:
            window.destroy()

    def flush_events(self):
        """Let Tk process anything the widget under test queued."""
        self.window.update_idletasks()
