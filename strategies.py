import logging
from typing import *

from models import *

logger = logging.getLogger()


class Strategy():
    def __init__(self, contract: Contract, exchange: str, timeframe: str,
                 balance_pct: float, take_profit: float, stop_loss: float):
        self.contract = contract
        self.exchange = exchange
        self.timeframe = timeframe
        self.balance_pct = balance_pct
        self.take_profit = take_profit
        self.stop_loss = stop_loss

        self.candles: List[Candle] = []


class TechnicalStrategy(Strategy):

    def __init__(self, contract: Contract, exchange: str, timeframe: str,
                 balance_pct: float, take_profit: float, stop_loss: float,
                 other_params: Dict):
        super().__init__(contract, exchange, timeframe, balance_pct, take_profit, stop_loss)

        self._ema_fast = other_params['ema_fast']
        self._ema_slow = other_params['ema_slow']
        self._ema_signal = other_params['ema_signal']


class BreakoutStrategy(Strategy):

    def __init__(self, contract: Contract, exchange: str, timeframe: str,
                 balance_pct: float, take_profit: float, stop_loss: float,
                 other_params: Dict):
        super().__init__(contract, exchange, timeframe, balance_pct, take_profit, stop_loss)

        self._min_volume = other_params['min_volume']
