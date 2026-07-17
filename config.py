from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv

@dataclass
class DataConfig:
    source:str
    ccxt_exchange: str
    synthetic_interval_seconds: float
    synthetic_start_price: float
    synthetic_seed: int

@dataclass
class StrategyConfig:
    name: str
    fast_period: int
    slow_period: int

@dataclass
class RiskConfig:
    starting_cash: float
    risk_fraction: float
    max_position_value: float
    max_open_positions: int
    daily_loss_limit_pct: float

@dataclass
class ExecutionConfig:
    mode: str
    fee_pct: float
    slippage_pct: float

@dataclass
class ServerConfig:
    host: str
    port: int

@dataclass
class DatabaseConfig:
    path: str

@dataclass
class Config:
    symbol: str
    timeframe: str
    data: DataConfig
    strategy: StrategyConfig
    risk: RiskConfig
    execution: ExecutionConfig
    server: ServerConfig
    database: DatabaseConfig

def load_config(path: str = "config.yaml") -> Config:
    load_dotenv()
    raw = yaml.safe_load(Path(path).read_text())
    return Config(
        symbol = raw["symbol"],
        timeframe = raw["timeframe"],
        data = DataConfig(**raw["data"]),
        strategy=StrategyConfig(**raw["strategy"]),
        risk = RiskConfig(**raw["risk"]),
        execution = ExecutionConfig(**raw["execution"]),
        server = ServerConfig (**raw["server"]),
        database = DatabaseConfig (**raw["database"]),
    )