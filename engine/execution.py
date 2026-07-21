from engine.models import Order, Fill


class ExecutionAdapter:
    async def submit(self, order: Order, price: float) -> Fill:
        raise NotImplementedError



class PaperAdapter (ExecutionAdapter):
    def __init__(self, fee_pct: float, slippage_pct: float) -> None:
        self.fee_pct = fee_pct
        self.slippage_pct = slippage_pct
        self.processed_ids = set()


    async def submit(self, order: Order, price: float) -> Fill:
        if order.order_id in self.processed_ids:
            raise ValueError(f"duplicated order: {order.order_id}")
        self.processed_ids.add(order.order_id)

        if order.side == "buy":
            fill_price = price * (1 + self.slippage_pct)
        else:
            fill_price = price * (1 - self.slippage_pct)

        fee = fill_price * order.quantity * self.fee_pct

        return Fill(
            order_id=order.order_id,
            symbol = order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=fill_price,
            fee=fee,
        )

class LiveAdapterStub(ExecutionAdapter):
    async def submit(self, order: Order, price: float) -> Fill:
        raise NotImplementedError(
            "Live trading is not implemented. Paper mode only in Phase 1."
        )
