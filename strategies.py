import logging
from typing import *
import time

import pandas as pd

from models import *

logger = logging.getLogger()

TF_EQUIV = {'1m': 60, '5m': 300, '15m': 900, '30m': 1800, '1h': 3600, '4h': 14400}


class Strategy():

    def __init__(self, client, contract: Contract, exchange: str, timeframe: str,
                 balance_pct: float, take_profit: float, stop_loss: float):
        self.client = client
        self.contract = contract
        self.exchange = exchange
        self.tf = timeframe
        self.tf_equiv = TF_EQUIV[timeframe] * 1000
        self.balance_pct = balance_pct
        self.take_profit = take_profit
        self.stop_loss = stop_loss

        self.open_position = False

        self.candles: List[Candle] = []

    def parse_trades(self, price: float, size: float, timestamp: int) -> str:

        timestamp_diff = int(time.time() * 1000) - timestamp
        if timestamp_diff >= 2000:
            logger.warning('%s %s: %s milliseconds of difference between the current time and the trade time',
                           self.exchange, self.contract.symbol, timestamp_diff)

        last_candle = self.candles[-1]

        # Same Candle

        if timestamp < last_candle.timestamp + self.tf_equiv:

            last_candle.close = price
            last_candle.volume += size

            if price > last_candle.high:
                last_candle.high = price

            elif price < last_candle.low:
                last_candle.low = price

            return 'same_candle'

        # Missing Candle(s)

        elif timestamp >= last_candle.timestamp + 2 * self.tf_equiv:

            missing_candles = int((timestamp - last_candle.timestamp) / self.tf_equiv) - 1

            logger.info('%s missing %s candles for %s %s (%s %s)', self.exchange, missing_candles, self.contract.symbol,
                        self.tf,
                        timestamp, last_candle.timestamp)

            for missing in range(missing_candles):
                new_ts = last_candle.timestamp + self.tf_equiv
                candle_info = {'ts': new_ts, 'open': last_candle.close, 'high': last_candle.close,
                               'low': last_candle.close,
                               'close': last_candle.close, 'volume': 0}
                new_candle = Candle(candle_info, self.tf, 'parse_trade')

                self.candles.append(new_candle)

                last_candle = new_candle

            new_ts = last_candle.timestamp + self.tf_equiv
            candle_info = {'ts': new_ts, 'open': price, 'high': price, 'low': price, 'close': price, 'volume': size}
            new_candle = Candle(candle_info, self.tf, 'parse_trade')

            self.candles.append(new_candle)

            return 'new_candle'

        # New Candle

        elif timestamp >= last_candle.timestamp + self.tf_equiv:

            new_ts = last_candle.timestamp + self.tf_equiv
            candle_info = {'ts': new_ts, 'open': price, 'high': price, 'low': price, 'close': price, 'volume': size}
            new_candle = Candle(candle_info, self.tf, 'parse_trade')

            self.candles.append(new_candle)

            logger.info('%s New candle for %s %s', self.exchange, self.contract.symbol, self.tf)

            return 'new_candle'

    def _open_position(self, signal_result: int):

        trade_size = self.client.get_trade_size(self.contract, self.candles[-1].close, self.balance_pct)
        if trade_size is None:
            return

class TechnicalStrategy(Strategy):

    def __init__(self, client, contract: Contract, exchange: str, timeframe: str,
                 balance_pct: float, take_profit: float, stop_loss: float,
                 other_params: Dict):
        super().__init__(client, contract, exchange, timeframe, balance_pct, take_profit, stop_loss)

        self._ema_fast = other_params['ema_fast']
        self._ema_slow = other_params['ema_slow']
        self._ema_signal = other_params['ema_signal']

        self._rsi_length = other_params['rsi_length']

    def _rsi(self):

        close_list = []
        for candle in self.candles:
            close_list.append(candle.close)

        closes = pd.Series(close_list)

        delta = closes.diff().dropna()

        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        avg_gain = up.ewm(com=(self._rsi_length-1), min_periods=self._rsi_length).mean()
        avg_loss = down.abs().ewm(com=(self._rsi_length - 1), min_periods=self._rsi_length).mean()

        rs = avg_gain / avg_loss

        rsi = 100 - 100 / (1 + rs)
        rsi = rsi.round(2)

        return rsi.iloc[-1]

    def _macd(self) -> Tuple[float, float]:

        close_list = []
        for candle in self.candles:
            close_list.append(candle.close)

        closes = pd.Series(close_list)

        ema_fast = closes.ewm(span=self._ema_fast).mean()
        ema_slow = closes.ewm(span=self._ema_slow).mean()

        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=self._ema_signal).mean()

        return macd_line.iloc[-2], macd_signal.iloc[-2]

    def _check_signal(self):

        macd_line, macd_signal = self._macd()
        rsi = self._rsi()

        print(rsi, macd_line, macd_signal)

        if rsi < 30 and macd_line > macd_signal:
            return 1
        elif rsi > 70 and macd_line < macd_signal:
            return -1
        else:
            return 0

    def check_trade(self, tick_type: str):

        if tick_type == 'new_candle' and not self.open_position:
            signal_result = self._check_signal()

            if signal_result in [-1, 1]:
                self._open_position(signal_result)

class BreakoutStrategy(Strategy):

    def __init__(self, client, contract: Contract, exchange: str, timeframe: str,
                 balance_pct: float, take_profit: float, stop_loss: float,
                 other_params: Dict):
        super().__init__(client, contract, exchange, timeframe, balance_pct, take_profit, stop_loss)

        self._min_volume = other_params['min_volume']

    def _check_signal(self) -> int:

        if self.candles[-1].close > self.candles[-2].high and self.candles[-1].volume > self._min_volume:
            return 1

        if self.candles[-1].close < self.candles[-2].low and self.candles[-1].volume > self._min_volume:
            return -1

        else:
            return 0

    def check_trade(self, tick_type: str):

        if not self.open_position:
            signal_result = self._check_signal()

            if signal_result in [-1, 1]:
                self._open_position(signal_result)