from matplotlib.ticker import MaxNLocator

from constants import (
    CHART_AXIS_LABEL_FONT_SIZE,
    CHART_GRID_ALPHA,
    CHART_TICK_FONT_SIZE,
    MAX_Y_AXIS_TICKS,
    SOLAR_GRID,
    SOLAR_PANEL,
    SOLAR_TEXT,
)


def style_chart(figure, axis):
    figure.patch.set_facecolor(SOLAR_PANEL)
    axis.set_facecolor(SOLAR_PANEL)
    axis.tick_params(colors=SOLAR_TEXT, labelsize=CHART_TICK_FONT_SIZE)
    axis.xaxis.label.set_color(SOLAR_TEXT)
    axis.yaxis.label.set_color(SOLAR_TEXT)
    axis.xaxis.label.set_fontsize(CHART_AXIS_LABEL_FONT_SIZE)
    axis.yaxis.label.set_fontsize(CHART_AXIS_LABEL_FONT_SIZE)
    axis.title.set_color(SOLAR_TEXT)
    axis.grid(color=SOLAR_GRID, alpha=CHART_GRID_ALPHA)
    # Cap the value ticks so they keep their spacing in a short window. The other
    # axis is left alone: it carries month names, which are already one per point.
    axis.yaxis.set_major_locator(MaxNLocator(nbins=MAX_Y_AXIS_TICKS))
    for spine in axis.spines.values():
        spine.set_color(SOLAR_GRID)
