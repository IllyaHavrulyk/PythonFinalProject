"""Test package.

Selects the non-interactive matplotlib backend before anything imports pyplot,
so a test run never tries to open a plotting window of its own. The charts embed
themselves through FigureCanvasTkAgg explicitly, so this does not affect them.
"""
import matplotlib

matplotlib.use("Agg")
