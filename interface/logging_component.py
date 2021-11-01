import tkinter as tk
from datetime import datetime

from interface.styling import *

class Logging(tk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logging_text = tk.Text(self, height=10, width=69, state=tk.DISABLED, bg=BG_COLOR, fg=FG_COLOR_2,
                                    font=GLOBAL_FONT)
        self.logging_text.pack(side=tk.TOP)

    def add_log(self, message: str):

        self.logging_text.configure(state=tk.NORMAL)

        self.logging_text.insert('1.0', datetime.utcnow().strftime('%a %H:%M:%S :: ') + message + '\n')

        self.logging_text.configure(state=tk.DISABLED)