import asyncio
import random
import time

from engine.events import EventBus, BAR
from engine.models import Bar


class SyntheticFeed:
    def __init__(self, bus: EventBus, symbol: str, interval: float,
                 start_price: float, seed: int) -> None:
        self.bus = bus
        self.symbol = symbol
        self.interval = interval
        self.price = start_price
        self.rng = random.Random(seed)
        self.running = False

    async def run(self) -> None:
        self.running = True
        while self.running:
            bar = self._next_bar()
            await self.bus.publish(BAR, bar)
            await asyncio.sleep(self.interval)

    def stop(self) -> None:
        self.running = False

    def _next_bar(self) -> Bar:
        open_price = self.price
        change_pct = self.rng.gauss(0, 0.002)
        close_price = open_price * (1 + change_pct)
        high = max(open_price, close_price) * (1 + abs(self.rng.gauss(0, 0.0005)))
        low = min(open_price, close_price) * (1 - abs(self.rng.gauss(0, 0.0005)))
        volume = abs(self.rng.gauss(10, 3))
        self.price = close_price
        return Bar(
            symbol=self.symbol,
            timestamp=time.time(),
            open=open_price,
            high=high,
            low=low,
            close=close_price,
            volume=volume,
        )

class CCXTFeed:
    def __init__(self, bus: EventBus, symbol: str, timeframe: str,
                 exchange_name: str) -> None:
        import ccxt.async_support as ccxt
        self.bus = bus
        self.symbol = symbol
        self.timeframe = timeframe
        self.exchange = getattr(ccxt, exchange_name)()
        self.running = False
        self.last_timestamp = 0

    async def run(self) -> None:
        self.running = True
        try:
            while self.running:
                bars = await self.exchange.fetch_ohlcv(
                    self.symbol, self.timeframe, limit=2
                )
                closed_bar = bars[-2]
                if closed_bar[0] > self.last_timestamp:
                    self.last_timestamp = closed_bar[0]
                    bar = Bar(
                        symbol=self.symbol,
                        timestamp=closed_bar[0] / 1000,
                        open=closed_bar[1],
                        high=closed_bar[2],
                        low=closed_bar[3],
                        close=closed_bar[4],
                        volume=closed_bar[5],
                    )
                    await self.bus.publish(BAR, bar)
                await asyncio.sleep(5)
        finally:
            await self.exchange.close()

    def stop(self) -> None:
        self.running = False