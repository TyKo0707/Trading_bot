import tkinter as tk
from interface.logging_component import Logging

from connectors.binance_futures import BinanceFuturesClient
from connectors.bitmex_futures import BitmexClient
from interface.styling import *
from interface.watchlist_component import WatchList


class Root(tk.Tk):

    def __init__(self, bitmex: BitmexClient, binance: BinanceFuturesClient):
        super().__init__()

        self.bitmex = bitmex
        self.binance = binance

        self.title('Trading Bot')

        self.configure(bg=BG_COLOR)

        self._left_frame = tk.Frame(self, bg=BG_COLOR)
        self._left_frame.pack(side=tk.LEFT)

        self._right_frame = tk.Frame(self, bg=BG_COLOR)
        self._right_frame.pack(side=tk.RIGHT)

        self._watchlist_frame = WatchList(self._left_frame, bg=BG_COLOR)
        self._watchlist_frame.pack(side=tk.TOP)

        self.logging_frame = Logging(self._left_frame, bg=BG_COLOR)
        self.logging_frame.pack(side=tk.TOP)

        self._update_ui()

    def _update_ui(self):

        for log in self.bitmex.logs:
            if not log['displayed']:
                self.logging_frame.add_log(log['log'])
                log['displayed'] = True

        for log in self.binance.logs:
            if not log['displayed']:
                self.logging_frame.add_log(log['log'])
                log['displayed'] = True

        self.after(1500, self._update_ui)
