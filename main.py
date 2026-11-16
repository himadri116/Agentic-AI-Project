"""
DevTeam AI CLI Runner: Run the autonomous multi-agent pipeline from the terminal.
"""

import sys
import argparse
import json
from devteam_ai.graph import DevTeamOrchestrator
from devteam_ai.llm.provider import LLMProvider
from devteam_ai.llm.knowledge_base import BENCHMARK_CHALLENGES


def main():
    parser = argparse.ArgumentParser(description="DevTeam AI: Autonomous Multi-Agent Software Development & Self-Healing Pipeline")
    parser.add_argument("--prompt", type=str, default="", help="Natural language requirements for the software component")
    parser.add_argument("--challenge", type=str, default="lru_cache_ttl", help="Key of benchmark challenge to execute (e.g. lru_cache_ttl, token_bucket, etc.)")
    parser.add_argument("--mode", type=str, default="auto", choices=["auto", "gemini", "ollama", "autonomous"], help="LLM backend mode")
    parser.add_argument("--retries", type=int, default=3, help="Maximum self-healing iterations")
    parser.add_argument("--timeout", type=float, default=25.0, help="Subprocess sandbox execution timeout (seconds)")
    args = parser.parse_args()

    # Determine prompt
    prompt = args.prompt
    if not prompt:
        if args.challenge in BENCHMARK_CHALLENGES:
            ch = BENCHMARK_CHALLENGES[args.challenge]
            print(f"[Benchmark Challenge #{ch['id']}]: {ch['title']}")
            prompt = ch["prompt"]
        else:
            prompt = "Implement a Thread-Safe In-Memory LRU Cache with TTL Expiration."

    print("=" * 70)
    print("DevTeam AI: Autonomous Multi-Agent System")
    print(f"Author: Himadri Bahuguna (BT23GCS204)")
    print(f"Backend Mode: {args.mode.upper()}")
    print(f"Task Prompt: {prompt}")
    print("=" * 70)

    provider = LLMProvider(mode=args.mode)
    orchestrator = DevTeamOrchestrator(provider=provider, timeout_seconds=args.timeout)

    print("\n[+] Launching LangGraph Multi-Agent State Machine...")
    final_state = orchestrator.run(prompt=prompt, max_retries=args.retries)

    print("\n" + "=" * 70)
    print("BLACKBOARD MESSAGE STREAM / AGENT TIMELINE:")
    print("=" * 70)
    for idx, msg in enumerate(final_state.get("messages", []), 1):
        print(f"[{msg.get('timestamp')}] {msg.get('sender')} ({msg.get('role')}):")
        print(f"  Phase: {msg.get('phase')}")
        print(f"  Content: {msg.get('content')}\n")

    test_res = final_state.get("test_results", {})
    metrics = final_state.get("metrics", {})
    doc = final_state.get("documentation", {})

    print("=" * 70)
    print("VERIFICATION & EXECUTION SUMMARY:")
    print("=" * 70)
    print(f"Final Status: {final_state.get('status')}")
    print(f"Total Pipeline Duration: {metrics.get('total_duration')}s")
    print(f"Self-Healing Iterations: {metrics.get('healing_cycles')}")
    print(f"Pass@1: {metrics.get('pass_at_1')}")
    print(f"Pass@2 (Self-Healed): {metrics.get('pass_at_2')}")
    print(f"Pytest Exit Code: {test_res.get('exit_code')}")
    print(f"Passed Tests: {test_res.get('passed_count')}/{test_res.get('total_count')}")

    if doc:
        print("\n" + "=" * 70)
        print("DOCUMENTER PROFILING REPORT:")
        print("=" * 70)
        print(f"Asymptotic Time Complexity:  {doc.get('time_complexity')}")
        print(f"Asymptotic Space Complexity: {doc.get('space_complexity')}")
        print(f"Complexity Rationale:\n  {doc.get('complexity_rationale')}")

    print("=" * 70)
    print("[SUCCESS] Pipeline completed.")


if __name__ == "__main__":
    main()
