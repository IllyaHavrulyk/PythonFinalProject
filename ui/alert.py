import ttkbootstrap as tb

class Alert:
    def __init__(self, master, text, style, row, column):
        self.master = master
        self.text = text
        self.style = style
        self.row = row
        self.column = column
        self.__tk_element = None
    
    def draw(self):
        self.__tk_element = tb.Label(
                    self.master,
                    text=self.text,
                    bootstyle=self.style,
                    padding=10,
                    anchor="center",
                )
        self.__tk_element.grid(row=self.row, column=self.column, padx=(8, 15), pady=5, sticky="ew")
        return self