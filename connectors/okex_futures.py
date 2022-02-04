import asyncio


class OkexClient:
    def __init__(self, public_key: str, secret_key: str, testnet: bool, futures: bool):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.futures = futures

        if self.futures:
            self.platform = "okex_futures"
            self._base_url = "https://fapi.binance.com"
            self._wss_url = "wss://fstream.binance.com/ws"
        else:
            self.platform = "okex_spot"
            self._base_url = "https://api.binance.com"
            self._wss_url = "wss://stream.binance.com:9443/ws"
