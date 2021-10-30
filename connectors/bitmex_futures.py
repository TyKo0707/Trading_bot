import hashlib
import hmac
import json
import logging
import threading
import time
from urllib.parse import urlencode
import typing
import requests
import websocket

from models import *

class BitmexClient():

    def __init__(self, public_key: str, secret_key: str, testnet: bool):
        if testnet:
            self._base_url = 'https://testnet.bitmex.com'
            self._wss_url = 'wss://testnet.bitmex.com/realtime'
        else:
            self._base_url = 'https://www.bitmex.com'
            self._wss_url = 'wss://www.bitmex.com/realtime'

        self._public_key = public_key
        self._secret_key = secret_key

        self._headers = {'X-MBX-APIKEY': self._public_key}

        self.prices = dict()

        self._ws_id = 1
        self._ws = None

        self.contracts = self.get_contracts()
        self.balance = self.get_balances()

        logger.info('Binance Futures Client successfully initialized')

        t = threading.Thread(target=self._start_ws())
        t.start()

