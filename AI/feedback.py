import time

from engine.events import EventBus, FILL, AI_FEEDBACK
from persistence.repository import Repository


class AIFeedback:
    def __init__(self, bus: EventBus, repo: Repository) -> None:
        self.bus = bus
        self.repo = repo
        bus.subscribe(FILL, self.on_fill)

    async def on_fill(self, fill) -> None:
        fills = self.repo.recent_fills(limit=200)
        buys = [f for f in fills if f["side"] == "buy"]
        sells = [f for f in fills if f["side"] == "sell"]

        message = (
            f"Trades so far: {len(fills)} fills "
            f"({len(buys)} buys, {len(sells)} sells). "
            f"Latest: {fill.side} {fill.quantity:.6f} {fill.symbol} "
            f"at {fill.price:.2f}, fee {fill.fee:.2f}."
        )

        timestamp = time.time()
        self.repo.save_ai_log(timestamp, message)
        await self.bus.publish(
            AI_FEEDBACK, {"timestamp": timestamp, "message": message}
        )