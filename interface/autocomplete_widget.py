import tkinter as tk
import typing


class Autocomplete(tk.Entry):
    def __init__(self, symbols: typing.List[str], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._symbols = symbols

        self._lb: tk.Listbox
        self._lb_open = False  # Used to know whether the Listbox is already open or not

        self.bind("<Up>", self._up_down)
        self.bind("<Down>", self._up_down)
        self.bind("<Right>", self._select)

        self._var = tk.StringVar()
        self.configure(textvariable=self._var)  # Links the tk.Entry content to a StringVar()
        self._var.trace("w", self._changed)  # When the self._var value changes

    def _changed(self, var_name: str, index: str, mode: str):

        """
        Open a Listbox when the tk.Entry content changes and get a list of symbols matching this content
        :param var_name:
        :param index:
        :param mode:
        :return:
        """

        self._var.set(self._var.get().upper())  # Set the content of the tk.Entry widget to uppercase as you type

        if self._var.get() == "":  # Closes the Listbox when the tk.Entry is empty
            if self._lb_open:
                self._lb.destroy()
                self._lb_open = False
        else:
            if not self._lb_open:
                self._lb = tk.Listbox(height=8)  # Limits the number of items displayed in the Listbox
                self._lb.place(x=self.winfo_x() + self.winfo_width(), y=self.winfo_y() + self.winfo_height() + 40)

                self._lb_open = True

            # Finds symbols that start with the characters that you typed in the tk.Entry widget
            symbols_matched = [symbol for symbol in self._symbols if symbol.startswith(self._var.get())]

            if len(symbols_matched) > 0:

                try:
                    self._lb.delete(0, tk.END)
                except tk.TclError:
                    pass

                for symbol in symbols_matched[:8]:  # Takes only the first 8 elements of the list to match the Listbox
                    self._lb.insert(tk.END, symbol)

            else:  # If no match, closes the Listbox if it was open
                if self._lb_open:
                    self._lb.destroy()
                    self._lb_open = False

    def _select(self, event: tk.Event):

        """
        Triggered with when the keyboard Right arrow is pressed, set the current Listbox item as a value of the
        tk.Entry widget.
        :param event:
        :return:
        """

        if self._lb_open:
            self._var.set(self._lb.get(tk.ACTIVE))
            self._lb.destroy()
            self._lb_open = False
            self.icursor(tk.END)

    def _up_down(self, event: tk.Event):

        """
        Move the Listbox cursor up or down depending on the keyboard key that was pressed.
        :param event:
        :return:
        """

        if self._lb_open:
            if self._lb.curselection() == ():  # No Listbox item selected yet
                index = -1
            else:
                index = self._lb.curselection()[0]

            lb_size = self._lb.size()

            if index > 0 and event.keysym == "Up":
                self._lb.select_clear(first=index)
                index = str(index - 1)
                self._lb.selection_set(first=index)
                self._lb.activate(index)
            elif index < lb_size - 1 and event.keysym == "Down":
                self._lb.select_clear(first=index)
                index = str(index + 1)
                self._lb.selection_set(first=index)
                self._lb.activate(index)
