import tkinter as tk
import typing

from database import WorkspaceData
from interface.autocomplete_widget import Autocomplete
from interface.scrollable_frame import ScrollableFrame
from interface.styling import *
from models import *


class WatchList(tk.Frame):
    def __init__(self, binance_contracts: typing.Dict[str, Contract], bitmex_contracts: typing.Dict[str, Contract],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.db = WorkspaceData()

        self.binance_symbols = list(binance_contracts.keys())
        self.bitmex_symbols = list(bitmex_contracts.keys())

        self._commands_frame = tk.Frame(self, bg=BG_COLOR)
        self._commands_frame.pack(side=tk.TOP)

        self._table_frame = tk.Frame(self, bg=BG_COLOR)
        self._table_frame.pack(side=tk.TOP)

        self._binance_label = tk.Label(self._commands_frame, text="Binance", bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT)
        self._binance_label.grid(row=0, column=0)

        self._binance_entry = Autocomplete(self.binance_symbols, self._commands_frame, fg=FG_COLOR, justify=tk.CENTER, insertbackground=FG_COLOR,
                                       bg=BG_COLOR_2)
        self._binance_entry.bind("<Return>", self._add_binance_symbol)
        self._binance_entry.grid(row=1, column=0)

        self._bitmex_label = tk.Label(self._commands_frame, text="Bitmex", bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT)
        self._bitmex_label.grid(row=0, column=1)

        self._bitmex_entry = Autocomplete(self.bitmex_symbols, self._commands_frame, fg=FG_COLOR, justify=tk.CENTER, insertbackground=FG_COLOR,
                                      bg=BG_COLOR_2)
        self._bitmex_entry.bind("<Return>", self._add_bitmex_symbol)
        self._bitmex_entry.grid(row=1, column=1)

        self.body_widgets = dict()

        self._headers = ["symbol", "exchange", "bid", "ask", "remove"]

        self._headers_frame = tk.Frame(self._table_frame, bg=BG_COLOR)

        self._col_width = 11

        for idx, h in enumerate(self._headers):
            header = tk.Label(self._headers_frame, text=h.capitalize() if h != "remove" else "", bg=BG_COLOR,
                              fg=FG_COLOR, font=GLOBAL_FONT, width=self._col_width)
            header.grid(row=0, column=idx)

        header = tk.Label(self._headers_frame, text="", bg=BG_COLOR,
                          fg=FG_COLOR, font=GLOBAL_FONT, width=2)
        header.grid(row=0, column=len(self._headers))

        self._headers_frame.pack(side=tk.TOP, anchor='nw')

        self._body_frame = ScrollableFrame(self._table_frame, bg=BG_COLOR, height=250)
        self._body_frame.pack(side=tk.TOP, fill=tk.X, anchor='nw')

        for h in self._headers:
            self.body_widgets[h] = dict()
            if h in ["bid", "ask"]:
                self.body_widgets[h + "_var"] = dict()

        self._body_index = 0

        saved_symbols = self.db.get('watchlist')

        for s in saved_symbols:
            self._add_symbol(s['symbol'], s['exchange'])

    def _remove_symbol(self, b_index: int):

        for h in self._headers:
            self.body_widgets[h][b_index].grid_forget()
            del self.body_widgets[h][b_index]

    def _add_binance_symbol(self, event):
        symbol = event.widget.get()

        if symbol in self.binance_symbols:
            self._add_symbol(symbol, "Binance")
            event.widget.delete(0, tk.END)

    def _add_bitmex_symbol(self, event):
        symbol = event.widget.get()

        if symbol in self.bitmex_symbols:
            self._add_symbol(symbol, "Bitmex")
            event.widget.delete(0, tk.END)

    def _add_symbol(self, symbol: str, exchange: str):

        b_index = self._body_index

        self.body_widgets['symbol'][b_index] = tk.Label(self._body_frame.sub_frame, text=symbol, bg=BG_COLOR, fg=FG_COLOR_2,
                                                        font=GLOBAL_FONT, width=self._col_width)
        self.body_widgets['symbol'][b_index].grid(row=b_index, column=0)

        self.body_widgets['exchange'][b_index] = tk.Label(self._body_frame.sub_frame, text=exchange, bg=BG_COLOR, fg=FG_COLOR_2,
                                                          font=GLOBAL_FONT, width=self._col_width)
        self.body_widgets['exchange'][b_index].grid(row=b_index, column=1)

        self.body_widgets['bid_var'][b_index] = tk.StringVar()
        self.body_widgets['bid'][b_index] = tk.Label(self._body_frame.sub_frame,
                                                     textvariable=self.body_widgets['bid_var'][b_index],
                                                     bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT, width=self._col_width)
        self.body_widgets['bid'][b_index].grid(row=b_index, column=2)

        self.body_widgets['ask_var'][b_index] = tk.StringVar()
        self.body_widgets['ask'][b_index] = tk.Label(self._body_frame.sub_frame,
                                                     textvariable=self.body_widgets['ask_var'][b_index],
                                                     bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT, width=self._col_width)
        self.body_widgets['ask'][b_index].grid(row=b_index, column=3)

        self.body_widgets['remove'][b_index] = tk.Button(self._body_frame.sub_frame, text="X",
                                                         bg="darkred", fg=FG_COLOR, font=GLOBAL_FONT,
                                                         command=lambda: self._remove_symbol(b_index), width=4)
        self.body_widgets['remove'][b_index].grid(row=b_index, column=4)

        self._body_index += 1

