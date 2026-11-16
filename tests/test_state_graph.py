"""
Unit tests for DevTeam AI LangGraph State Machine and Self-Healing Cycle.
"""

import pytest
from devteam_ai.graph import DevTeamOrchestrator
from devteam_ai.llm.provider import LLMProvider


def test_orchestrator_successful_pipeline():
    provider = LLMProvider(mode="autonomous")
    orchestrator = DevTeamOrchestrator(provider=provider, timeout_seconds=15.0)

    final_state = orchestrator.run(prompt="Implement Dijkstra's Shortest Path Algorithm on Weighted Directed Graphs.")
    
    assert final_state["status"] == "VERIFIED"
    assert final_state["test_results"]["is_success"] is True
    assert final_state["test_results"]["passed_count"] >= 5
    assert "documentation" in final_state
    assert "time_complexity" in final_state["documentation"]


def test_orchestrator_self_healing_recovery():
    provider = LLMProvider(mode="autonomous")
    orchestrator = DevTeamOrchestrator(provider=provider, timeout_seconds=15.0)

    # token_bucket has an intentional boundary failure on iteration 1 and heals on iteration 2
    final_state = orchestrator.run(prompt="Implement a Token Bucket Rate Limiter with Burst Capacity & Concurrency.")

    assert final_state["status"] == "VERIFIED"
    assert final_state["healing_iteration"] >= 1
    assert final_state["metrics"]["pass_at_1"] is False
    assert final_state["metrics"]["pass_at_2"] is True
    assert final_state["test_results"]["is_success"] is True
