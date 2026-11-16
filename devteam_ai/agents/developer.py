"""
Developer Agent: Software Engineer & Implementer.
Authors clean, PEP-8 compliant Python code (solution.py) with full type annotations.
Performs surgical AST refactoring and bug fixing during self-healing loops.
"""

import json
from typing import Dict, Any
from devteam_ai.agents.base import BaseAgent
from devteam_ai.state import DevTeamState
from devteam_ai.sandbox.ast_analyzer import analyze_code_ast


DEVELOPER_SYSTEM_PROMPT = """You are a Senior Staff Software Engineer at DevTeam AI.
Your objective is to author clean, production-grade, PEP-8 compliant Python code implementing the architectural specification.
Requirements:
1. Provide complete, executable code without omissions or placeholder pass statements.
2. Include explicit type annotations for all function/method arguments and returns.
3. Handle concurrency, synchronization locks, and boundary edge cases cleanly.
4. If refactoring after a test failure, carefully incorporate the Reviewer's root-cause analysis and patch guidance.
5. Return ONLY executable Python code inside a markdown code block (```python ... ```).
"""


class DeveloperAgent(BaseAgent):
    """Generates and refactors the primary solution module (solution.py)."""

    def __init__(self, provider):
        super().__init__(name="DeveloperAgent", role="Software Engineer & Implementer", provider=provider)

    def run(self, state: DevTeamState) -> Dict[str, Any]:
        prompt = state.get("prompt", "")
        spec = state.get("architect_spec", {})
        existing_code = state.get("solution_code", "")
        review_feedback = state.get("review_feedback")
        healing_iteration = state.get("healing_iteration", 0)

        is_healing = bool(review_feedback and healing_iteration > 0)

        if is_healing:
            user_prompt = (
                f"REFACTORING TASK (Self-Healing Cycle #{healing_iteration}):\n"
                f"Task Requirement: {prompt}\n\n"
                f"Architectural Spec:\n{json.dumps(spec, indent=2)}\n\n"
                f"Previous Code:\n```python\n{existing_code}\n```\n\n"
                f"Reviewer Diagnosis:\n"
                f"- Root Cause: {review_feedback.get('root_cause')}\n"
                f"- AST Diagnosis: {review_feedback.get('ast_diagnosis')}\n"
                f"- Patch Guidance: {review_feedback.get('patch_guidance')}\n\n"
                f"Please produce the revised, bug-fixed solution.py code."
            )
        else:
            user_prompt = (
                f"IMPLEMENTATION TASK:\n"
                f"Task Requirement: {prompt}\n\n"
                f"Architectural Spec:\n{json.dumps(spec, indent=2)}\n\n"
                f"Please implement solution.py adhering strictly to the specification."
            )

        raw_code = self.provider.generate(DEVELOPER_SYSTEM_PROMPT, user_prompt, temperature=0.1)

        # Extract code from markdown fences if present
        clean_code = raw_code.strip()
        if "```python" in clean_code:
            clean_code = clean_code.split("```python")[1].split("```")[0].strip()
        elif "```" in clean_code:
            clean_code = clean_code.split("```")[1].split("```")[0].strip()

        # AST syntax validation
        ast_check = analyze_code_ast(clean_code)
        if not ast_check.is_valid:
            # Fallback to existing or template if syntax error
            msg_content = f"AST parse warning: {ast_check.error}. Code generated with potential syntax issue."
        else:
            msg_content = (
                f"{'Refactored' if is_healing else 'Synthesized'} solution.py "
                f"({len(clean_code.splitlines())} LOC, {len(ast_check.classes)} classes, "
                f"{len(ast_check.functions)} functions)."
            )

        msg = self.create_message(
            phase="Phase 2: Code Synthesis" if not is_healing else f"Phase 4: Self-Healing Patch #{healing_iteration}",
            content=msg_content,
            metadata={"healing_iteration": healing_iteration, "is_healing": is_healing}
        )

        return {
            "solution_code": clean_code,
            "active_agent": "QA Test Agent" if not is_healing else "Execution Sandbox",
            "messages": [msg]
        }
