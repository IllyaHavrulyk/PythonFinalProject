# Application
APP_TITLE = "Менеджер витрат"
APP_GEOMETRY = "1920x1080"
APP_THEME = "solar"
APP_MIN_WIDTH = 1050
APP_MIN_HEIGHT = 700
APP_MODE_DEV = "dev"
APP_MODE_TEST = "test"

# Colors and styles
SOLAR_PANEL = "#073642"
SOLAR_TEXT = "#eee8d5"
SOLAR_GRID = "#586e75"
SOLAR_YELLOW = "#f4d35e"
PIE_RED = "#cb4b16"
PIE_BLUE = "#2aa198"
PIE_YELLOW = "#b58900"
PIE_PURPLE = "#6c71c4"
PIE_PINK = "#d33682"
DANGER_STYLE = "danger"
SUCCESS_STYLE = "success"
EXPENSE_BUTTON_STYLE = "danger-outline"
INCOME_BUTTON_STYLE = "success-outline"
EXPORT_BUTTON_STYLE = "warning-outline"
APPLY_BUTTON_STYLE = "info-outline"
RED_ALERT_STYLE = "danger-inverse"
GREEN_ALERT_STYLE = "success-inverse"
ORANGE_ALERT_STYLE = "warning-inverse"

# Typography and spacing
FONT_FAMILY = "Helvetica"
FONT_WEIGHT_BOLD = "bold"
BODY_FONT_SIZE = 12
DIALOG_TITLE_FONT_SIZE = 13
CHART_TITLE_FONT_SIZE = 10
CHART_TICK_FONT_SIZE = 7
CHART_AXIS_LABEL_FONT_SIZE = 8
PIE_LABEL_FONT_SIZE = 7
MAX_Y_AXIS_TICKS = 5
PANEL_PADDING = 5
DIALOG_PADDING = 24
SIDEBAR_PADDING = (15, 18)
ALERT_PADDING = 10
CONTROL_GAP = 5
CHART_VERTICAL_PADDING = 10
RIGHT_PANEL_PADDING = (8, 15)
LEFT_CHART_PADDING = (0, 8)
FORECAST_CHART_PADDING = (0, 15)
DIALOG_TITLE_PADDING = (0, 12)
FIELD_LABEL_PADDING = (0, 8)
SIDEBAR_FIRST_BUTTON_PADDING = (0, 12)
SIDEBAR_BUTTON_PADDING = 12
SIDEBAR_INFO_PADDING = (28, 10)
SIDEBAR_BUTTON_INTERNAL_PADDING = 8
DIALOG_BUTTON_INTERNAL_PADDING = 4

# Widget and chart dimensions
SIDEBAR_MIN_WIDTH = 220
DATE_CONTROLS_MIN_HEIGHT = 150
FORECAST_CHART_MIN_HEIGHT = 180
DIALOG_ENTRY_WIDTH = 28
CATEGORY_ENTRY_WIDTH = 26
DATE_ENTRY_WIDTH = 10
EXPENSE_TABLE_HEIGHT = 4
DATE_COLUMN_WIDTH = 90
CATEGORY_COLUMN_WIDTH = 110
AMOUNT_COLUMN_WIDTH = 90
TOP_CHART_FIGURE_SIZE = (4, 2)
PIE_CHART_FIGURE_SIZE = (3, 2)
FORECAST_CHART_FIGURE_SIZE = (8, 1.5)
CHART_DPI = 100
DEFAULT_LINE_WIDTH = 2.5
FORECAST_LINE_WIDTH = 2
CHART_FILL_ALPHA = 0.3
CHART_GRID_ALPHA = 0.25
PIE_START_ANGLE = 90
PIE_PERCENT_FORMAT = "%1.0f%%"
TOPMOST_DELAY_MS = 250

# Financial and analytics settings
CURRENCY_LABEL = "грн"
AMOUNT_FORMAT_SPEC = ",.2f"
INTEGER_AMOUNT_FORMAT_SPEC = ",.0f"
PERCENT_FORMAT_SPEC = ".1f"
THOUSANDS_SEPARATOR = " "
MONEY_DECIMAL_PLACES = 2
KOPECKS_PER_HRYVNIA = 100
DEFAULT_BALANCE = 0
INPUT_DECIMAL_SEPARATOR = ","
NORMALIZED_DECIMAL_SEPARATOR = "."
BALANCE_HISTORY_MONTHS = 6
FORECAST_MONTHS = 6
BALANCE_TREND_MONTHS = 3
SPEND_WARNING_PERCENTAGE = 80
SPEND_DANGER_PERCENTAGE = 100
SAFETY_CUSHION = 1_000

# Main dashboard copy
TOP_CHART_TITLE = "Динаміка балансу"
EXPENSE_CHART_TITLE = "Розподіл витрат"
FORECAST_CHART_TITLE = "Майбутній баланс"
BALANCE_AXIS_LABEL = "Баланс, грн"
CURRENCY_AXIS_LABEL = CURRENCY_LABEL
NO_GRAPH_DATA_TEXT = "Немає даних"
NO_EXPENSES_TEXT = "Немає витрат"

# Sidebar and transaction dialogs
EXPENSE_BUTTON_TEXT = "Витрата"
INCOME_BUTTON_TEXT = "Дохід"
EXPORT_BUTTON_TEXT = "Експорт (CSV)"
EXPORT_DIALOG_TITLE = "Зберегти експорт"
EXPORT_DEFAULT_FILENAME = "transactions.csv"
EXPORT_FILE_EXTENSION = ".csv"
EXPORT_FILE_TYPES = [("CSV", "*.csv"), ("Усі файли", "*.*")]
EXPORT_SUCCESS_TITLE = "Експорт завершено"
EXPORT_SUCCESS_TEXT_TEMPLATE = "Збережено записів: {count}\n{path}"
EXPORT_EMPTY_TITLE = "Немає даних"
EXPORT_EMPTY_TEXT = "Ще немає доходів або витрат для експорту."
EXPORT_ERROR_TITLE = "Помилка експорту"
EXPORT_ERROR_TEXT_TEMPLATE = "Не вдалося зберегти файл:\n{error}"
CSV_ENCODING = "utf-8-sig"
# Excel opened by double-click splits on the system list separator, which is ";"
# in a Ukrainian locale. RFC 4180 readers (pandas, Sheets) accept it when told.
CSV_DELIMITER = ";"
# Ukrainian Excel reads "5500.00" as text; with a comma it is a number.
CSV_DECIMAL_SEPARATOR = ","
CSV_HEADERS = ("Дата", "Тип", "Категорія", "Сума")
CSV_INCOME_LABEL = "Дохід"
CSV_EXPENSE_LABEL = "Витрата"
CSV_NO_CATEGORY = ""
ADD_BUTTON_TEXT = "Додати"
INCOME_DIALOG_TITLE = "Додати дохід"
EXPENSE_DIALOG_TITLE = "Додати витрату"
INCOME_AMOUNT_LABEL = "Сума доходу"
EXPENSE_AMOUNT_LABEL = "Сума витрати"
CATEGORY_LABEL = "Категорія"
ENTER_AMOUNT_ERROR = "Введіть суму"
ENTER_VALID_AMOUNT_ERROR = "Введіть коректну суму"
BALANCE_TEXT_TEMPLATE = "Баланс:\n{balance:,.2f} {currency}"
SAFETY_CUSHION_TEXT_TEMPLATE = "Подушка безпеки:\n{amount} {currency}"

# Initial balance dialog
INITIAL_BALANCE_DIALOG_TITLE = "Початковий баланс"
INITIAL_BALANCE_PROMPT = "Введіть початковий баланс"
START_BUTTON_TEXT = "Почати"
INVALID_NUMBER_ERROR = "Введіть коректне число"

# Date selector and expense table
DATE_FROM_TEXT = "від"
DATE_TO_TEXT = "до"
APPLY_BUTTON_TEXT = "Застосувати"
DATE_FORMAT = "%Y-%m-%d"
DATE_SELECTED_EVENT = "<<DateEntrySelected>>"
ENTER_KEY_EVENT = "<Return>"
FOCUS_OUT_EVENT = "<FocusOut>"
CLOSE_WINDOW_EVENT = "WM_DELETE_WINDOW"
EXPENSE_TABLE_TITLE = "Витрати за період"
DATE_HEADING = "Дата"
CATEGORY_HEADING = CATEGORY_LABEL
AMOUNT_HEADING = "Сума"
EXPENSE_AMOUNT_TEXT_TEMPLATE = "{amount:,.2f} {currency}"

# Dashboard alerts
SPEND_INCOME_DIFF_TEXT_TEMPLATE = "Витрати становлять {percentage}% доходу цього місяця."
SPEND_DIFF_TEXT_TEMPLATE = "Найбільше витрат на «{category}»: {number} грн цього місяця."
BALANCE_GROWTH_TEXT_TEMPLATE = "Баланс {diff} на {percentage}% за останні {months} місяці."
ZERO_BALANCE_CHANGE_TEXT_TEMPLATE = "Зміна балансу за останні {months} місяці: {amount} грн."
FORECAST_TEXT_TEMPLATE = "Очікуваний баланс через {months} місяців: {balance} грн."
NO_ACTIVITY_TEXT = "Додайте дохід або витрату, щоб побачити аналітику."
NO_INCOME_TEXT_TEMPLATE = "Витрати цього місяця: {amount} грн. Доходів ще немає."
NO_MONTHLY_EXPENSES_TEXT = "Цього місяця витрат ще немає."
BALANCE_INCREASED_TEXT = "зріс"
BALANCE_DECREASED_TEXT = "зменшився"
ALERT_POSITIONS = [(3, 1), (3, 2), (4, 1), (4, 2)]

# Categories and month labels
EXPENSE_CATEGORIES = ["Їжа", "Утиль", "Бенз", "Розваги", "Квартира"]
DEFAULT_EXPENSE_CATEGORY = EXPENSE_CATEGORIES[0]
EXPENSE_COLORS = {
    "Їжа": PIE_RED,
    "Утиль": PIE_BLUE,
    "Бенз": PIE_YELLOW,
    "Розваги": PIE_PURPLE,
    "Квартира": PIE_PINK,
}
MONTHS_TRANSLATION = {
    1: "Січ", 2: "Лют", 3: "Бер", 4: "Кві",
    5: "Тра", 6: "Чер", 7: "Лип", 8: "Сер",
    9: "Вер", 10: "Жов", 11: "Лис", 12: "Гру",
}

# Mock data used only in APP_MODE=test.
# Incomes are (day, amount); expenses are (day, category, amount). Days beyond the
# length of a real month, or in the future for the current month, are clamped.
MOCK_INITIAL_BALANCE = 42_000
MOCK_MONTHLY_INCOMES = [
    [(5, 12_500)],
    [(5, 13_200), (22, 2_400)],
    [(5, 12_800)],
    [(5, 14_000)],
    [(5, 13_800), (19, 1_900)],
    [(5, 15_000)],
]
MOCK_MONTHLY_EXPENSES = [
    [
        (3, "Квартира", 5_500),
        (6, "Їжа", 1_150),
        (9, "Утиль", 1_080),
        (11, "Бенз", 820),
        (13, "Їжа", 890),
        (16, "Розваги", 540),
        (19, "Їжа", 1_240),
        (24, "Бенз", 760),
    ],
    [
        (3, "Квартира", 5_500),
        (7, "Їжа", 1_320),
        (10, "Утиль", 1_240),
        (12, "Бенз", 910),
        (15, "Їжа", 780),
        (18, "Розваги", 1_150),
        (21, "Їжа", 1_060),
        (27, "Бенз", 840),
    ],
    [
        (3, "Квартира", 5_500),
        (6, "Їжа", 1_080),
        (9, "Утиль", 2_180),
        (12, "Бенз", 880),
        (14, "Їжа", 1_390),
        (17, "Розваги", 920),
        (20, "Їжа", 950),
        (23, "Бенз", 790),
        (28, "Їжа", 1_120),
    ],
    [
        (3, "Квартира", 5_500),
        (8, "Їжа", 1_210),
        (10, "Утиль", 1_460),
        (13, "Бенз", 850),
        (16, "Їжа", 830),
        (21, "Їжа", 1_170),
        (25, "Розваги", 610),
    ],
    [
        (3, "Квартира", 5_500),
        (6, "Їжа", 940),
        (9, "Утиль", 1_120),
        (11, "Бенз", 930),
        (14, "Їжа", 1_280),
        (17, "Розваги", 1_480),
        (20, "Їжа", 870),
        (26, "Бенз", 800),
        (28, "Їжа", 1_030),
    ],
    [
        (3, "Квартира", 5_500),
        (7, "Їжа", 1_190),
        (9, "Утиль", 1_060),
        (11, "Бенз", 870),
        (13, "Їжа", 1_240),
        (16, "Розваги", 900),
        (20, "Їжа", 880),
    ],
]
