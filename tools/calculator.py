# tools/calculator.py
# Safe math evaluator using Python's AST (Abstract Syntax Tree).
# Python 3.12 compatible — uses ast.Constant instead of deprecated ast.Num.
# No eval() used — only allows whitelisted numeric operations.

import ast
import operator

# Mapping of AST operator types to actual Python operations
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,   # Unary minus, e.g. -5
    ast.UAdd: operator.pos,   # Unary plus
}


def _eval_node(node):
    """Recursively evaluate an AST node, only allowing safe numeric operations."""
    # Numeric literal (Python 3.8+ uses ast.Constant for all literals)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Non-numeric constant: {node.value!r}")

    # Binary operation: left OP right (e.g., 2 + 3)
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in ALLOWED_OPERATORS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        # Guard against division by zero
        if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
            raise ZeroDivisionError("Division by zero is undefined, Sir.")
        return ALLOWED_OPERATORS[op_type](left, right)

    # Unary operation: OP operand (e.g., -5)
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in ALLOWED_OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        operand = _eval_node(node.operand)
        return ALLOWED_OPERATORS[op_type](operand)

    raise ValueError(f"Unsupported expression type: {type(node).__name__}")


def calculate(expression: str) -> str:
    """
    Safely evaluate a math expression string and return a formatted result.
    Only numbers and arithmetic operators are permitted.
    """
    expression = expression.strip()
    try:
        # Parse the expression into an AST tree
        tree = ast.parse(expression, mode="eval")
        result = _eval_node(tree.body)

        # Format result: show integer if whole number, else float with precision
        if isinstance(result, float) and result.is_integer():
            result = int(result)

        # Format with comma separators for readability (e.g., 65,536)
        formatted = f"{result:,}" if isinstance(result, int) else f"{result:,.6g}"
        return f"That would be {formatted}, Sir."
    except ZeroDivisionError as e:
        return f"A mathematical impossibility, Sir. {e}"
    except (ValueError, SyntaxError, TypeError) as e:
        return f"I was unable to evaluate that expression, Sir. Error: {e}"
    except Exception as e:
        return f"Calculation error, Sir: {e}"
