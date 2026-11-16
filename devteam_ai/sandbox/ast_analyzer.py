"""
AST Analyzer: Inspects Python source code using the standard 'ast' module.
Performs syntax verification, AST decomposition, and traceback correlation.
"""

import ast
from typing import Dict, List, Any, Optional


class ASTAnalysisResult:
    def __init__(self, is_valid: bool, error: Optional[str] = None):
        self.is_valid = is_valid
        self.error = error
        self.classes: List[str] = []
        self.functions: List[str] = []
        self.has_type_annotations: bool = True
        self.docstring_count: int = 0
        self.ast_tree: Optional[ast.AST] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "error": self.error,
            "classes": self.classes,
            "functions": self.functions,
            "has_type_annotations": self.has_type_annotations,
            "docstring_count": self.docstring_count,
        }


def analyze_code_ast(code_str: str) -> ASTAnalysisResult:
    """Parses code into an AST and extracts structural signatures and docstrings."""
    try:
        tree = ast.parse(code_str)
    except SyntaxError as e:
        return ASTAnalysisResult(is_valid=False, error=f"SyntaxError at line {e.lineno}, col {e.offset}: {e.msg}")
    except Exception as e:
        return ASTAnalysisResult(is_valid=False, error=str(e))

    result = ASTAnalysisResult(is_valid=True)
    result.ast_tree = tree

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            result.classes.append(node.name)
            if ast.get_docstring(node):
                result.docstring_count += 1
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result.functions.append(node.name)
            if ast.get_docstring(node):
                result.docstring_count += 1
            # Check for type annotations on arguments and return type
            if node.returns is None and node.name != "__init__":
                result.has_type_annotations = False
            for arg in node.args.args:
                if arg.arg != "self" and arg.arg != "cls" and arg.annotation is None:
                    result.has_type_annotations = False

    return result


def correlate_traceback_with_ast(code_str: str, traceback_str: str) -> Dict[str, Any]:
    """
    Correlates runtime traceback line numbers with AST function/method scopes
    to pinpoint exact faulty constructs for the Reviewer & Healer agent.
    """
    import re
    analysis = analyze_code_ast(code_str)
    if not analysis.is_valid or not analysis.ast_tree:
        return {
            "fault_location": "Syntax / Unparseable Code",
            "faulty_function": None,
            "line_number": None,
            "details": analysis.error
        }

    # Extract line numbers from traceback referring to solution.py
    line_matches = re.findall(r'solution\.py", line (\d+)', traceback_str)
    faulty_line = int(line_matches[-1]) if line_matches else None

    faulty_function = None
    faulty_class = None

    if faulty_line:
        # Traverse AST to find enclosing class / function
        for node in ast.walk(analysis.ast_tree):
            if isinstance(node, ast.ClassDef):
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    if node.lineno <= faulty_line <= (node.end_lineno or 99999):
                        faulty_class = node.name
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    if node.lineno <= faulty_line <= (node.end_lineno or 99999):
                        faulty_function = node.name

    return {
        "faulty_line": faulty_line,
        "faulty_class": faulty_class,
        "faulty_function": faulty_function,
        "identified_classes": analysis.classes,
        "identified_functions": analysis.functions,
    }
