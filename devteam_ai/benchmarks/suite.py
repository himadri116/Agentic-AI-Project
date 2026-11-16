"""
Benchmark Suite Runner: Evaluates DevTeam AI against the 15 classic computer science challenges.
Measures empirical Pass@1, Pass@2, MTTR, and self-healing resilience.
"""

import time
from typing import List, Optional, Callable
from devteam_ai.graph import DevTeamOrchestrator
from devteam_ai.llm.provider import LLMProvider
from devteam_ai.llm.knowledge_base import BENCHMARK_CHALLENGES
from devteam_ai.benchmarks.metrics import ChallengeBenchmarkResult, BenchmarkSummary, calculate_benchmark_summary


class BenchmarkSuite:
    """Executes the full 15-problem computer science verification suite."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or LLMProvider()
        self.orchestrator = DevTeamOrchestrator(provider=self.provider)

    def run_single(self, key: str, on_progress: Optional[Callable[[str], None]] = None) -> ChallengeBenchmarkResult:
        """Executes a single benchmark challenge."""
        if key not in BENCHMARK_CHALLENGES:
            raise KeyError(f"Challenge '{key}' not found in benchmark suite.")

        challenge = BENCHMARK_CHALLENGES[key]
        if on_progress:
            on_progress(f"Evaluating Challenge #{challenge['id']}: {challenge['title']}...")

        start_time = time.time()
        final_state = self.orchestrator.run(prompt=challenge["prompt"], task_id=f"bm_{key}")
        duration = round(time.time() - start_time, 2)

        test_results = final_state.get("test_results", {})
        metrics = final_state.get("metrics", {})
        healing_cycles = final_state.get("healing_iteration", 0)

        pass_1 = metrics.get("pass_at_1", False)
        pass_2 = metrics.get("pass_at_2", False)
        final_passed = test_results.get("is_success", False)

        return ChallengeBenchmarkResult(
            challenge_id=challenge["id"],
            key=key,
            title=challenge["title"],
            pass_at_1=pass_1,
            pass_at_2=pass_2 or pass_1,
            final_passed=final_passed,
            healing_cycles=healing_cycles,
            duration_seconds=duration,
            total_tests=test_results.get("total_count", 0),
            passed_tests=test_results.get("passed_count", 0),
            failed_tests=test_results.get("failed_count", 0),
            error_summary=test_results.get("error_summary", "")
        )

    def run_all(self, on_progress: Optional[Callable[[str, int, int], None]] = None) -> BenchmarkSummary:
        """Runs all 15 benchmark challenges sequentially and computes academic summary."""
        results: List[ChallengeBenchmarkResult] = []
        keys = list(BENCHMARK_CHALLENGES.keys())
        total = len(keys)

        for idx, key in enumerate(keys, 1):
            if on_progress:
                on_progress(BENCHMARK_CHALLENGES[key]["title"], idx, total)
            res = self.run_single(key)
            results.append(res)

        return calculate_benchmark_summary(results)
