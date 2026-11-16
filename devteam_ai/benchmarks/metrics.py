"""
Benchmark Metrics Tracker: Computes Pass@1, Pass@2, MTTR, and Recovery Rates.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class ChallengeBenchmarkResult(BaseModel):
    challenge_id: int
    key: str
    title: str
    pass_at_1: bool
    pass_at_2: bool
    final_passed: bool
    healing_cycles: int
    duration_seconds: float
    total_tests: int
    passed_tests: int
    failed_tests: int
    error_summary: str = ""


class BenchmarkSummary(BaseModel):
    total_challenges: int = 0
    passed_at_1_count: int = 0
    passed_at_2_count: int = 0
    final_passed_count: int = 0
    pass_at_1_rate: float = 0.0
    pass_at_2_rate: float = 0.0
    final_pass_rate: float = 0.0
    mean_time_to_resolve: float = 0.0
    autonomous_recovery_rate: float = 0.0
    results: List[ChallengeBenchmarkResult] = Field(default_factory=list)


def calculate_benchmark_summary(results: List[ChallengeBenchmarkResult]) -> BenchmarkSummary:
    """Aggregates individual challenge results into empirical academic metrics."""
    if not results:
        return BenchmarkSummary()

    total = len(results)
    pass_1 = sum(1 for r in results if r.pass_at_1)
    pass_2 = sum(1 for r in results if r.pass_at_2 or r.pass_at_1)
    final_pass = sum(1 for r in results if r.final_passed)
    total_time = sum(r.duration_seconds for r in results)

    # Self-healing recovery rate: of those that failed at 1, how many healed?
    failed_at_1 = [r for r in results if not r.pass_at_1]
    healed = [r for r in failed_at_1 if r.final_passed and r.healing_cycles > 0]
    recovery_rate = (len(healed) / len(failed_at_1) * 100.0) if failed_at_1 else 100.0

    return BenchmarkSummary(
        total_challenges=total,
        passed_at_1_count=pass_1,
        passed_at_2_count=pass_2,
        final_passed_count=final_pass,
        pass_at_1_rate=round(pass_1 / total * 100.0, 1),
        pass_at_2_rate=round(pass_2 / total * 100.0, 1),
        final_pass_rate=round(final_pass / total * 100.0, 1),
        mean_time_to_resolve=round(total_time / total, 2),
        autonomous_recovery_rate=round(recovery_rate, 1),
        results=results
    )
