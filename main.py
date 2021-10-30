import logging
import tkinter as tk
from connectors.binance_futures import BinanceFuturesClient

import os
from dotenv import load_dotenv

load_dotenv()

binance_public_key = os.getenv('BINANCE_PK')
binance_secret_key = os.getenv('BINANCE_SK')
bitmex_public_key = os.getenv('BITMEX_PK')
bitmex_secret_key = os.getenv('BITMEX_SK')
bitmex_test_key = os.getenv('BITMEX_TK')


logger = logging.getLogger()

logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s :: %(message)s")
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler('info.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

if __name__ == '__main__':

    binance = BinanceFuturesClient(binance_public_key, binance_secret_key, True)

    root = tk.Tk()
    root.mainloop()
