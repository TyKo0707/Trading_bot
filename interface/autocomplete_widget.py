import tkinter as tk
import typing

class Autocomplete(tk.Entry):
    def __init__(self, symbols: typing.List[str], *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._symbols = symbols

        self._lb = tk.Listbox()

        self._var = tk.StringVar()
        self.configure(textvariable=self._var)
        self._var.trace('w', self._changed)

    def _changed(self, var_name: str, index: str, mode: str):

        self._var.set(self._var.get().upper())

        self._lb = tk.Listbox(height=8)
        self._lb.place(x=self.winfo_x(), y=self.winfo_y())