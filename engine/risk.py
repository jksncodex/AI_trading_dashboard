import uuid

from engine.models import Intent, Order, RiskDecision, Position


class RiskGate:
    def __init__(self, starting_cash: float, risk_fraction: float,
                 max_position_value: float, max_open_positions: int,
                 daily_loss_limit_pct: float) -> None:
        self.risk_fraction = risk_fraction
        self.max_position_value = max_position_value
        self.max_open_positions = max_open_positions
        self.daily_loss_limit = starting_cash * daily_loss_limit_pct
        self.kill_switch = False
        self.daily_loss = 0.0

    def evaluate(self, intent: Intent, price: float,
                 positions: dict, cash: float) -> RiskDecision:
        is_closing = intent.side == "sell" and intent.symbol in positions

        if not is_closing:
            if self.kill_switch:
                return RiskDecision(False, "kill switch engaged")
            if self.daily_loss >= self.daily_loss_limit:
                return RiskDecision(False, "daily loss limit reached")
            if len(positions) >= self.max_open_positions and \
                    intent.symbol not in positions:
                return RiskDecision(False, "max open positions reached")

        if is_closing:
            quantity = positions[intent.symbol].quantity
        else:
            cash_to_risk = cash * self.risk_fraction
            capped = min(cash_to_risk, self.max_position_value)
            quantity = capped / price
            if quantity <= 0:
                return RiskDecision(False, "insufficient cash")

        order = Order(
            symbol=intent.symbol,
            side=intent.side,
            quantity=quantity,
            order_id=str(uuid.uuid4()),
        )
        return RiskDecision(True, "approved", order)