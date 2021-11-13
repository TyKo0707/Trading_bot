import tkinter as tk
import typing

class Autocomplete(tk.Entry):
    def __init__(self, symbols: typing.List[str], *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._symbols = symbols

        self._lb = tk.Listbox()
        self._lb_open = False

        self.bind('<Up>', self._up_down)
        self.bind('<Down>', self._up_down)
        self.bind('<Right>', self._select)

        self._var = tk.StringVar()
        self.configure(textvariable=self._var)
        self._var.trace('w', self._changed)

    def _changed(self, var_name: str, index: str, mode: str):

        self._var.set(self._var.get().upper())

        if self._var.get() == '':
            if self._lb_open:
                self._lb.destroy()
                self._lb_open = False
        else:
            if not self._lb_open:
                self._lb = tk.Listbox(height=8)
                self._lb.place(x=self.winfo_x() + self.winfo_width(), y=self.winfo_y() + self.winfo_height() + 10)
                self._lb_open = True

            symbols_matched = [symbol for symbol in self._symbols if symbol.startswith(self._var.get())]

            if len(symbols_matched) > 0:

                try:
                    self._lb.delete(0, tk.END)
                except tk.TclError:
                    pass

                for symbol in symbols_matched:
                    self._lb.insert(tk.END, symbol)

            else:
                if self._lb_open:
                    self._lb.destroy()
                    self._lb_open = False

    def _select(self, event: tk.Event):

        if self._lb_open:
            self._var.set(self._lb.get(tk.ACTIVE))
            self._lb.destroy()
            self._lb_open = False
            self.icursor(tk.END)

    def _up_down(self, event: tk.Event):

        if self._lb_open:
            if self._lb.curselection() == ():
                index = -1
            else:
                index = self._lb.curselection()[0]

            lb_size = self._lb.size()

            if index > 0 and event.keysym == 'Up':
                self._lb.select_clear(first=index)
                index = str(index - 1)
                self._lb.select_set(first=str(index))
                self._lb.activate(index)

            elif index < lb_size - 1 and event.keysym == 'Down':
                self._lb.select_clear(first=index)
                index = str(index + 1)
                self._lb.select_set(first=str(index))
                self._lb.activate(index)
