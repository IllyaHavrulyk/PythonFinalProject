from constants import APP_GEOMETRY, APP_TITLE
from config import APP_MODE, DATABASE_PATH, RESET_DATA_ON_START
from persistence.sqlite_repository import SQLiteBalanceRepository
from services.finance_service import FinanceService
from ui.main_window import MainWindow


if __name__ == "__main__":
    repository = SQLiteBalanceRepository(DATABASE_PATH)
    finance_service = FinanceService(repository)
    main_window = MainWindow(
        APP_TITLE,
        APP_GEOMETRY,
        finance_service=finance_service,
        app_mode=APP_MODE,
        reset_data_on_start=RESET_DATA_ON_START,
    )
    main_window.start()
