import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
VALID_APP_MODES = {"dev", "test"}


def _read_env_file(path):
    values = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"").strip("'")
    return values


base_environment = _read_env_file(PROJECT_ROOT / ".env")
APP_MODE = os.getenv("APP_MODE", base_environment.get("APP_MODE", "dev")).lower()
if APP_MODE not in VALID_APP_MODES:
    raise ValueError("APP_MODE must be either 'dev' or 'test'.")

profile_environment = _read_env_file(PROJECT_ROOT / f".env.{APP_MODE}")
database_name = os.getenv(
    "DATABASE_NAME",
    profile_environment.get("DATABASE_NAME", f"{APP_MODE}_expense_manager.db"),
)
DATABASE_PATH = Path(database_name)
if not DATABASE_PATH.is_absolute():
    DATABASE_PATH = PROJECT_ROOT / DATABASE_PATH

reset_value = os.getenv(
    "RESET_DATA_ON_START",
    profile_environment.get("RESET_DATA_ON_START", "false"),
)
RESET_DATA_ON_START = reset_value.lower() in {"1", "true", "yes", "on"}
