"""
QA Test Agent: Adversarial Test Engineer.
Independently authors extensive Pytest test suites (test_solution.py).
Generates 6-12 targeted test cases probing boundary values, stress conditions,
concurrency, and exception states.
"""

import json
from typing import Dict, Any
from devteam_ai.agents.base import BaseAgent
from devteam_ai.state import DevTeamState
from devteam_ai.sandbox.ast_analyzer import analyze_code_ast


QA_SYSTEM_PROMPT = """You are an Adversarial QA Test Engineer at DevTeam AI.
Your mindset is skeptical, rigorous, and adversarial: your goal is to break the implementation by finding edge cases.
Requirements:
1. Write 6 to 12 targeted Pytest cases in `test_solution.py`.
2. Probe boundary conditions: 0 capacity, empty inputs, negative values, timeouts, duplicate keys.
3. Test exception handling with `pytest.raises(...)`.
4. Test concurrent operations, race conditions, or state consistency where applicable.
5. Import components directly from `solution` (e.g. `from solution import ...`).
6. Return ONLY executable Pytest code inside a markdown code block (```python ... ```).
"""


class QAEngineerAgent(BaseAgent):
    """Synthesizes adversarial test suites probing edge conditions and stress limits."""

    def __init__(self, provider):
        super().__init__(name="QATestAgent", role="Adversarial Test Engineer", provider=provider)

    def run(self, state: DevTeamState) -> Dict[str, Any]:
        prompt = state.get("prompt", "")
        spec = state.get("architect_spec", {})

        user_prompt = (
            f"ADVERSARIAL TESTING TASK:\n"
            f"Task Requirement: {prompt}\n\n"
            f"Architectural Spec & Invariants:\n{json.dumps(spec, indent=2)}\n\n"
            f"Write a comprehensive adversarial Pytest suite (`test_solution.py`) covering all boundary conditions."
        )

        raw_code = self.provider.generate(QA_SYSTEM_PROMPT, user_prompt, temperature=0.2)

        # Extract code from markdown fences
        clean_test = raw_code.strip()
        if "```python" in clean_test:
            clean_test = clean_test.split("```python")[1].split("```")[0].strip()
        elif "```" in clean_test:
            clean_test = clean_test.split("```")[1].split("```")[0].strip()

        # Count test functions
        ast_check = analyze_code_ast(clean_test)
        test_count = len([fn for fn in ast_check.functions if fn.startswith("test_")])

        summary = (
            f"Authored adversarial Pytest suite test_solution.py with {test_count} targeted test cases "
            f"probing invariants, boundary limits, and stress conditions."
        )

        msg = self.create_message(
            phase="Phase 2: Adversarial Test Synthesis",
            content=summary,
            metadata={"test_count": test_count}
        )

        return {
            "test_code": clean_test,
            "active_agent": "Execution Sandbox Engine",
            "messages": [msg]
        }
