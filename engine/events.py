import asyncio
from collections import defaultdict
from typing import Callable, Any

# Event Type Names
BAR = "bar"
SIGNAL = "signal"
ORDER_APPROVED = "order_approved"
ORDER_REJECTED = "order_rejected"
FILL =  "fill"
EQUITY_UPDATE = "equity_update"
AI_FEEDBACK = "ai_feedback"

class EventBus:
    def __init__(self) -> None:
        self.subscribers = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable) -> None:
        self.subscribers[event_type].append(handler)

    async def publish(self, event_type: str, payload: Any) -> None:
        for handler in self._subscribers[event_type]:
            result = handler(payload)
            if asyncio.iscoroutine(result):
                await result