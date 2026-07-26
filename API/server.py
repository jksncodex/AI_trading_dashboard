import asyncio
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pathlib import Path
from fastapi.responses import FileResponse

from config import load_config
from engine.events import (
    SIGNAL, ORDER_APPROVED, ORDER_REJECTED, FILL, EQUITY_UPDATE, AI_FEEDBACK,)
from engine.orchestrator import Orchestrator
from persistence.db import init_db
from persistence.repository import Repository
from ai.feedback import AIFeedback

app = FastAPI()

state = {}


@app.on_event("startup")
async def startup() -> None:
    config = load_config()
    engine = init_db(config.database.url)
    repo = Repository(engine)
    orch = Orchestrator(config)
    ai = AIFeedback(orch.bus, repo)

    orch.bus.subscribe(SIGNAL, lambda intent: repo.save_signal(intent))
    orch.bus.subscribe(ORDER_APPROVED, lambda order: repo.save_order(order))
    orch.bus.subscribe(FILL, lambda fill: repo.save_fill(fill))
    orch.bus.subscribe(
        EQUITY_UPDATE, lambda value: repo.save_equity(time.time(), value)
    )

    async def on_fill_ws(fill):
        await broadcast({
            "type": "fill",
            "symbol": fill.symbol,
            "side": fill.side,
            "quantity": fill.quantity,
            "price": fill.price,
            "fee": fill.fee,
            "timestamp": fill.timestamp,
        })

    async def on_equity_ws(value):
        await broadcast({
            "type": "equity",
            "value": value,
            "timestamp": time.time(),
        })

    async def on_signal_ws(intent):
        await broadcast({
            "type": "signal",
            "symbol": intent.symbol,
            "side": intent.side,
            "timestamp": intent.timestamp,
        })

    async def on_ai_ws(payload):
        await broadcast({
            "type": "ai",
            "timestamp": payload["timestamp"],
            "message": payload["message"],
        })

    orch.bus.subscribe(FILL, on_fill_ws)
    orch.bus.subscribe(EQUITY_UPDATE, on_equity_ws)
    orch.bus.subscribe(SIGNAL, on_signal_ws)
    orch.bus.subscribe(ORDER_REJECTED, on_reject_ws)
    orch.bus.subscribe(AI_FEEDBACK, on_ai_ws)


    state["config"] = config
    state["repo"] = repo
    state["orch"] = orch
    state["ai"] = ai
    state["feed_task"] = asyncio.create_task(orch.start())

@app.post("/api/contorl/release")
async def release_kill():
    state["orch"].engage_kill_switch()
    return {"ok": True, "kill_switch": True}


@app.post("/api/control/release")
async def release_kill():
    state["orch"].release_kill_switch()
    return {"ok": True, "kill_switch": False}

@app.post("/api.control/flatten")
async def flatten():
    await state["orch"].flatten_all()
    return{"ok": True}

@app.post("/api/control/pause")
async def pause():
    state["orch"].pause_strategy()
    return {"ok": True, "paused": True}

@app.post("/api/control/resume")
async def resume():
    state["orch"].resume_strategy()
    return {"ok": True, "paused": False}


clients = []


async def broadcast(message: dict) -> None:
    dead = []
    for ws in clients:
        try:
            await ws.send_json(message)
        except Exception:
            dead.append(ws)
    for ws in dead:
        clients.remove(ws)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        if ws in clients:
            clients.remove(ws)