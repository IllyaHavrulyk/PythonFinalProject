from constants import *
from ui.alert import Alert


class DashboardAlerts:
    def __init__(self, master):
        self.master = master
        self.alerts = []

    def draw(self):
        alert_configs = [
            (SPEND_INCOME_DIFF_TEXT_TEMPLATE, ORANGE_ALERT_STYLE, 3, 1),
            (SPEND_DIFF_TEXT_TEMPLATE, ORANGE_ALERT_STYLE, 3, 2),
            (BALANCE_GROWTH_TEXT_TEMPLATE, RED_ALERT_STYLE, 4, 1),
            (SPEND_DIFF_TEXT_TEMPLATE, GREEN_ALERT_STYLE, 4, 2),
        ]

        self.alerts = [
            Alert(self.master, text, style, row, column).draw()
            for text, style, row, column in alert_configs
        ]
        return self
