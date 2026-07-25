from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS signals (
        id SERIAL PRIMARY KEY,
        timestamp DOUBLE PRECISION NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL
    )
    """,
    """
     CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        order_id TEXT NOT NULL,
        timestamp DOUBLE PRECISION NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,
        quantity DOUBLE PRECISION NOT NULL
    )
    """,
    """
        CREATE TABLE IF NOT EXISTS fills (
        id SERIAL PRIMARY KEY,
        order_id TEXT NOT NULL,
        timestamp DOUBLE PRECISION NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,
        quantity DOUBLE PRECISION NOT NULL,
        price DOUBLE PRECISION NOT NULL,
        fee  DOUBLE PRECISION NOT NULL
    )
    """,
"""
    CREATE TABLE IF NOT EXISTS equity (
        id SERIAL PRIMARY KEY,
        timestamp DOUBLE PRECISION NOT NULL,
        value DOUBLE PRECISION NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ai_logs (
        id SERIAL PRIMARY KEY,
        timestamp DOUBLE PRECISION NOT NULL,
        message TEXT NOT NULL
    )
    """,
]

def _sqlite_schema(stmt: str) -> str:
    return stmt.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")

def init_db(url:str) -> Engine:
    engine = create_engine(url)
    is_sqlite = url.startswith("sqlite")
    with engine.begin() as conn:
        from sqlalchemy import text
        for stmt in SCHEMA_STATEMENTS:
            if is_sqlite:
                stmt = _sqlite_schema(stmt)
            conn.execute(text(stmt))
    return engine


