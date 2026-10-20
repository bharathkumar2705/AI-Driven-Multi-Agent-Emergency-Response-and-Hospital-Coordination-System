"""Base agent class defining the PEAS framework and sense-decide-act loop."""
from typing import Dict, Any, List, Optional
import datetime


class BaseAgent:
    """
    Base class for all agents in the multi-agent system.

    PEAS Framework:
    - Performance: defined per agent subclass
    - Environment: the shared simulation state
    - Actuators: the act() method
    - Sensors: the sense() method
    """

    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.state: Dict[str, Any] = {}
        self.goal: str = ""
        self.knowledge: Dict[str, Any] = {}
        self.current_action: str = "IDLE"
        self.current_plan: Optional[str] = None
        self.message_log: List[dict] = []
        self._outbox: List[dict] = []  # messages to send this tick

    def sense(self, environment: dict):
        """Update agent knowledge from the environment."""
        raise NotImplementedError

    def decide(self) -> str:
        """Determine next action based on current state and knowledge."""
        raise NotImplementedError

    def act(self, environment: dict) -> List[dict]:
        """Execute decided action and return list of effects/messages."""
        raise NotImplementedError

    def communicate(self, sender: str, message_type: str, content: str, data: dict = None):
        """Receive a message from another agent."""
        msg = {
            "from": sender,
            "type": message_type,
            "content": content,
            "data": data or {},
            "time": _now()
        }
        self.message_log.append(msg)
        self._handle_message(msg)

    def _handle_message(self, msg: dict):
        """Override in subclasses to handle specific message types."""
        pass

    def send_message(self, receiver: str, message_type: str, content: str, data: dict = None):
        """Queue an outgoing message."""
        self._outbox.append({
            "sender": self.agent_id,
            "receiver": receiver,
            "message_type": message_type,
            "content": content,
            "data": data or {},
            "timestamp": _now()
        })

    def flush_outbox(self) -> List[dict]:
        msgs = list(self._outbox)
        self._outbox.clear()
        return msgs

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "state": self.state,
            "goal": self.goal,
            "knowledge": {k: v for k, v in self.knowledge.items() if not k.startswith('_')},
            "current_action": self.current_action,
            "current_plan": self.current_plan
        }


def _now() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")
