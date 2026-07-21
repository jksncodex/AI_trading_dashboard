from engine.models import Fill, Position


class Portfolio:
    def __init__(self, starting_cash: float) -> None:
        self.cash = starting_cash
        self.positions = {}
        self.realised_pnl = 0.0
        self.last_price = {}

    def apply_fill(self, fill: Fill) -> None:
        self.cash -= fill.fee

        if fill.side == "buy":
            cost = fill.price * fill.quantity
            self.cash -= cost
            if fill.symbol in self.positions:
                pos = self.positions[fill.symbol]
                total_qty = pos.quantity + fill.quantity
                total_cost = pos.avg_price * pos.quantity + cost
                pos.avg_price = total_cost / total_qty
                pos.quantity = total_qty
            else:
                self.positions[fill.symbol] = Position(
                    symbol=fill.symbol,
                    quantity=fill.quantity,
                    avg_price=fill.price,
                )
        else:
            proceeds = fill.price * fill.quantity
            self.cash += proceeds
            if fill.symbol in self.positions:
                pos = self.positions[fill.symbol]
                cost_basis = pos.avg_price * fill.quantity
                self.realised_pnl += proceeds - cost_basis
                pos.quantity -= fill.quantity
                if pos.quantity <= 0:
                    del self.positions[fill.symbol]

    def mark_price(self, symbol: str, price: float) -> None:
        self.last_price[symbol] = price
        if symbol in self.positions:
            pos = self.positions[symbol]
            pos.unrealised_pnl = (price - pos.avg_price) * pos.quantity

    def equity(self) -> float:
        holdings_value = sum(
            self.last_price.get(sym, pos.avg_price) * pos.quantity
            for sym, pos in self.positions.items()
        )
        return self.cash + holdings_value