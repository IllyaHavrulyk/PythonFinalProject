from constants import *


def style_chart(figure, axis):
    figure.patch.set_facecolor(SOLAR_PANEL)
    axis.set_facecolor(SOLAR_PANEL)
    axis.tick_params(colors=SOLAR_TEXT)
    axis.xaxis.label.set_color(SOLAR_TEXT)
    axis.yaxis.label.set_color(SOLAR_TEXT)
    axis.title.set_color(SOLAR_TEXT)
    axis.grid(color=SOLAR_GRID, alpha=0.25)
    for spine in axis.spines.values():
        spine.set_color(SOLAR_GRID)
