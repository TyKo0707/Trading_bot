import tkinter as tk
import typing

import json

from interface.styling import *
from interface.scrollable_frame import ScrollableFrame

from connectors.binance_futures import BinanceClient
from connectors.bitmex_futures import BitmexClient

from strategies import TechnicalStrategy, BreakoutStrategy
from utils import *

from database import WorkspaceData


if typing.TYPE_CHECKING:
    from interface.root_component import Root


class StrategyEditor(tk.Frame):
    def __init__(self, root: "Root", binance: BinanceClient, bitmex: BitmexClient, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root = root

        self.db = WorkspaceData()

        self._valid_integer = self.register(check_integer_format)
        self._valid_float = self.register(check_float_format)

        self._exchanges = {"Binance": binance, "Bitmex": bitmex}

        self._all_contracts = []
        self._all_timeframes = ["1m", "5m", "15m", "30m", "1h", "4h"]

        for exchange, client in self._exchanges.items():
            for symbol, contract in client.contracts.items():
                # If you want less symbols in the list, filter here (there are a lot of pairs on Binance Spot)
                self._all_contracts.append(symbol + "_" + exchange.capitalize())

        self._commands_frame = tk.Frame(self, bg=BG_COLOR)
        self._commands_frame.pack(side=tk.TOP)

        self._table_frame = tk.Frame(self, bg=BG_COLOR)
        self._table_frame.pack(side=tk.TOP)

        self._add_button = tk.Button(self._commands_frame, text="Add strategy", font=GLOBAL_FONT,
                                     command=self._add_strategy_row, bg=BG_COLOR_2, fg=FG_COLOR)
        self._add_button.pack(side=tk.TOP)

        self.body_widgets = dict()

        self._headers_frame = tk.Frame(self._table_frame, bg=BG_COLOR)

        self.additional_parameters = dict()
        self._extra_input = dict()

        # Defines the widgets displayed on each row and some characteristics of these widgets like their width
        # This lets the program create the widgets dynamically and it takes less space in the code
        # The width may need to be adjusted depending on your screen size and resolution
        self._base_params = [
            {"code_name": "strategy_type", "widget": tk.OptionMenu, "data_type": str,
             "values": ["Technical", "Breakout"], "width": 10, "header": "Strategy"},
            {"code_name": "contract", "widget": tk.OptionMenu, "data_type": str, "values": self._all_contracts,
             "width": 15, "header": "Contract"},
            {"code_name": "timeframe", "widget": tk.OptionMenu, "data_type": str, "values": self._all_timeframes,
             "width": 10, "header": "Timeframe"},
            {"code_name": "balance_pct", "widget": tk.Entry, "data_type": float, "width": 10, "header": "Balance %"},
            {"code_name": "take_profit", "widget": tk.Entry, "data_type": float, "width": 7, "header": "TP %"},
            {"code_name": "stop_loss", "widget": tk.Entry, "data_type": float, "width": 7, "header": "SL %"},
            {"code_name": "parameters", "widget": tk.Button, "data_type": float, "text": "Parameters",
             "bg": BG_COLOR_2, "command": self._show_popup, "header": "", "width": 10},
            {"code_name": "activation", "widget": tk.Button, "data_type": float, "text": "OFF",
             "bg": "darkred", "command": self._switch_strategy, "header": "", "width" : 8},
            {"code_name": "delete", "widget": tk.Button, "data_type": float, "text": "X",
             "bg": "darkred", "command": self._delete_row, "header": "", "width": 6},

        ]

        self.extra_params = {
            "Technical": [
                {"code_name": "rsi_length", "name": "RSI Periods", "widget": tk.Entry, "data_type": int},
                {"code_name": "ema_fast", "name": "MACD Fast Length", "widget": tk.Entry, "data_type": int},
                {"code_name": "ema_slow", "name": "MACD Slow Length", "widget": tk.Entry, "data_type": int},
                {"code_name": "ema_signal", "name": "MACD Signal Length", "widget": tk.Entry, "data_type": int},
            ],
            "Breakout": [
                {"code_name": "min_volume", "name": "Minimum Volume", "widget": tk.Entry, "data_type": float},
            ]
        }

        for idx, h in enumerate(self._base_params):
            header = tk.Label(self._headers_frame, text=h['header'], bg=BG_COLOR, fg=FG_COLOR, font=GLOBAL_FONT,
                              width=h['width'], bd=1, relief=tk.FLAT)
            header.grid(row=0, column=idx, padx=2)

        header = tk.Label(self._headers_frame, text="", bg=BG_COLOR, fg=FG_COLOR, font=GLOBAL_FONT,
                          width=8, bd=1, relief=tk.FLAT)
        header.grid(row=0, column=len(self._base_params), padx=2)

        self._headers_frame.pack(side=tk.TOP, anchor="nw")

        self._body_frame = ScrollableFrame(self._table_frame, bg=BG_COLOR, height=250)
        self._body_frame.pack(side=tk.TOP, fill=tk.X, anchor="nw")

        for h in self._base_params:
            self.body_widgets[h['code_name']] = dict()
            if h['code_name'] in ["strategy_type", "contract", "timeframe"]:
                self.body_widgets[h['code_name'] + "_var"] = dict()

        self._body_index = 0

        self._load_workspace()

    def _add_strategy_row(self):

        """
        Add a new row with widgets defined in the self._base_params list.
        Aligning these widgets with the headers (that are in another frame) can be tricky.
        List of arguments having an influence on the widgets width: bd, indicatoron, width, font, highlightthickness
        This is because the widgets are of different types (the headers are Labels and the body widgets can be Buttons...
        Mac OSX/Windows also has an influence on the widget style and thus width.
        :return:
        """

        b_index = self._body_index

        for col, base_param in enumerate(self._base_params):
            code_name = base_param['code_name']
            if base_param['widget'] == tk.OptionMenu:
                self.body_widgets[code_name + "_var"][b_index] = tk.StringVar()
                self.body_widgets[code_name + "_var"][b_index].set(base_param['values'][0])
                self.body_widgets[code_name][b_index] = tk.OptionMenu(self._body_frame.sub_frame,
                                                                      self.body_widgets[code_name + "_var"][b_index],
                                                                      *base_param['values'])
                self.body_widgets[code_name][b_index].config(width=base_param['width'], bd=0, indicatoron=0)

            elif base_param['widget'] == tk.Entry:
                self.body_widgets[code_name][b_index] = tk.Entry(self._body_frame.sub_frame, justify=tk.CENTER,
                                                                 bg=BG_COLOR_2, fg=FG_COLOR,
                                                                 font=GLOBAL_FONT, bd=1, width=base_param['width'])

                if base_param['data_type'] == int:
                    self.body_widgets[code_name][b_index].config(validate='key', validatecommand=(self._valid_integer, "%P"))
                elif base_param['data_type'] == float:
                    self.body_widgets[code_name][b_index].config(validate='key', validatecommand=(self._valid_float, "%P"))

            elif base_param['widget'] == tk.Button:
                self.body_widgets[code_name][b_index] = tk.Button(self._body_frame.sub_frame, text=base_param['text'],
                                        bg=base_param['bg'], fg=FG_COLOR, font=GLOBAL_FONT, width=base_param['width'],
                                        command=lambda frozen_command=base_param['command']: frozen_command(b_index))
            else:
                continue

            self.body_widgets[code_name][b_index].grid(row=b_index, column=col, padx=2)

        self.additional_parameters[b_index] = dict()

        for strat, params in self.extra_params.items():
            for param in params:
                self.additional_parameters[b_index][param['code_name']] = None

        self._body_index += 1

    def _delete_row(self, b_index: int):

        """
        Triggered when the user clicks the X button.
        The row below the one deleted will automatically adjust and take its place, independently of its b_index.
        :param b_index:
        :return:
        """

        for element in self._base_params:
            self.body_widgets[element['code_name']][b_index].grid_forget()

            del self.body_widgets[element['code_name']][b_index]

    def _show_popup(self, b_index: int):

        """
        Display a popup window with additional parameters that are specific to the strategy selected.
        This avoids overloading the strategy component with too many tk.Entry boxes.
        :param b_index:
        :return:
        """

        x = self.body_widgets["parameters"][b_index].winfo_rootx()
        y = self.body_widgets["parameters"][b_index].winfo_rooty()

        self._popup_window = tk.Toplevel(self)
        self._popup_window.wm_title("Parameters")

        self._popup_window.config(bg=BG_COLOR)
        self._popup_window.attributes("-topmost", "true")
        self._popup_window.grab_set()

        self._popup_window.geometry(f"+{x - 80}+{y + 30}")

        strat_selected = self.body_widgets['strategy_type_var'][b_index].get()

        row_nb = 0

        for param in self.extra_params[strat_selected]:
            code_name = param['code_name']

            temp_label = tk.Label(self._popup_window, bg=BG_COLOR, fg=FG_COLOR, text=param['name'], font=BOLD_FONT)
            temp_label.grid(row=row_nb, column=0)

            if param['widget'] == tk.Entry:
                self._extra_input[code_name] = tk.Entry(self._popup_window, bg=BG_COLOR_2, justify=tk.CENTER, fg=FG_COLOR,
                                                        insertbackground=FG_COLOR, highlightthickness=False)

                # Sets the data validation function based on the data_type chosen
                if param['data_type'] == int:
                    self._extra_input[code_name].config(validate='key', validatecommand=(self._valid_integer, "%P"))
                elif param['data_type'] == float:
                    self._extra_input[code_name].config(validate='key', validatecommand=(self._valid_float, "%P"))

                if self.additional_parameters[b_index][code_name] is not None:
                    self._extra_input[code_name].insert(tk.END, str(self.additional_parameters[b_index][code_name]))
            else:
                continue

            self._extra_input[code_name].grid(row=row_nb, column=1)

            row_nb += 1

        # Validation Button

        validation_button = tk.Button(self._popup_window, text="Validate", bg=BG_COLOR_2, fg=FG_COLOR,
                                      command=lambda: self._validate_parameters(b_index))
        validation_button.grid(row=row_nb, column=0, columnspan=2)

    def _validate_parameters(self, b_index: int):

        """
        Record the parameters set in the popup window and close it.
        :param b_index:
        :return:
        """

        strat_selected = self.body_widgets['strategy_type_var'][b_index].get()

        for param in self.extra_params[strat_selected]:
            code_name = param['code_name']

            if self._extra_input[code_name].get() == "":
                self.additional_parameters[b_index][code_name] = None
            else:
                self.additional_parameters[b_index][code_name] = param['data_type'](self._extra_input[code_name].get())

        self._popup_window.destroy()

    def _switch_strategy(self, b_index: int):

        """
        Triggered when the user presses the ON/OFF button.
        Collects initial historical data (hence why there is a small delay on the interface after you click).
        :param b_index:
        :return:
        """

        for param in ["balance_pct", "take_profit", "stop_loss"]:
            if self.body_widgets[param][b_index].get() == "":
                self.root.logging_frame.add_log(f"Missing {param} parameter")
                return

        strat_selected = self.body_widgets['strategy_type_var'][b_index].get()

        for param in self.extra_params[strat_selected]:
            if self.additional_parameters[b_index][param['code_name']] is None:
                self.root.logging_frame.add_log(f"Missing {param['code_name']} parameter")
                return

        symbol = self.body_widgets['contract_var'][b_index].get().split("_")[0]
        timeframe = self.body_widgets['timeframe_var'][b_index].get()
        exchange = self.body_widgets['contract_var'][b_index].get().split("_")[1]

        contract = self._exchanges[exchange].contracts[symbol]

        balance_pct = float(self.body_widgets['balance_pct'][b_index].get())
        take_profit = float(self.body_widgets['take_profit'][b_index].get())
        stop_loss = float(self.body_widgets['stop_loss'][b_index].get())

        if self.body_widgets['activation'][b_index].cget("text") == "OFF":

            if strat_selected == "Technical":
                new_strategy = TechnicalStrategy(self._exchanges[exchange], contract, exchange, timeframe, balance_pct,
                                                 take_profit, stop_loss, self.additional_parameters[b_index])
            elif strat_selected == "Breakout":
                new_strategy = BreakoutStrategy(self._exchanges[exchange], contract, exchange, timeframe, balance_pct,
                                                take_profit, stop_loss, self.additional_parameters[b_index])
            else:
                return

            # Collects historical data. It is just one API call so that is ok, but be careful not to call methods
            # that would lock the UI for too long.
            # For example don't make a query to a database containing billions of rows, your interface would freeze.
            new_strategy.candles = self._exchanges[exchange].get_historical_candles(contract, timeframe)

            if len(new_strategy.candles) == 0:
                self.root.logging_frame.add_log(f"No historical data retrieved for {contract.symbol}")
                return

            if exchange == "Binance":
                self._exchanges[exchange].subscribe_channel([contract], "aggTrade")
                self._exchanges[exchange].subscribe_channel([contract], "bookTicker")

            self._exchanges[exchange].strategies[b_index] = new_strategy

            for param in self._base_params:
                code_name = param['code_name']

                if code_name != "activation" and "_var" not in code_name:
                    self.body_widgets[code_name][b_index].config(state=tk.DISABLED)  # Locks the widgets of this row

            self.body_widgets['activation'][b_index].config(bg="darkgreen", text="ON")
            self.root.logging_frame.add_log(f"{strat_selected} strategy on {symbol} / {timeframe} started")

        else:
            del self._exchanges[exchange].strategies[b_index]

            for param in self._base_params:
                code_name = param['code_name']

                if code_name != "activation" and "_var" not in code_name:
                    self.body_widgets[code_name][b_index].config(state=tk.NORMAL)

            self.body_widgets['activation'][b_index].config(bg="darkred", text="OFF")
            self.root.logging_frame.add_log(f"{strat_selected} strategy on {symbol} / {timeframe} stopped")

    def _load_workspace(self):

        """
        Add the rows and fill them with data saved in the database
        :return:
        """

        data = self.db.get("strategies")

        for row in data:
            self._add_strategy_row()

            b_index = self._body_index - 1  # -1 to select the row that was just added

            for base_param in self._base_params:
                code_name = base_param['code_name']

                if base_param['widget'] == tk.OptionMenu and row[code_name] is not None:
                    self.body_widgets[code_name + "_var"][b_index].set(row[code_name])
                elif base_param['widget'] == tk.Entry and row[code_name] is not None:
                    self.body_widgets[code_name][b_index].insert(tk.END, row[code_name])

            extra_params = json.loads(row['extra_params'])

            for param, value in extra_params.items():
                if value is not None:
                    self.additional_parameters[b_index][param] = value



