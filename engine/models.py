from dataclasses import dataclass, field
from typing import Optional
import time

@dataclass
class Bar:
    symbol: str
    timestamp: float
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass
class Intent:
    symbol: str
    side: str # buy or sell
    timestamp: float = field(default_factory=time.time)
    strategy_id: str = "default"

@dataclass
class Order:
    symbol: str
    side: str
    quantity: float
    order_id: str
    timestamp: float = field(default_factory=time.time)

@dataclass
class Fill:
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    fee: float
    timestamp: float = field(default_factory=time.time)

@dataclass
class Position:
    symbol: str
    quantity: float
    avg_price: float
    unrealised_pnl: float = 0.0

@dataclass
class RiskDecision:
    approved: bool
    reason: str
    order: Optional[Order]= None
