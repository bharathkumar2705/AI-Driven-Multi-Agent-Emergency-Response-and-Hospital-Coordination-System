"""
Agent Message Bus - publish/subscribe system for inter-agent communication.
All messages are logged and broadcast to WebSocket clients.
"""
from typing import List, Dict, Callable, Any
import asyncio
import datetime
import uuid
from database.mongo import get_db

class AgentMessage:
    def __init__(self, sender: str, receiver: str, message_type: str,
                 content: str, data: dict = None):
        self.message_id = str(uuid.uuid4())[:8]
        self.timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.content = content
        self.data = data or {}

    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "sender": self.sender,
            "receiver": self.receiver,
            "message_type": self.message_type,
            "content": self.content,
            "data": self.data
        }


class MessageBus:
    def __init__(self):
        self._log: List[AgentMessage] = []
        self._ws_clients: List = []  # WebSocket connections
        self._tick_messages: List[AgentMessage] = []  # messages in current tick

    def publish(self, sender: str, receiver: str, message_type: str,
                content: str, data: dict = None) -> AgentMessage:
        msg = AgentMessage(sender, receiver, message_type, content, data)
        self._log.append(msg)
        self._tick_messages.append(msg)
        
        db = get_db()
        if db is not None:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Fire and forget DB insertion
                    asyncio.create_task(db["agent_messages"].insert_one(msg.to_dict()))
            except Exception:
                pass
                
        return msg

    def collect_agent_messages(self, outbox: List[dict]):
        """Collect messages from an agent's outbox into the bus log."""
        for m in outbox:
            self.publish(
                m["sender"], m["receiver"], m["message_type"],
                m["content"], m.get("data", {})
            )

    def flush_tick_messages(self) -> List[dict]:
        """Return and clear messages queued during this tick."""
        msgs = [m.to_dict() for m in self._tick_messages]
        self._tick_messages.clear()
        return msgs

    def get_all_messages(self, limit: int = 100) -> List[dict]:
        return [m.to_dict() for m in self._log[-limit:]]

    def get_message_count(self) -> int:
        return len(self._log)

    def add_ws_client(self, ws):
        self._ws_clients.append(ws)

    def remove_ws_client(self, ws):
        if ws in self._ws_clients:
            self._ws_clients.remove(ws)

    async def broadcast(self, data: dict):
        """Send data to all connected WebSocket clients."""
        if not self._ws_clients:
            return
        dead = []
        for ws in self._ws_clients:
            try:
                import json
                await ws.send_text(json.dumps(data))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.remove_ws_client(ws)

    def clear_log(self):
        self._log.clear()
        self._tick_messages.clear()


# Global message bus
_bus: MessageBus = None

def get_message_bus() -> MessageBus:
    global _bus
    if _bus is None:
        _bus = MessageBus()
    return _bus

def reset_message_bus() -> MessageBus:
    global _bus
    _bus = MessageBus()
    return _bus
