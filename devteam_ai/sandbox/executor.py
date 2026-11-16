"""
Subprocess Sandbox Engine: Executes Pytest test suites in isolated temporary environments.
Intercepts exit codes, assertion errors, stdout/stderr, and runtime latencies with strict timeouts.
"""

import os
import sys
import time
import tempfile
import subprocess
import re
from typing import Optional
from devteam_ai.state import TestResult


class SandboxExecutor:
    """Harness executing tests in isolated scratch directories with strict timeouts."""

    def __init__(self, timeout_seconds: float = 25.0):
        self.timeout_seconds = timeout_seconds

    def execute(self, solution_code: str, test_code: str) -> TestResult:
        """
        Writes solution.py and test_solution.py into a temporary scratch directory,
        invokes `pytest -v test_solution.py` via subprocess, and returns a structured TestResult.
        """
        start_time = time.perf_counter()

        with tempfile.TemporaryDirectory(prefix="devteam_sandbox_") as temp_dir:
            solution_path = os.path.join(temp_dir, "solution.py")
            test_path = os.path.join(temp_dir, "test_solution.py")

            with open(solution_path, "w", encoding="utf-8") as f:
                f.write(solution_code)

            with open(test_path, "w", encoding="utf-8") as f:
                f.write(test_code)

            # Ensure temp_dir is on PYTHONPATH
            env = os.environ.copy()
            python_path = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = f"{temp_dir}{os.pathsep}{python_path}"

            # Pytest command
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                "-v",
                "--tb=short",
                "-W",
                "ignore",
                "test_solution.py"
            ]

            try:
                proc = subprocess.run(
                    cmd,
                    cwd=temp_dir,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=self.timeout_seconds
                )
                duration = time.perf_counter() - start_time
                stdout = proc.stdout
                stderr = proc.stderr
                exit_code = proc.returncode

            except subprocess.TimeoutExpired as exc:
                duration = time.perf_counter() - start_time
                stdout = exc.stdout if exc.stdout else ""
                stderr = f"Execution timed out after {self.timeout_seconds} seconds."
                return TestResult(
                    exit_code=-1,
                    passed_count=0,
                    failed_count=1,
                    total_count=1,
                    duration_seconds=duration,
                    stdout=stdout,
                    stderr=stderr,
                    error_summary="TimeoutExpired: Test execution exceeded time limit.",
                    traceback=stderr,
                    is_success=False
                )
            except Exception as e:
                duration = time.perf_counter() - start_time
                return TestResult(
                    exit_code=-2,
                    passed_count=0,
                    failed_count=1,
                    total_count=1,
                    duration_seconds=duration,
                    stdout="",
                    stderr=str(e),
                    error_summary=f"Subprocess invocation failure: {str(e)}",
                    traceback=str(e),
                    is_success=False
                )

        # Parse test metrics from stdout
        passed, failed, total = self._parse_pytest_counts(stdout)
        error_summary, tb_text = self._extract_traceback_and_summary(stdout, stderr)

        is_success = (exit_code == 0 and failed == 0 and (passed > 0 or total > 0))

        return TestResult(
            exit_code=exit_code,
            passed_count=passed,
            failed_count=failed,
            total_count=total if total > 0 else (passed + failed),
            duration_seconds=round(duration, 3),
            stdout=stdout,
            stderr=stderr,
            error_summary=error_summary,
            traceback=tb_text,
            is_success=is_success
        )

    def _parse_pytest_counts(self, stdout: str) -> tuple[int, int, int]:
        """Extracts passed, failed, and total counts from pytest output."""
        passed = 0
        failed = 0
        total = 0

        # Match e.g. "== 8 passed in 0.05s ==" or "== 1 failed, 7 passed in 0.12s =="
        passed_match = re.search(r'(\d+)\s+passed', stdout)
        if passed_match:
            passed = int(passed_match.group(1))

        failed_match = re.search(r'(\d+)\s+failed', stdout)
        if failed_match:
            failed = int(failed_match.group(1))

        error_match = re.search(r'(\d+)\s+error', stdout)
        if error_match:
            failed += int(error_match.group(1))

        total = passed + failed
        return passed, failed, total

    def _extract_traceback_and_summary(self, stdout: str, stderr: str) -> tuple[str, str]:
        """Extracts key traceback segment and failure summary."""
        combined = stdout + "\n" + stderr
        traceback_lines = []
        capturing = False
        error_summary = ""

        for line in combined.splitlines():
            if "FAILURES" in line or "ERRORS" in line or "Traceback (most recent call last):" in line:
                capturing = True
            if capturing:
                traceback_lines.append(line)
            if re.search(r'^(AssertionError|TypeError|ValueError|KeyError|AttributeError|Exception):', line):
                error_summary = line.strip()

        if not error_summary and traceback_lines:
            for l in reversed(traceback_lines):
                if l.startswith("E   ") or "Error" in l:
                    error_summary = l.strip()
                    break

        tb_text = "\n".join(traceback_lines) if traceback_lines else (stderr or stdout)
        if not error_summary and "failed" in stdout:
            error_summary = "Test assertions or execution failed. See traceback."

        return error_summary, tb_text
