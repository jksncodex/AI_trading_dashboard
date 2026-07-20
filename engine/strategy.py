from collections import deque

from engine.events import EventBus, BAR, SIGNAL
from engine.models import Bar, Intent

class Strategy:
    def __init__(self, bus: EventBus, symbol: str) -> None:
        self.bus = bus
        self.symbol = symbol
        self.paused = False
        bus.subscribe (BAR, self.on_bar)

    def pause(self) -> None:
        self.paused = True

    def resume(self) -> None:
        self.paused = False

    async def on_bar(self, bar: Bar) -> None:
        raise NotImplementedError

class MACrossoverStrategy(Strategy):
    def __init__(self, bus: EventBus, symbol: str,
                 fast_period: int, slow_period: int) -> None:
        super().__init__(bus, symbol)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.closes = deque(maxlen=slow_period)
        self.prev_fast = None
        self.prev_slow = None

    async def on_bar(self, bar: Bar) -> None:
        if self.paused:
            return
        self.closes.append(bar.close)
        if len(self.closes) < self.slow_period:
            return

        fast =sum(list(self.closes)[-self.fast_period:]) / self.fast_period
        slow = sum(self.closes) / self.slow_period

        if self.prev_fast is not None:
            crossed_up = self.prev_fast <= self.prev_slow and fast > slow
            crossed_down = self.prev_fast >= self.prev_slow and fast < slow
            if crossed_up:
                await self.bus.publish (SIGNAL, Intent(self.symbol, "buy"))
            elif crossed_down:
                await self.bus.publish(SIGNAL, Intent(self.symbol, "sell"))

        self.prev_fast = fast
        self.prev_slow = slow



