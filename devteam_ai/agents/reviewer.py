"""
Reviewer & Healer Agent: Senior Staff Debugger.
Performs AST and traceback analysis on failed test runs.
Diagnoses root causes and feeds targeted patch guidance back to Developer.
"""

import json
from typing import Dict, Any
from devteam_ai.agents.base import BaseAgent
from devteam_ai.state import DevTeamState, ReviewFeedback
from devteam_ai.sandbox.ast_analyzer import correlate_traceback_with_ast


REVIEWER_SYSTEM_PROMPT = """You are a Senior Staff Debugger and Reviewer at DevTeam AI.
A test suite execution has failed. Your job is to conduct rigorous root-cause analysis.
Instructions:
1. Examine the stderr traceback and test failure messages.
2. Analyze the AST correlation pointing to the faulty component or line.
3. Formulate precise, surgical patch instructions for the Developer Agent.
4. Output your analysis as a valid JSON object matching the ReviewFeedback schema:
{
  "root_cause": "Detailed explanation of why the test failed...",
  "ast_diagnosis": "Identified method/variable in AST where logic diverged...",
  "patch_guidance": "Exact instructions on what to change in solution.py...",
  "affected_components": ["ClassName or FunctionName"],
  "severity": "ERROR"
}
"""


class ReviewerAgent(BaseAgent):
    """Diagnoses runtime test failures and formulates surgical code patches."""

    def __init__(self, provider):
        super().__init__(name="ReviewerAgent", role="Senior Staff Debugger", provider=provider)

    def run(self, state: DevTeamState) -> Dict[str, Any]:
        test_results = state.get("test_results", {})
        solution_code = state.get("solution_code", "")
        traceback_str = test_results.get("traceback", "") or test_results.get("stderr", "")
        error_summary = test_results.get("error_summary", "Assertion failure during test execution")
        current_iter = state.get("healing_iteration", 0) + 1

        # AST Traceback correlation
        ast_correlation = correlate_traceback_with_ast(solution_code, traceback_str)

        user_prompt = (
            f"DEBUGGING & ROOT CAUSE ANALYSIS (Iteration #{current_iter}):\n"
            f"Error Summary: {error_summary}\n"
            f"Traceback:\n{traceback_str}\n\n"
            f"AST Correlation:\n{json.dumps(ast_correlation, indent=2)}\n\n"
            f"Source Code:\n```python\n{solution_code}\n```\n\n"
            f"Provide surgical root cause diagnosis and patch guidance in JSON."
        )

        raw_analysis = self.provider.generate(REVIEWER_SYSTEM_PROMPT, user_prompt, temperature=0.1)

        # Parse JSON
        feedback_dict = {}
        try:
            cleaned = raw_analysis.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            feedback_dict = json.loads(cleaned.strip())
        except Exception:
            feedback_dict = {
                "root_cause": error_summary,
                "ast_diagnosis": f"Fault detected around {ast_correlation.get('faulty_function') or 'solution'} (line {ast_correlation.get('faulty_line', 'unknown')})",
                "patch_guidance": "Refactor boundary condition and ensure proper handling of expired entries and capacity limits.",
                "affected_components": [ast_correlation.get('faulty_class') or "Solution"],
                "severity": "ERROR"
            }

        # Safely handle root_cause and components
        root_cause_val = feedback_dict.get("root_cause")
        root_cause_str = str(root_cause_val) if root_cause_val else str(error_summary or "Identified test failure")
        affected_comps = feedback_dict.get("affected_components")
        comp_name = affected_comps[0] if (isinstance(affected_comps, list) and affected_comps) else "Component"

        # Build message
        msg_text = (
            f"[Self-Healing Iteration #{current_iter}] Diagnosed failure: {root_cause_str[:120]}... "
            f"Targeting component '{comp_name}'. "
            f"Dispatching surgical patch instructions to Developer Agent."
        )

        msg = self.create_message(
            phase=f"Phase 4: Root-Cause Diagnosis #{current_iter}",
            content=msg_text,
            metadata={"iteration": current_iter, "feedback": feedback_dict}
        )

        history = list(state.get("healing_history", []))
        history.append({
            "iteration": current_iter,
            "error_summary": error_summary,
            "feedback": feedback_dict
        })

        return {
            "review_feedback": feedback_dict,
            "healing_iteration": current_iter,
            "healing_history": history,
            "current_phase": f"Phase 4: Self-Healing Loop (Iteration {current_iter})",
            "active_agent": "Developer Agent",
            "messages": [msg]
        }
