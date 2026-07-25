from sqlalchemy import text
from sqlalchemy.engine import Engine

from engine.models import Intent, Order, Fill


class Repository:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def save_signal(self, intent: Intent) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO signals (timestamp, symbol, side) "
                    "VALUES (:timestamp, :symbol, :side)"
                ),
                {
                    "timestamp": intent.timestamp,
                    "symbol": intent.symbol,
                    "side": intent.side,
                },
            )

    def save_order(self, order: Order) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO orders (order_id, timestamp, symbol, side, quantity) "
                    "VALUES (:order_id, :timestamp, :symbol, :side, :quantity)"
                ),
                {
                    "order_id": order.order_id,
                    "timestamp": order.timestamp,
                    "symbol": order.symbol,
                    "side": order.side,
                    "quantity": order.quantity,
                },
            )

    def save_fill(self, fill: Fill) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO fills "
                    "(order_id, timestamp, symbol, side, quantity, price, fee) "
                    "VALUES (:order_id, :timestamp, :symbol, :side, "
                    ":quantity, :price, :fee)"
                ),
                {
                    "order_id": fill.order_id,
                    "timestamp": fill.timestamp,
                    "symbol": fill.symbol,
                    "side": fill.side,
                    "quantity": fill.quantity,
                    "price": fill.price,
                    "fee": fill.fee,
                },
            )

    def save_equity(self, timestamp: float, value: float) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                text("INSERT INTO equity (timestamp, value) "
                     "VALUES (:timestamp, :value)"),
                {"timestamp": timestamp, "value": value},
            )

    def save_ai_log(self, timestamp: float, message: str) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                text("INSERT INTO ai_logs (timestamp, message) "
                     "VALUES (:timestamp, :message)"),
                {"timestamp": timestamp, "message": message},
            )

    def recent_fills(self, limit: int = 50) -> list:
        with self.engine.begin() as conn:
            rows = conn.execute(
                text(
                    "SELECT order_id, timestamp, symbol, side, quantity, price, fee "
                    "FROM fills ORDER BY timestamp DESC LIMIT :limit"
                ),
                {"limit": limit},
            )
            return [dict(row._mapping) for row in rows]

    def recent_signals(self, limit: int = 50) -> list:
        with self.engine.begin() as conn:
            rows = conn.execute(
                text(
                    "SELECT timestamp, symbol, side "
                    "FROM signals ORDER BY timestamp DESC LIMIT :limit"
                ),
                {"limit": limit},
            )
            return [dict(row._mapping) for row in rows]

    def equity_curve(self, limit: int = 500) -> list:
        with self.engine.begin() as conn:
            rows = conn.execute(
                text(
                    "SELECT timestamp, value FROM equity "
                    "ORDER BY timestamp ASC LIMIT :limit"
                ),
                {"limit": limit},
            )
            return [dict(row._mapping) for row in rows]

    def recent_ai_logs(self, limit: int = 20) -> list:
        with self.engine.begin() as conn:
            rows = conn.execute(
                text(
                    "SELECT timestamp, message FROM ai_logs "
                    "ORDER BY timestamp DESC LIMIT :limit"
                ),
                {"limit": limit},
            )
            return [dict(row._mapping) for row in rows]