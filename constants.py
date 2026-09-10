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
BALANCE_UNCHANGED_TEXT = "не змінився"
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
    "Jan": "Січ", "Feb": "Лют", "Mar": "Бер", "Apr": "Кві",
    "May": "Тра", "Jun": "Чер", "Jul": "Лип", "Aug": "Сер",
    "Sep": "Вер", "Oct": "Жов", "Nov": "Лис", "Dec": "Гру",
}

# Mock data used only in APP_MODE=test
MOCK_INITIAL_BALANCE = 42_000
MOCK_TRANSACTION_DAY = 15
MOCK_MONTHLY_INCOMES = [12_500, 13_200, 12_800, 14_000, 13_800, 15_000]
MOCK_MONTHLY_EXPENSES = [
    [("Їжа", 3_200), ("Квартира", 5_500)],
    [("Їжа", 3_450), ("Бенз", 1_600)],
    [("Квартира", 5_500), ("Розваги", 1_300)],
    [("Їжа", 3_100), ("Утиль", 1_100)],
    [("Бенз", 1_850), ("Розваги", 1_500)],
    [("Їжа", 3_600), ("Квартира", 5_500), ("Розваги", 1_200)],
]
