import csv
import tempfile
import unittest
from datetime import date
from pathlib import Path

from constants import (
    CSV_DELIMITER,
    CSV_ENCODING,
    CSV_EXPENSE_LABEL,
    CSV_HEADERS,
    CSV_INCOME_LABEL,
)
from persistence.csv_exporter import export_transactions
from persistence.sqlite_repository import SQLiteBalanceRepository
from services.finance_service import FinanceService


class CsvExportTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.export_path = Path(self.temporary_directory.name) / "export.csv"
        repository = SQLiteBalanceRepository(
            Path(self.temporary_directory.name) / "test.db",
        )
        self.service = FinanceService(repository)
        self.service.initialize("dev", False, "100.00")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def _read_rows(self):
        with open(self.export_path, encoding=CSV_ENCODING, newline="") as csv_file:
            return list(csv.reader(csv_file, delimiter=CSV_DELIMITER))

    def test_export_writes_every_transaction_oldest_first(self):
        self.service.add_expense("40.00", "Їжа", date(2026, 9, 11))
        self.service.add_income("25.50", date(2026, 9, 9))

        exported = self.service.export_transactions(self.export_path)
        header, *rows = self._read_rows()

        self.assertEqual(exported, 2)
        self.assertEqual(header, list(CSV_HEADERS))
        self.assertEqual(rows[0], ["2026-09-09", CSV_INCOME_LABEL, "", "25,50"])
        self.assertEqual(rows[1], ["2026-09-11", CSV_EXPENSE_LABEL, "Їжа", "40,00"])

    def test_export_keeps_money_exact(self):
        self.service.add_expense("0.10", "Їжа", date(2026, 9, 11))

        self.service.export_transactions(self.export_path)

        self.assertEqual(self._read_rows()[1][3], "0,10")

    def test_export_never_emits_a_dot_as_a_decimal_separator(self):
        self.service.add_expense("1234.50", "Квартира", date(2026, 9, 11))
        self.service.add_income("9876.05", date(2026, 9, 10))

        self.service.export_transactions(self.export_path)
        amounts = [row[3] for row in self._read_rows()[1:]]

        self.assertEqual(amounts, ["9876,05", "1234,50"])
        self.assertNotIn(".", self.export_path.read_text(encoding=CSV_ENCODING))

    def test_export_writes_a_bom_so_excel_reads_cyrillic(self):
        self.service.export_transactions(self.export_path)

        self.assertTrue(self.export_path.read_bytes().startswith(b"\xef\xbb\xbf"))

    def test_export_does_not_leave_blank_lines_between_rows(self):
        self.service.add_income("10.00", date(2026, 9, 9))

        self.service.export_transactions(self.export_path)
        text = self.export_path.read_text(encoding=CSV_ENCODING)

        self.assertNotIn("\r\r\n", text)
        self.assertEqual(len(text.strip().splitlines()), 2)

    def test_export_of_an_empty_balance_writes_only_the_header(self):
        exported = self.service.export_transactions(self.export_path)

        self.assertEqual(exported, 0)
        self.assertEqual(self._read_rows(), [list(CSV_HEADERS)])

    def test_export_reports_an_unwritable_destination(self):
        with self.assertRaises(OSError):
            export_transactions(
                self.service.balance,
                Path(self.temporary_directory.name) / "missing" / "export.csv",
            )


if __name__ == "__main__":
    unittest.main()
