"""
DevTeam AI: Autonomous Multi-Agent System for Collaborative Software Development,
Peer Review, and Self-Healing Code Verification.
"""

from devteam_ai.state import DevTeamState
from devteam_ai.graph import DevTeamOrchestrator
from devteam_ai.llm.provider import LLMProvider
from devteam_ai.sandbox.executor import SandboxExecutor
from devteam_ai.benchmarks.suite import BenchmarkSuite

__version__ = "1.0.0"
__author__ = "Himadri Bahuguna (BT23GCS204)"

__all__ = [
    "DevTeamState",
    "DevTeamOrchestrator",
    "LLMProvider",
    "SandboxExecutor",
    "BenchmarkSuite",
]
