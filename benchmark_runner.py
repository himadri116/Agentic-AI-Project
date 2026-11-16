"""
DevTeam AI Benchmark Evaluation Runner:
Executes the 15 classic Computer Science & Software Engineering challenges,
measures Pass@1, Pass@2, MTTR, and generates academic verification reports.
"""

import os
import sys
import json
import time
import argparse
from devteam_ai.benchmarks.suite import BenchmarkSuite
from devteam_ai.llm.provider import LLMProvider
from devteam_ai.llm.knowledge_base import BENCHMARK_CHALLENGES


def print_banner():
    print("=" * 85)
    print(" DevTeam AI: Autonomous Multi-Agent System - 15-Challenge Benchmark Suite")
    print(" Author: Himadri Bahuguna (BT23GCS204) | ET 4-1 Learning Technologies Project")
    print("=" * 85)


def main():
    parser = argparse.ArgumentParser(description="Run DevTeam AI Benchmark Suite across 15 CS Challenges")
    parser.add_argument("--mode", type=str, default="auto", choices=["auto", "gemini", "ollama", "autonomous"], help="LLM backend mode")
    parser.add_argument("--output", type=str, default="benchmark_results.json", help="Path to save output JSON metrics")
    parser.add_argument("--report", type=str, default="benchmark_report.md", help="Path to save markdown summary report")
    parser.add_argument("--limit", type=int, default=15, help="Limit number of challenges to run (1-15)")
    args = parser.parse_args()

    print_banner()

    provider = LLMProvider(mode=args.mode)
    suite = BenchmarkSuite(provider=provider)

    print(f"\n[+] Executing evaluation across {min(args.limit, len(BENCHMARK_CHALLENGES))} benchmark challenges...")
    print(f"[+] LLM Backend Mode: {provider.get_effective_mode().upper()}\n")

    keys = list(BENCHMARK_CHALLENGES.keys())[:args.limit]
    results = []

    print(f"{'#':<3} | {'Challenge Title':<45} | {'Pass@1':<7} | {'Pass@2':<7} | {'Cycles':<6} | {'Tests':<7} | {'Time(s)':<7}")
    print("-" * 88)

    for idx, key in enumerate(keys, 1):
        res = suite.run_single(key)
        results.append(res)
        pass1_str = "PASS" if res.pass_at_1 else "FAIL"
        pass2_str = "PASS" if res.pass_at_2 else "FAIL"
        tests_str = f"{res.passed_tests}/{res.total_tests}"
        print(f"{res.challenge_id:<3} | {res.title[:45]:<45} | {pass1_str:<7} | {pass2_str:<7} | {res.healing_cycles:<6} | {tests_str:<7} | {res.duration_seconds:<7.2f}")

    print("-" * 88)

    # Compute empirical summary
    from devteam_ai.benchmarks.metrics import calculate_benchmark_summary
    summary = calculate_benchmark_summary(results)

    print("\n" + "=" * 85)
    print(" EMPIRICAL VERIFICATION BENCHMARK METRICS SUMMARY")
    print("=" * 85)
    print(f"Total Challenges Evaluated:       {summary.total_challenges}")
    print(f"Pass@1 Rate (Initial Generation): {summary.pass_at_1_rate}%  (Target: > 70.0%) -> {'[MET]' if summary.pass_at_1_rate >= 70.0 else '[BELOW]'}")
    print(f"Pass@2 Rate (Self-Healed):        {summary.pass_at_2_rate}% (Target: > 90.0%) -> {'[MET]' if summary.pass_at_2_rate >= 90.0 else '[BELOW]'}")
    print(f"Final Test Passage Rate:          {summary.final_pass_rate}%")
    print(f"Autonomous Self-Healing Rate:     {summary.autonomous_recovery_rate}% (Target: > 85.0%) -> {'[MET]' if summary.autonomous_recovery_rate >= 85.0 else '[BELOW]'}")
    print(f"Mean Time to Resolve (MTTR):      {summary.mean_time_to_resolve}s (Target: < 45.0s) -> {'[MET]' if summary.mean_time_to_resolve < 45.0 else '[BELOW]'}")
    print("=" * 85)

    # Save to JSON
    json_path = os.path.abspath(args.output)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary.model_dump(), f, indent=2)
    print(f"\n[+] Raw metrics saved to: {json_path}")

    # Save Markdown report
    md_content = f"""# DevTeam AI: 15-Challenge Empirical Benchmark Report
**Student Name:** Himadri Bahuguna (BT23GCS204)  
**Subject:** ET 4-1 Learning Technologies Project Course  
**System:** Autonomous Multi-Agent Collaborative Development with Self-Healing Verification  

---

## 1. Executive Summary & Verification Targets

| Metric | Target Benchmark | Achieved Result | Verification Status |
| :--- | :--- | :--- | :--- |
| **Pass@1 Rate** | > 70.0% | **{summary.pass_at_1_rate}%** | {'✅ MET' if summary.pass_at_1_rate >= 70.0 else '⚠️ BELOW'} |
| **Pass@2 Rate (Self-Healed)** | > 90.0% | **{summary.pass_at_2_rate}%** | {'✅ MET' if summary.pass_at_2_rate >= 90.0 else '⚠️ BELOW'} |
| **Autonomous Recovery Rate** | > 85.0% | **{summary.autonomous_recovery_rate}%** | {'✅ MET' if summary.autonomous_recovery_rate >= 85.0 else '⚠️ BELOW'} |
| **Mean Time to Resolve (MTTR)** | < 45.0s | **{summary.mean_time_to_resolve}s** | {'✅ MET' if summary.mean_time_to_resolve < 45.0 else '⚠️ BELOW'} |

---

## 2. Detailed Per-Challenge Breakdown

| # | Challenge Name | Pass@1 | Pass@2 | Healing Cycles | Tests Passed | Duration (s) |
| :-: | :--- | :-: | :-: | :-: | :-: | :-: |
"""
    for r in results:
        p1 = "✅ PASS" if r.pass_at_1 else "❌ FAIL"
        p2 = "✅ PASS" if r.pass_at_2 else "❌ FAIL"
        md_content += f"| {r.challenge_id} | {r.title} | {p1} | {p2} | {r.healing_cycles} | {r.passed_tests}/{r.total_tests} | {r.duration_seconds}s |\n"

    md_content += f"""
---
*Report generated automatically by DevTeam AI Benchmark Suite.*
"""
    report_path = os.path.abspath(args.report)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[+] Academic Markdown report saved to: {report_path}")


if __name__ == "__main__":
    main()
