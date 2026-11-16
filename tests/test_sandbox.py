"""
Unit tests for DevTeam AI Sandbox Execution Engine and AST Analyzer.
"""

import pytest
from devteam_ai.sandbox.executor import SandboxExecutor
from devteam_ai.sandbox.ast_analyzer import analyze_code_ast, correlate_traceback_with_ast


def test_sandbox_passing_code():
    executor = SandboxExecutor(timeout_seconds=10.0)
    solution = """
def add(a: int, b: int) -> int:
    return a + b
"""
    test_code = """
from solution import add

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
"""
    result = executor.execute(solution, test_code)
    assert result.is_success is True
    assert result.exit_code == 0
    assert result.passed_count == 1
    assert result.failed_count == 0


def test_sandbox_failing_code():
    executor = SandboxExecutor(timeout_seconds=10.0)
    solution = """
def divide(a: int, b: int) -> float:
    return a / b
"""
    test_code = """
import pytest
from solution import divide

def test_divide_by_zero():
    # Intentionally wrong assertion
    assert divide(10, 0) == 0
"""
    result = executor.execute(solution, test_code)
    assert result.is_success is False
    assert result.exit_code != 0
    assert result.failed_count >= 1
    assert "ZeroDivisionError" in result.stdout or "ZeroDivisionError" in result.stderr or "ZeroDivisionError" in result.traceback


def test_sandbox_timeout():
    executor = SandboxExecutor(timeout_seconds=1.0)
    solution = """
import time
def infinite_loop():
    while True:
        time.sleep(0.1)
"""
    test_code = """
from solution import infinite_loop
def test_timeout():
    infinite_loop()
"""
    result = executor.execute(solution, test_code)
    assert result.is_success is False
    assert result.exit_code == -1
    assert "timed out" in result.stderr.lower()


def test_ast_analysis():
    code = """
class MyCalculator:
    '''A simple calculator class.'''
    def multiply(self, a: int, b: int) -> int:
        '''Multiplies two numbers.'''
        return a * b
"""
    res = analyze_code_ast(code)
    assert res.is_valid is True
    assert "MyCalculator" in res.classes
    assert "multiply" in res.functions
    assert res.docstring_count == 2


def test_ast_syntax_error():
    broken_code = "def broken(:\n    pass"
    res = analyze_code_ast(broken_code)
    assert res.is_valid is False
    assert "SyntaxError" in res.error
