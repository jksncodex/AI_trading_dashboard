from engine.events import (
    EventBus, BAR, SIGNAL, FILL,
    ORDER_APPROVED, ORDER_REJECTED, EQUITY_UPDATE,
)
from engine.models import Intent, Fill
from engine.market_data import SyntheticFeed, CCXTFeed
from engine.strategy import MACrossoverStrategy
from engine.risk import RiskGate
from engine.execution import PaperAdapter, LiveAdapterStub
from engine.portfolio import Portfolio
from config import Config


class Orchestrator:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.bus = EventBus()
        self.portfolio = Portfolio(config.risk.starting_cash)
        self.risk = RiskGate(
            starting_cash=config.risk.starting_cash,
            risk_fraction=config.risk.risk_fraction,
            max_position_value=config.risk.max_position_value,
            max_open_positions=config.risk.max_open_positions,
            daily_loss_limit_pct=config.risk.daily_loss_limit_pct,
        )

        if config.execution.mode == "live":
            self.execution = LiveAdapterStub()
        else:
            self.execution = PaperAdapter(
                fee_pct=config.execution.fee_pct,
                slippage_pct=config.execution.slippage_pct,
            )

        self.strategy = MACrossoverStrategy(
            self.bus, config.symbol,
            config.strategy.fast_period,
            config.strategy.slow_period,
        )

        if config.data.source == "ccxt":
            self.feed = CCXTFeed(
                self.bus, config.symbol,
                config.timeframe, config.data.ccxt_exchange,
            )
        else:
            self.feed = SyntheticFeed(
                self.bus, config.symbol,
                config.data.synthetic_interval_seconds,
                config.data.synthetic_start_price,
                config.data.synthetic_seed,
            )

        self.bus.subscribe(BAR, self.on_bar)
        self.bus.subscribe(SIGNAL, self.on_signal)