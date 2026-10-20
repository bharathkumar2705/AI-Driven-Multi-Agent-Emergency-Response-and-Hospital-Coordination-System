"""
AI-Driven Multi-Agent Emergency Response System - FastAPI Backend
"""
import asyncio
import json
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from database.mongo import connect_db, disconnect_db
from communication.message_bus import get_message_bus
from simulation.simulator import get_simulator

from api import hospitals, ambulances, patients, doctors, roads, emergencies, simulation, search, knowledge, agents

load_dotenv()

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    # Pre-initialize simulator with default scenario
    sim = get_simulator()
    sim.initialize("scenario_1")
    yield
    await disconnect_db()


app = FastAPI(
    title="FOAI Emergency Response System",
    description="AI-Driven Multi-Agent Emergency Response & Hospital Coordination",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST routers
PREFIX = "/api/v1"
app.include_router(hospitals.router, prefix=PREFIX, tags=["Hospitals"])
app.include_router(ambulances.router, prefix=PREFIX, tags=["Ambulances"])
app.include_router(patients.router, prefix=PREFIX, tags=["Patients"])
app.include_router(doctors.router, prefix=PREFIX, tags=["Doctors"])
app.include_router(roads.router, prefix=PREFIX, tags=["Roads"])
app.include_router(emergencies.router, prefix=PREFIX, tags=["Emergencies"])
app.include_router(simulation.router, prefix=PREFIX, tags=["Simulation"])
app.include_router(search.router, prefix=PREFIX, tags=["Search"])
app.include_router(knowledge.router, prefix=PREFIX, tags=["Knowledge"])
app.include_router(agents.router, prefix=PREFIX, tags=["Agents"])


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    bus = get_message_bus()
    bus.add_ws_client(websocket)
    try:
        # Send initial state on connect
        sim = get_simulator()
        state = sim.get_full_state()
        await websocket.send_text(json.dumps({"type": "INITIAL_STATE", "data": state}))

        while True:
            # Keep connection alive; data is pushed from simulator ticks
            try:
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                data = json.loads(msg)
                # Handle ping
                if data.get("type") == "PING":
                    await websocket.send_text(json.dumps({"type": "PONG"}))
            except asyncio.TimeoutError:
                await websocket.send_text(json.dumps({"type": "HEARTBEAT"}))
    except WebSocketDisconnect:
        bus.remove_ws_client(websocket)
    except Exception:
        bus.remove_ws_client(websocket)


@app.get("/")
def root():
    return {
        "name": "FOAI Emergency Response System",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "ok"}
