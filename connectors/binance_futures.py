import hashlib
import hmac
import json
import logging
import threading
import time
import typing
from urllib.parse import urlencode

import requests
import websocket

from models import *
from strategies import TechnicalStrategy, BreakoutStrategy

logger = logging.getLogger()


class BinanceFuturesClient:

    def __init__(self, public_key: str, secret_key: str, testnet: bool):
        if testnet:
            self._base_url = 'https://testnet.binancefuture.com'
            self._wss_url = 'wss://stream.binancefuture.com/ws'
        else:
            self._base_url = 'https://fapi.binance.com'
            self._wss_url = 'wss://fstream.binancefuture.com/ws'

        self._public_key = public_key
        self._secret_key = secret_key

        self._headers = {'X-MBX-APIKEY': self._public_key}

        self.prices = dict()
        self.strategies: typing.Dict[int, typing.Union[TechnicalStrategy, BreakoutStrategy]] = dict()

        self.logs = []

        self._ws_id = 1

        self.contracts = self.get_contracts()
        self.balance = self.get_balances()

        t = threading.Thread(target=self._start_ws)
        t.start()

        logger.info("Binance Futures Client successfully initialized")

    def _add_log(self, msg: str):
        logger.info('%s', msg)
        self.logs.append({'log': msg, 'displayed': False})

    def _generate_signature(self, data: typing.Dict) -> str:

        return hmac.new(self._secret_key.encode(), urlencode(data).encode(), hashlib.sha256).hexdigest()

    def _make_request(self, method: str, endpoint: str, data: typing.Dict):

        if method == "GET":
            try:
                response = requests.get(self._base_url + endpoint, params=data, headers=self._headers)
            except Exception as e:
                logger.error('Connection error while making %s request to %s', method, endpoint, e)
                return None

        elif method == "POST":
            try:
                response = requests.post(self._base_url + endpoint, params=data, headers=self._headers)
            except Exception as e:
                logger.error('Connection error while making %s request to %s', method, endpoint, e)
                return None

        elif method == "DELETE":
            try:
                response = requests.delete(self._base_url + endpoint, params=data, headers=self._headers)
            except Exception as e:
                logger.error('Connection error while making %s request to %s', method, endpoint, e)
                return None

        else:
            raise ValueError()

        if response.status_code == 200:
            return response.json()

        else:
            logger.error("Error while making request to %s: %s (error code %s)",
                         method, endpoint, response.json())
            return None

    def get_contracts(self):

        exchange_info = self._make_request("GET", '/fapi/v1/exchangeInfo', dict())

        contracts = dict()

        if exchange_info is not None:
            for contract_data in exchange_info['symbols']:
                contracts[contract_data['symbol']] = Contract(contract_data, 'binance')

        return contracts

    def get_historical_candles(self, contracts: Contract, interval: str) -> typing.List[Candle]:

        data = dict()
        data['symbol'] = contracts.symbol
        data['interval'] = interval
        data['limit'] = 1000

        raw_candles = self._make_request('GET', '/fapi/v1/klines', data)

        candles = []

        if raw_candles is not None:
            for c in raw_candles:
                candles.append(Candle(c, interval, 'binance'))

        return candles

    def get_bid_ask(self, contracts: Contract) -> typing.Dict[str, float]:

        data = dict()
        data['symbol'] = contracts.symbol
        ob_data = self._make_request('GET', '/fapi/v1/ticker/bookTicker', data)

        if ob_data is not None:
            if contracts.symbol not in self.prices:
                self.prices[contracts.symbol] = {'bid': float(ob_data['bidPrice']),
                                                 'ask': float(ob_data['askPrice'])}
            else:
                self.prices[contracts.symbol]['bid'] = float(ob_data['bidPrice'])
                self.prices[contracts.symbol]['bid'] = float(ob_data['askPrice'])

            return self.prices[contracts.symbol]

    def get_balances(self) -> typing.Dict[str, Balance]:

        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self._generate_signature(data)

        balances = dict()

        account_data = self._make_request('GET', '/fapi/v1/account', data)

        if account_data is not None:
            for a in account_data['assets']:
                balances[a['asset']] = Balance(a, 'binance')

        return balances

    def place_order(self, contracts: Contract, side: str, quantity: float, order_type: str, price=None,
                    tif=None) -> OrderStatus:

        data = dict()
        data['symbol'] = contracts.symbol
        data['side'] = side
        data['quantity'] = round(quantity / contracts.lot_size) * contracts.lot_size
        data['type'] = order_type

        if price is not None:
            data['price'] = round(price / contracts.tick_size) * contracts.tick_size
        if tif is not None:
            data['timeInForce'] = tif

        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self._generate_signature(data)

        order_status = self._make_request('POST', '/fapi/v1/order', data)

        if order_status is not None:
            order_status = OrderStatus(order_status, 'binance')

        return order_status

    def cancel_order(self, contracts: Contract, order_id: int) -> OrderStatus:

        data = dict()
        data['orderID'] = order_id
        data['symbol'] = contracts.symbol

        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self._generate_signature(data)

        order_status = self._make_request('DELETE', '/fapi/v1/order', data)

        if order_status is not None:
            order_status = OrderStatus(order_status, 'binance')

        return order_status

    def get_order_status(self, contracts: Contract, order_id: int) -> OrderStatus:

        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['symbol'] = contracts.symbol
        data['orderID'] = order_id
        data['signature'] = self._generate_signature(data)

        order_status = self._make_request("GET", '/fapi/v1/order', data)

        if order_status is not None:
            order_status = OrderStatus(order_status, 'binance')

        return order_status

    def _start_ws(self):

        self.ws = websocket.WebSocketApp(self._wss_url, on_open=self._on_open, on_close=self._on_close,
                                         on_error=self._on_error, on_message=self._on_message)
        while True:
            try:
                self.ws.run_forever()
            except Exception as e:
                logger.error('Binance error in run_forever() method: %s', e)
            time.sleep(2)

    def _on_open(self, ws):

        logger.info('Binance connection is opened')
        self.subscribe_channel(list(self.contracts.values()), "bookTicker")

    def _on_close(self, ws):

        logger.warning('Binance Websocket connection is closed')

    def _on_error(self, ws, msg: str):

        logger.error('Binance connection error: %s', msg)

    def _on_message(self, ws, msg: str):

        data = json.loads(msg)

        if 'e' in data:
            if data['e'] == 'bookTicker':
                symbol = data['s']
                if data is not None:
                    if symbol not in self.prices:
                        self.prices[symbol] = {'bid': float(data['b']),
                                               'ask': float(data['a'])}
                    else:
                        self.prices[symbol]['bid'] = float(data['b'])
                        self.prices[symbol]['ask'] = float(data['a'])

            elif data['e'] == 'aggTrade':
                symbol = data['s']

                for key, strat in self.strategies.items():
                    if strat.contract.symbol == symbol:
                        strat.parse_trades(float(data['p']), float(data['q']), data['T'])

    def subscribe_channel(self, contracts: typing.List[Contract], channel: str):

        data = dict()
        data['method'] = 'SUBSCRIBE'
        data['params'] = []

        for contract in contracts:
            data['params'].append(contract.symbol.lower() + '@' + channel)

        data['id'] = self._ws_id

        try:
            self.ws.send(json.dumps(data))
        except Exception as e:
            logger.error('Websocket error while subscribing to %s %s updates: %s', len(contracts), channel, e)

        self._ws_id += 1
