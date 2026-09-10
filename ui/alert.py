import ttkbootstrap as tb

from constants import ALERT_PADDING, CONTROL_GAP, RIGHT_PANEL_PADDING

class Alert:
    def __init__(self, master, text, style, row, column):
        self.master = master
        self.text = text
        self.style = style
        self.row = row
        self.column = column
        self._tk_element = None
    
    def draw(self):
        self._tk_element = tb.Label(
                    self.master,
                    text=self.text,
                    bootstyle=self.style,
                    padding=ALERT_PADDING,
                    anchor="center",
                )
        self._tk_element.grid(
            row=self.row,
            column=self.column,
            padx=RIGHT_PANEL_PADDING,
            pady=CONTROL_GAP,
            sticky="ew",
        )
        return self

    def update(self, text, style):
        self.text = text
        self.style = style
        self._tk_element.configure(text=text, bootstyle=style)
