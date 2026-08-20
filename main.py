import ttkbootstrap as tb
from ttkbootstrap.constants import *

import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg as tkAgg
import numpy as np

root = tb.Window(themename="minty")
root.title("Менеджер витрат")
root.geometry("1400x850")
root.minsize(1050, 700)

# Keep navigation in its own column. The chart columns are the only columns
# that grow when the window is maximized.
root.columnconfigure(0, weight=0, minsize=220)
root.columnconfigure((1, 2), weight=1, uniform="charts")
root.rowconfigure(0, weight=4)
root.rowconfigure(1, weight=0)
root.rowconfigure(2, weight=2)
root.rowconfigure((3, 4), weight=0)

# Buttons and cushion text
sidebar = tb.Frame(root, padding=(15, 18))
sidebar.grid(row=0, column=0, rowspan=5, sticky="nsew")
sidebar.columnconfigure(0, weight=1)

btn_expense = tb.Button(sidebar, text="Витрата", bootstyle="danger-outline")
btn_expense.grid(row=0, column=0, pady=(0, 12), ipady=8, sticky="ew")

btn_income = tb.Button(sidebar, text="Дохід", bootstyle="success-outline")
btn_income.grid(row=1, column=0, pady=12, ipady=8, sticky="ew")

btn_export = tb.Button(sidebar, text="Експорт (CSV)", bootstyle="warning-outline")
btn_export.grid(row=2, column=0, pady=12, ipady=8, sticky="ew")

lbl_cushion = tb.Label(
    sidebar,
    text="Подушка безпеки:\n1000 грн",
    font=("Helvetica", 12, "bold"),
    justify="center",
)
lbl_cushion.grid(row=3, column=0, pady=(28, 10), sticky="ew")

# Top dashboard matplotlib charts
frame_top_chart = tb.LabelFrame(root, text="Динаміка балансу", padding=5)
frame_top_chart.grid(row=0, column=1, padx=(0, 8), pady=10, sticky="nsew")

# Matplotlib line chart figure and axis
fig_line, ax_line = plt.subplots(figsize=(4, 2), dpi=100)
x_data = np.array([1, 2, 3, 4, 5, 6, 7])
y_data = np.array([10, 8, 12, 2, 4, 10, 29])
ax_line.plot(x_data, y_data, color="#3498db", linewidth=2.5)
ax_line.set_title("Динаміка балансу", fontsize=10)

# Render line chart figure into tkinter
canvas_line = tkAgg.FigureCanvasTkAgg(fig_line, master=frame_top_chart)
canvas_line.get_tk_widget().pack(fill=BOTH, expand=True)

# Pie chart frame
frame_pie_chart = tb.LabelFrame(root, text="Розподіл витрат", padding=5)
frame_pie_chart.grid(row=0, column=2, padx=(8, 15), pady=10, sticky="nsew")

# Matplotlib pie chart figure and axis
fig_pie, ax_pie = plt.subplots(figsize=(3, 2), dpi=100)
labels = ["Їжа", "Утиль", "Бенз", "Розваги", "Квартира"]
colors = ["#ff7675", "#74b9ff", "#ffeaa7", "#a29bfe", "#fab1a0"]
sizes = [30, 20, 15, 15, 20]
ax_pie.pie(sizes, labels=labels, colors=colors, autopct="%1.0f%%", startangle=90)
ax_pie.axis("equal")

# Render pie figure
canvas_pie = tkAgg.FigureCanvasTkAgg(fig_pie, master=frame_pie_chart)
canvas_pie.get_tk_widget().pack(fill=BOTH, expand=True)

# Date selector
frame_dates_center = tb.Frame(root)
frame_dates_center.grid(row=1, column=1, padx=(0, 8), pady=5, sticky="ew")
tb.Label(frame_dates_center, text="від").pack(side=LEFT)
tb.DateEntry(frame_dates_center, width=10).pack(side=LEFT, expand=True, padx=5)
tb.Label(frame_dates_center, text="до").pack(side=LEFT)
tb.DateEntry(frame_dates_center, width=10).pack(side=LEFT, expand=True, padx=5)

# Date selector
frame_dates_pie = tb.Frame(root)
frame_dates_pie.grid(row=1, column=2, padx=(8, 15), pady=5, sticky="ew")
tb.Label(frame_dates_pie, text="від").pack(side=LEFT)
tb.DateEntry(frame_dates_pie, width=10).pack(side=LEFT, expand=True, padx=5)
tb.Label(frame_dates_pie, text="до").pack(side=LEFT)
tb.DateEntry(frame_dates_pie, width=10).pack(side=LEFT, expand=True, padx=5)

# Create frame for long chart
frame_long_chart = tb.LabelFrame(root, text="Майбутній баланс", padding=5)
frame_long_chart.grid(row=2, column=1, columnspan=2, padx=(0, 15), pady=10, sticky="nsew")

# Create figure and axis for long chart
fig_long, ax_long = plt.subplots(figsize=(8, 1.0), dpi=100)
x_wave = np.linspace(0, 15, 100)
y_wave = np.sin(x_wave) * np.cos(x_wave * 0.5) + (x_wave * 0.2)
ax_long.plot(x_wave, y_wave, color="#2ecc71", linewidth=2)
ax_long.fill_between(x_wave, y_wave, color="#2ecc71", linewidth=0.1)

# Render long canvas
canvas_long = tkAgg.FigureCanvasTkAgg(fig_long, master=frame_long_chart)
canvas_long.get_tk_widget().pack(fill=BOTH, expand=TRUE)

# Render alerts
alert_orange = tb.Label(
    root,
    text="Ви витратили на їжу на 1000грн більше цього місяця!!",
    bootstyle="warning-inverse",
    padding=10,
    anchor="center",
)
alert_orange.grid(row=3, column=1, padx=(0, 8), pady=5, sticky="ew")

alert_orange = tb.Label(
    root,
    text="Ваші витрати перевищують 50% вашого доходу!",
    bootstyle="danger-inverse",
    padding=10,
    anchor="center",
)
alert_orange.grid(row=3, column=2, padx=(8, 15), pady=5, sticky="ew")

alert_orange = tb.Label(
    root,
    text="Ви витратили на бензин на 500грн менше цього місяця!!",
    bootstyle="success-inverse",
    padding=10,
    anchor="center",
)
alert_orange.grid(row=4, column=1, padx=(0, 8), pady=5, sticky="ew")

alert_orange = tb.Label(
    root,
    text="Ріст балансу сповільнився на 25% за 3 міс!",
    bootstyle="danger-inverse",
    padding=10,
    anchor="center",
)
alert_orange.grid(row=4, column=2, padx=(8, 15), pady=5, sticky="ew")

root.mainloop()
