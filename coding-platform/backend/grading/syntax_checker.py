import ast
import traceback
from typing import Dict, Any, Optional

class SyntaxChecker:
    @staticmethod
    def check_syntax(code: str) -> Dict[str, Any]:
        """
        Validates Python syntax and returns detailed error information if invalid.
        """
        try:
            compile(code, "<string>", "exec")
            return {
                "valid": True,
                "error": None,
                "line": None,
                "offset": None,
                "text": None
            }
        except SyntaxError as e:
            return {
                "valid": False,
                "error": e.msg,
                "line": e.lineno,
                "offset": e.offset,
                "text": e.text.strip() if e.text else ""
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "line": None,
                "offset": None,
                "text": None
            }

    @staticmethod
    def get_ast_safely(code: str) -> Optional[ast.AST]:
        """
        Attempts to parse AST. Returns None if syntax is invalid.
        """
        try:
            return ast.parse(code)
        except SyntaxError:
            # For partial evaluation, we might want to try to fix common small errors
            # like missing colons if we were feeling adventurous, but for now
            # we just return None to signal the analyzer to use a fallback if needed.
            return None
