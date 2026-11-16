"""
DevTeamState: Strongly-typed blackboard state schema for DevTeam AI.
Manages multi-agent task progression, message passing, and state persistence.
"""

from typing import TypedDict, Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
import datetime


class AgentMessage(BaseModel):
    """Structured message broadcast to the blackboard bus."""
    sender: str
    role: str
    phase: str
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().strftime("%H:%M:%S"))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MethodSpec(BaseModel):
    name: str
    params: List[str]
    return_type: str
    description: str


class ClassSpec(BaseModel):
    name: str
    description: str
    methods: List[MethodSpec] = Field(default_factory=list)


class ArchitectSpec(BaseModel):
    title: str
    classes: List[ClassSpec] = Field(default_factory=list)
    invariants: List[str] = Field(default_factory=list)
    pre_conditions: List[str] = Field(default_factory=list)
    post_conditions: List[str] = Field(default_factory=list)
    algorithmic_approach: str = ""
    edge_cases: List[str] = Field(default_factory=list)


class TestResult(BaseModel):
    exit_code: int
    passed_count: int = 0
    failed_count: int = 0
    total_count: int = 0
    duration_seconds: float = 0.0
    stdout: str = ""
    stderr: str = ""
    error_summary: str = ""
    traceback: str = ""
    is_success: bool = False


class ReviewFeedback(BaseModel):
    root_cause: str
    ast_diagnosis: str
    patch_guidance: str
    affected_components: List[str] = Field(default_factory=list)
    severity: str = "ERROR"  # "ERROR", "WARNING", "REGRESSION"


class DocumentationArtifact(BaseModel):
    time_complexity: str
    space_complexity: str
    complexity_rationale: str
    google_docstrings: str
    readme_markdown: str


def merge_messages(left: List[Dict[str, Any]], right: Union[List[Dict[str, Any]], Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Reducer to append messages to the blackboard."""
    if left is None:
        left = []
    if right is None:
        return left
    if isinstance(right, dict):
        return left + [right]
    return left + list(right)


class DevTeamState(TypedDict, total=False):
    """
    Typed blackboard state machine schema representing DevTeamState.
    Adheres strictly to the LangGraph cyclic state-graph requirements.
    """
    # Core Task Definition
    task_id: str
    prompt: str
    current_phase: str
    status: str  # "IN_PROGRESS", "VERIFIED", "HEALING", "EXHAUSTED", "FAILED"

    # Agent Deliverables
    architect_spec: Optional[Dict[str, Any]]
    solution_code: str
    test_code: str
    test_results: Optional[Dict[str, Any]]
    review_feedback: Optional[Dict[str, Any]]
    documentation: Optional[Dict[str, Any]]

    # Self-Healing Control Loops
    healing_iteration: int
    max_healing_iterations: int
    healing_history: List[Dict[str, Any]]

    # Observability & Message Bus
    messages: List[Dict[str, Any]]
    active_agent: str

    # Verification & Empirical Metrics
    metrics: Dict[str, Any]
