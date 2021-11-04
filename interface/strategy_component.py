import tkinter as tk
import typing
from interface.styling import *

class StrategyEditor(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._all_contracts = ['BTCUSDT', 'ETHUSDT']
        self._all_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h']

        self._headers = ['Strategy', 'Contract', 'Timeframe', 'Balance %', 'TP %', 'SL %']

        self._base_params = [
            {'code_name': 'strategy_type', 'widget': tk.OptionMenu,
             'data_type': str, 'values': ['Technical', 'Breakout'],
             'width': 10},
            {'code_name': 'contract', 'widget': tk.OptionMenu,
             'data_type': str, 'values': self._all_contracts,
             'width': 15},
            {'code_name': 'timeframe', 'widget': tk.OptionMenu,
             'data_type': str, 'values': self._all_timeframes,
             'width': 7},
            {'code_name': 'balance_pct', 'widget': tk.Entry,
             'data_type': float, 'width': 7},
            {'code_name': 'take_profit', 'widget': tk.Entry,
             'data_type': float, 'width': 7},
            {'code_name': 'stop_loss', 'widget': tk.Entry,
             'data_type': float, 'width': 7},
            {'code_name': 'parameters', 'widget': tk.Button,
             'data_type': float, 'text': 'Parameters',
             'bg': BG_COLOR_2, 'command': self._show_popup},
            {'code_name': 'activation', 'widget': tk.Button,
             'data_type': float, 'text': 'OFF',
             'bg': 'darkred', 'command': self._switch_strategy},
            {'code_name': 'delete', 'widget': tk.Button,
             'data_type': float, 'text': 'X',
             'bg': 'darkred', 'command': self._delete_row}
        ]

        self._commands_frame = tk.Frame(self, bg=BG_COLOR)
        self._commands_frame.pack(side=tk.TOP)

        self._table_frame = tk.Frame(self, bg=BG_COLOR)
        self._table_frame.pack(side=tk.TOP)

        self._add_button = tk.Button(self._commands_frame, text='Add strategy', font=GLOBAL_FONT,
                                     command=self._add_strategy_row, bg=BG_COLOR_2, fg=FG_COLOR)
        self._add_button.pack(side=tk.TOP)

        self.body_widgets = dict()

        for idx, h in enumerate(self._headers):
            header = tk.Label(self._table_frame, text=h, bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT)
            header.grid(row=0, column=idx)

        for h in self._base_params:
            self.body_widgets[h['code_name']] = dict()
            if h['code_name'] in ['strategy_type', 'contract', 'timeframe']:
                self.body_widgets[h['code_name'] + '_var'] = dict()

        self._body_index = 1

    def _add_strategy_row(self):
        b_index = self._body_index

        for col, base_params in enumerate(self._base_params):
            code_name = base_params['code_name']
            if base_params['widget'] == tk.OptionMenu:
                self.body_widgets[code_name + '_var'][b_index] = tk.StringVar()
                self.body_widgets[code_name][b_index] = tk.OptionMenu(self._table_frame,
                                                                      self.body_widgets[code_name + '_var'][b_index],
                                                                      *base_params['values'])
                self.body_widgets[code_name][b_index].config(width=base_params['width'])

            elif base_params['widget'] == tk.Entry:
                self.body_widgets[code_name][b_index] = tk.Entry(self._table_frame, justify=tk.CENTER)

            elif base_params['widget'] == tk.Button:
                self.body_widgets[code_name][b_index] = tk.Button(self._table_frame, text=base_params['text'], bg=base_params['bg'], fg=FG_COLOR,
                                                    command=lambda frozen_command=base_params['command']: frozen_command(b_index))

            else:
                continue

            self.body_widgets[code_name][b_index].grid(row=b_index, column=col)

        self._body_index += 1

    def _delete_row(self, b_index: int):

        for element in self._base_params:
            self.body_widgets[element['code_name']][b_index].grid_forget()

            del self.body_widgets[element['code_name']][b_index]

    def _show_popup(self, b_index: int):
        return

    def _switch_strategy(self, b_index: int):
        return

