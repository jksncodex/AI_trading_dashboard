# Trading Dashboard

A self-hosted, AI-assisted trading system built from scratch in Python.

## What it is
An event-driven paper trading dashboard with a live browser interface.
Prices come in, a strategy generates signals, a risk gate approves or blocks them,
and paper orders are executed and tracked. Everything is saved to a local database.
A live dashboard shows positions, P&L, and an equity curve in real time.

## What it is not (yet)
This is Phase 1 — the foundation. It is not connected to real money or a real broker.
The strategy included is a simple moving average crossover, included only to prove
the pipeline works end to end.

## Planned
- Phase 2: Backtesting and validation harness
- Phase 3: Machine learning strategies (Temporal Convolutional Network, Graph Diffusion, ETF shock modelling)
- Phase 4: Live broker connection and real execution

## Built with
- Python 3.10+
- FastAPI + Uvicorn (web server and dashboard)
- SQLite (local database)
- CCXT (exchange data feed, optional)

## Status
Setting up project structure and configuration layer.