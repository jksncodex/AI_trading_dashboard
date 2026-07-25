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

async def on_bar(self, bar) -> None:
    self.portfolio.mark_price(bar.symbol, bar.close)
    await self.bus.publish(EQUITY_UPDATE, self.portfolio.equity())

async def on_signal(self, intent: Intent) -> None:
    price = self.portfolio.last_price.get(intent.symbol)
    if price is None:
        return

    decision = self.risk.evaluate(
        intent, price, self.portfolio.positions, self.portfolio.cash
    )

    if not decision.approved:
        await self.bus.publish(ORDER_REJECTED, decision.reason)
        return

    fill = await self.execution.submit(decision.order, price)
    equity_before  = self.portfolio.equity()
    self.portfolio.apply_fill(fill)
    equity_after = self.portfolio.equity()

    loss = equity_before - equity_after
    if loss > 0:
        self.risk.daily.loss += loss

    await self.bus.publish(ORDER_APPROVED, decision.order)
    await self.bus.publish(FILL, fill)

async def start(self) -> None:
    await self.feed.run()

def engage_kill_switch(self) -> None:
    self.risk.kill_switch = True

def release_kill_switch(self) -> None:
    self.risk.kill_switch = False

def pause_strategy(self) -> None:
    self.strategy.pause()

def resume_strategy(self)-> None:
    self.strategy.resume()

async def flatten_all(self) -> None:
    for symbol in list(self.portfolio.positions.keys()):
        price = self.portfolio.last_price.get(symbol)
        if price is None:
            continue
        intent = Intent(symbol, "sell")
        decision = self.risk.evaluate(
            intent, price, self.portfolio.positions, self.portfolio.cash
        )
        if decision.approved:
            fill = await self.execution.submit(decision.order, price)
            self.portfolio.apply_fill(fill)
            await self.bus.publish(FILL, fill)
