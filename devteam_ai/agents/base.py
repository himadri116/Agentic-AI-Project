"""
Base Agent Definition: Standardizes agent interfaces, logging, and message passing.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import datetime
from devteam_ai.state import DevTeamState, AgentMessage
from devteam_ai.llm.provider import LLMProvider


class BaseAgent(ABC):
    """Abstract base class for all DevTeam AI specialized agents."""

    def __init__(self, name: str, role: str, provider: LLMProvider):
        self.name = name
        self.role = role
        self.provider = provider

    def create_message(self, phase: str, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Creates a standardized agent message for the blackboard."""
        msg = AgentMessage(
            sender=self.name,
            role=self.role,
            phase=phase,
            content=content,
            timestamp=datetime.datetime.now().strftime("%H:%M:%S"),
            metadata=metadata or {}
        )
        return msg.model_dump()

    @abstractmethod
    def run(self, state: DevTeamState) -> Dict[str, Any]:
        """Executes the agent's core task and returns state patch dictionary."""
        pass
