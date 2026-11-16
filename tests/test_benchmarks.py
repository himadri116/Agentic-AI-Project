"""
Unit test for BenchmarkSuite execution.
"""

from devteam_ai.benchmarks.suite import BenchmarkSuite
from devteam_ai.llm.provider import LLMProvider


def test_benchmark_suite_single():
    provider = LLMProvider(mode="autonomous")
    suite = BenchmarkSuite(provider=provider)
    result = suite.run_single("lru_cache_ttl")
    
    assert result.challenge_id == 1
    assert result.final_passed is True
    assert result.passed_tests == 6
    assert result.total_tests == 6
