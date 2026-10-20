from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "foai_emergency")

_async_client: AsyncIOMotorClient = None
_db = None

async def connect_db():
    global _async_client, _db
    try:
        _async_client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        await _async_client.server_info()
        _db = _async_client[DB_NAME]
        print(f"[DB] Connected to MongoDB: {DB_NAME}")
        await _init_collections()
    except Exception as e:
        print(f"[DB] MongoDB unavailable ({e}). Using in-memory fallback.")
        _db = None

async def disconnect_db():
    if _async_client:
        _async_client.close()

def get_db():
    return _db

async def _init_collections():
    if _db is None:
        return
    collections = [
        "patients", "ambulances", "hospitals", "doctors",
        "roads", "emergencies", "agent_messages",
        "simulation_runs", "search_results", "events"
    ]
    existing = await _db.list_collection_names()
    for col in collections:
        if col not in existing:
            await _db.create_collection(col)
