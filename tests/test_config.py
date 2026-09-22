import importlib
import os
import tempfile
import unittest
from pathlib import Path

import config


class ReadEnvFileTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)

    def _write(self, text):
        path = Path(self.directory.name) / ".env"
        path.write_text(text, encoding="utf-8")
        return path

    def test_missing_file_yields_no_values(self):
        missing = Path(self.directory.name) / "absent"

        self.assertEqual(config._read_env_file(missing), {})

    def test_reads_key_value_pairs(self):
        path = self._write("APP_MODE=test\nDATABASE_NAME=a.db\n")

        self.assertEqual(
            config._read_env_file(path),
            {"APP_MODE": "test", "DATABASE_NAME": "a.db"},
        )

    def test_skips_comments_blank_lines_and_lines_without_an_equals(self):
        path = self._write("# comment\n\n   \nNOT_A_PAIR\nAPP_MODE=dev\n")

        self.assertEqual(config._read_env_file(path), {"APP_MODE": "dev"})

    def test_strips_whitespace_and_surrounding_quotes(self):
        path = self._write('  APP_MODE  =  "test"  \nNAME=\'x.db\'\n')

        self.assertEqual(
            config._read_env_file(path),
            {"APP_MODE": "test", "NAME": "x.db"},
        )

    def test_keeps_equals_signs_inside_the_value(self):
        path = self._write("TOKEN=a=b=c\n")

        self.assertEqual(config._read_env_file(path), {"TOKEN": "a=b=c"})


class ConfigResolutionTests(unittest.TestCase):
    """Reloads config with the environment patched.

    Environment variables win over the .env files, so these assertions do not
    depend on whatever .env happens to sit in the working copy.
    """

    def setUp(self):
        self.original_environment = dict(os.environ)
        self.addCleanup(self._restore_environment)

    def _restore_environment(self):
        os.environ.clear()
        os.environ.update(self.original_environment)
        importlib.reload(config)

    def _reload_with(self, **variables):
        for key in ("APP_MODE", "DATABASE_NAME", "RESET_DATA_ON_START"):
            os.environ.pop(key, None)
        os.environ.update(variables)
        return importlib.reload(config)

    def test_app_mode_comes_from_the_environment_and_is_lowercased(self):
        self.assertEqual(self._reload_with(APP_MODE="TEST").APP_MODE, "test")

    def test_an_unknown_app_mode_is_rejected(self):
        with self.assertRaises(ValueError):
            self._reload_with(APP_MODE="production")

    def test_a_relative_database_name_is_anchored_to_the_project_root(self):
        reloaded = self._reload_with(APP_MODE="dev", DATABASE_NAME="custom.db")

        self.assertTrue(reloaded.DATABASE_PATH.is_absolute())
        self.assertEqual(reloaded.DATABASE_PATH.parent, reloaded.PROJECT_ROOT)
        self.assertEqual(reloaded.DATABASE_PATH.name, "custom.db")

    def test_an_absolute_database_name_is_used_as_given(self):
        absolute = Path(tempfile.gettempdir()).resolve() / "elsewhere.db"

        reloaded = self._reload_with(APP_MODE="dev", DATABASE_NAME=str(absolute))

        self.assertEqual(reloaded.DATABASE_PATH, absolute)

    def test_reset_flag_accepts_the_usual_spellings_of_true(self):
        for value in ("1", "true", "TRUE", "Yes", "on"):
            with self.subTest(value=value):
                reloaded = self._reload_with(APP_MODE="test", RESET_DATA_ON_START=value)
                self.assertTrue(reloaded.RESET_DATA_ON_START)

    def test_reset_flag_is_false_for_anything_else(self):
        for value in ("0", "false", "no", "off", "", "maybe"):
            with self.subTest(value=value):
                reloaded = self._reload_with(APP_MODE="test", RESET_DATA_ON_START=value)
                self.assertFalse(reloaded.RESET_DATA_ON_START)


if __name__ == "__main__":
    unittest.main()
