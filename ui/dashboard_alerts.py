from calculations.dashboard_utils import build_dashboard_alerts
from ui.alert import Alert


class DashboardAlerts:
    def __init__(self, master, balance):
        self.master = master
        self.balance = balance
        self.alerts = []

    def draw(self):
        positions = [(3, 1), (3, 2), (4, 1), (4, 2)]
        alert_data = build_dashboard_alerts(self.balance)

        self.alerts = [
            Alert(self.master, text, style, row, column).draw()
            for (text, style), (row, column) in zip(alert_data, positions)
        ]

        return self

    def update(self):
        for alert, (text, style) in zip(
            self.alerts,
            build_dashboard_alerts(self.balance),
        ):
            alert.update(text, style)
