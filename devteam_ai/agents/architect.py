"""
Architect Agent: System Designer & Specifier.
Decomposes natural language requirements into formal specifications:
classes, type-annotated method signatures, invariants, and pre/post-conditions.
"""

import json
from typing import Dict, Any
from devteam_ai.agents.base import BaseAgent
from devteam_ai.state import DevTeamState, ArchitectSpec


ARCHITECT_SYSTEM_PROMPT = """You are the Lead Software Architect at DevTeam AI.
Your responsibility is to decompose complex software requirements into formal, rigorous technical specifications.
Define:
1. Target class hierarchy and responsibilities
2. Exact method signatures with full type annotations
3. Invariants that must hold across all states
4. Pre-conditions and post-conditions for critical operations
5. Boundary edge conditions to be respected

Output your response as a valid JSON object matching the ArchitectSpec schema:
{
  "title": "ComponentName",
  "classes": [
    {
      "name": "ClassName",
      "description": "...",
      "methods": [
        {"name": "method_name", "params": ["self", "arg1: int"], "return_type": "bool", "description": "..."}
      ]
    }
  ],
  "invariants": ["..."],
  "pre_conditions": ["..."],
  "post_conditions": ["..."],
  "algorithmic_approach": "...",
  "edge_cases": ["..."]
}
"""


class ArchitectAgent(BaseAgent):
    """Decomposes requirements into structured interface blueprints."""

    def __init__(self, provider):
        super().__init__(name="ArchitectAgent", role="System Designer & Specifier", provider=provider)

    def run(self, state: DevTeamState) -> Dict[str, Any]:
        prompt = state.get("prompt", "")
        system_prompt = ARCHITECT_SYSTEM_PROMPT
        user_prompt = f"Decompose this software requirement into a formal technical spec:\n\n{prompt}"

        raw_response = self.provider.generate(system_prompt, user_prompt, temperature=0.1)

        # Parse JSON
        spec_dict = {}
        try:
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            spec_dict = json.loads(cleaned.strip())
        except Exception:
            # Fallback structure
            spec_dict = {
                "title": "ArchitectSpecification",
                "classes": [{"name": "Solution", "description": "Core implementation class.", "methods": []}],
                "invariants": ["System must remain consistent and thread-safe"],
                "pre_conditions": ["Input arguments valid"],
                "post_conditions": ["State accurately updated"],
                "algorithmic_approach": "Decomposed modular architecture",
                "edge_cases": ["Capacity exhaustion", "Null inputs", "Concurrency contention"]
            }

        num_classes = len(spec_dict.get("classes", []))
        summary = (
            f"Completed architectural decomposition for '{spec_dict.get('title', 'Component')}'. "
            f"Defined {num_classes} classes, {len(spec_dict.get('invariants', []))} invariants, "
            f"and {len(spec_dict.get('edge_cases', []))} boundary edge cases."
        )

        msg = self.create_message(
            phase="Phase 1: Architectural Decomposition",
            content=summary,
            metadata={"spec_title": spec_dict.get("title")}
        )

        return {
            "architect_spec": spec_dict,
            "current_phase": "Phase 2: Parallel Implementation & Adversarial Test Synthesis",
            "active_agent": "Developer & QA Agents",
            "messages": [msg]
        }
