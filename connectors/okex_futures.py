import asyncio


class OkexClient:
    def __init__(self, public_key: str, secret_key: str, testnet: bool, futures: bool):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.futures = futures
