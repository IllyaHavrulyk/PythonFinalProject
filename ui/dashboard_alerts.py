from calculations.dashboard_utils import build_dashboard_alerts
from constants import ALERT_POSITIONS
from ui.alert import Alert


class DashboardAlerts:
    def __init__(self, master, balance):
        self.master = master
        self.balance = balance
        self.alerts = []

    def draw(self):
        alert_data = build_dashboard_alerts(self.balance)

        self.alerts = [
            Alert(self.master, text, style, row, column).draw()
            for (text, style), (row, column) in zip(alert_data, ALERT_POSITIONS)
        ]

        return self

    def update(self):
        for alert, (text, style) in zip(
            self.alerts,
            build_dashboard_alerts(self.balance),
        ):
            alert.update(text, style)
