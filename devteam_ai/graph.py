"""
LangGraph Multi-Agent State Graph Orchestrator.
Builds the cyclic state machine with conditional branching and self-healing retry loop.
"""

import time
from typing import Dict, Any, Callable, Optional
from langgraph.graph import StateGraph, START, END

from devteam_ai.state import DevTeamState, merge_messages
from devteam_ai.llm.provider import LLMProvider
from devteam_ai.sandbox.executor import SandboxExecutor
from devteam_ai.agents.architect import ArchitectAgent
from devteam_ai.agents.developer import DeveloperAgent
from devteam_ai.agents.qa_engineer import QAEngineerAgent
from devteam_ai.agents.reviewer import ReviewerAgent
from devteam_ai.agents.documenter import DocumenterAgent


class DevTeamOrchestrator:
    """Multi-Agent LangGraph State Machine for DevTeam AI."""

    def __init__(self, provider: Optional[LLMProvider] = None, timeout_seconds: float = 25.0):
        self.provider = provider or LLMProvider()
        self.sandbox = SandboxExecutor(timeout_seconds=timeout_seconds)

        # Initialize agents
        self.architect = ArchitectAgent(self.provider)
        self.developer = DeveloperAgent(self.provider)
        self.qa = QAEngineerAgent(self.provider)
        self.reviewer = ReviewerAgent(self.provider)
        self.documenter = DocumenterAgent(self.provider)

        # Build graph
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(DevTeamState)

        # Add Agent and Sandbox Nodes
        builder.add_node("architect", self._architect_node)
        builder.add_node("developer", self._developer_node)
        builder.add_node("qa_engineer", self._qa_node)
        builder.add_node("sandbox_executor", self._sandbox_node)
        builder.add_node("reviewer", self._reviewer_node)
        builder.add_node("documenter", self._documenter_node)

        # Wire Graph Transitions
        builder.add_edge(START, "architect")
        builder.add_edge("architect", "developer")
        builder.add_edge("developer", "qa_engineer")
        builder.add_edge("qa_engineer", "sandbox_executor")

        # Conditional Edge after Sandbox execution
        builder.add_conditional_edges(
            "sandbox_executor",
            self._route_after_sandbox,
            {
                "documenter": "documenter",
                "reviewer": "reviewer",
            }
        )

        # Closed-Loop Self-Healing: Reviewer -> Developer
        builder.add_edge("reviewer", "developer")

        # Terminal Edge
        builder.add_edge("documenter", END)

        return builder.compile()

    # Node Implementations
    def _architect_node(self, state: DevTeamState) -> Dict[str, Any]:
        patch = self.architect.run(state)
        patch["messages"] = merge_messages(state.get("messages", []), patch.get("messages", []))
        return patch

    def _developer_node(self, state: DevTeamState) -> Dict[str, Any]:
        patch = self.developer.run(state)
        patch["messages"] = merge_messages(state.get("messages", []), patch.get("messages", []))
        return patch

    def _qa_node(self, state: DevTeamState) -> Dict[str, Any]:
        # If we already have tests from iteration 0, we preserve them so Developer is tested against the same adversarial suite
        if state.get("test_code") and state.get("healing_iteration", 0) > 0:
            return {"active_agent": "Execution Sandbox"}
        patch = self.qa.run(state)
        patch["messages"] = merge_messages(state.get("messages", []), patch.get("messages", []))
        return patch

    def _sandbox_node(self, state: DevTeamState) -> Dict[str, Any]:
        solution_code = state.get("solution_code", "")
        test_code = state.get("test_code", "")
        curr_iter = state.get("healing_iteration", 0)

        # Execute tests in isolated scratch directory
        result = self.sandbox.execute(solution_code, test_code)
        result_dict = result.model_dump()

        summary_msg = (
            f"Pytest Execution completed in {result.duration_seconds}s. "
            f"Exit Code: {result.exit_code}. Passed: {result.passed_count}, Failed: {result.failed_count}."
        )

        msg = {
            "sender": "SandboxExecutor",
            "role": "Local Sandbox Runtime Judge",
            "phase": f"Phase 3: Subprocess Execution (Run #{curr_iter + 1})",
            "content": summary_msg,
            "timestamp": time.strftime("%H:%M:%S"),
            "metadata": {
                "exit_code": result.exit_code,
                "passed": result.passed_count,
                "failed": result.failed_count,
                "duration": result.duration_seconds
            }
        }

        # Check empirical benchmark metrics
        metrics = dict(state.get("metrics", {}))
        if curr_iter == 0:
            metrics["pass_at_1"] = result.is_success
        elif curr_iter == 1:
            metrics["pass_at_2"] = result.is_success

        return {
            "test_results": result_dict,
            "messages": merge_messages(state.get("messages", []), [msg]),
            "active_agent": "Reviewer & Healer" if not result.is_success else "Documenter Agent",
            "metrics": metrics
        }

    def _route_after_sandbox(self, state: DevTeamState) -> str:
        """Dynamic conditional branching based on exit code and retry count."""
        results = state.get("test_results", {})
        is_success = results.get("is_success", False)
        curr_iter = state.get("healing_iteration", 0)
        max_retries = state.get("max_healing_iterations", 3)

        if is_success:
            return "documenter"

        if curr_iter < max_retries:
            return "reviewer"
        else:
            # Exhausted max retries, proceed to document best effort
            return "documenter"

    def _reviewer_node(self, state: DevTeamState) -> Dict[str, Any]:
        patch = self.reviewer.run(state)
        patch["messages"] = merge_messages(state.get("messages", []), patch.get("messages", []))
        return patch

    def _documenter_node(self, state: DevTeamState) -> Dict[str, Any]:
        patch = self.documenter.run(state)
        patch["messages"] = merge_messages(state.get("messages", []), patch.get("messages", []))
        return patch

    def run(self, prompt: str, task_id: str = "task_001", max_retries: int = 3) -> DevTeamState:
        """Executes the full multi-agent pipeline synchronously to completion."""
        initial_state: DevTeamState = {
            "task_id": task_id,
            "prompt": prompt,
            "current_phase": "Phase 1: Ingestion & Architectural Decomposition",
            "status": "IN_PROGRESS",
            "healing_iteration": 0,
            "max_healing_iterations": max_retries,
            "healing_history": [],
            "messages": [],
            "active_agent": "Architect Agent",
            "metrics": {
                "start_time": time.time(),
                "pass_at_1": False,
                "pass_at_2": False,
                "healing_cycles": 0
            }
        }

        final_state = self.graph.invoke(initial_state)

        # Finalize metrics
        end_time = time.time()
        final_state["metrics"]["end_time"] = end_time
        final_state["metrics"]["total_duration"] = round(end_time - final_state["metrics"]["start_time"], 2)
        final_state["metrics"]["healing_cycles"] = final_state.get("healing_iteration", 0)

        return final_state
