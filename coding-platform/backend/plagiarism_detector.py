import ast
import difflib
from typing import List, Dict, Any

class PlagiarismDetector:
    @staticmethod
    def tokenize_code(code: str) -> List[str]:
        """Returns a list of AST node type names as tokens, ignoring code-specific values."""
        try:
            tree = ast.parse(code)
            tokens = []
            for node in ast.walk(tree):
                tokens.append(type(node).__name__)
            return tokens
        except SyntaxError:
            return []

    @staticmethod
    def get_ast_structure(code: str) -> str:
        """Returns a simplified string representation of the AST structure for comparison."""
        try:
            tree = ast.parse(code)
            # We don't modify the tree because it's slow. We use ast.dump which is already quite structural.
            # To be even more robust, we could strip literals but ast.dump(tree, annotate_fields=False) is a good start.
            return ast.dump(tree, annotate_fields=False)
        except SyntaxError:
            return ""

    @staticmethod
    def get_control_flow_fingerprint(code: str) -> List[str]:
        """Captures the nesting and sequence of branching/looping nodes."""
        try:
            tree = ast.parse(code)
            
            class CFGVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.fp = []
                    self.depth = 0

                def generic_visit(self, node):
                    branch_nodes = (ast.If, ast.For, ast.While, ast.Try, ast.FunctionDef, ast.With)
                    is_branch = isinstance(node, branch_nodes)
                    if is_branch:
                        self.fp.append(f"{self.depth}_{type(node).__name__}")
                        self.depth += 1
                    super().generic_visit(node)
                    if is_branch:
                        self.depth -= 1
            
            visitor = CFGVisitor()
            visitor.visit(tree)
            return visitor.fp
        except SyntaxError:
            return []

    @classmethod
    def calculate_similarity(cls, code1: str, code2: str) -> Dict[str, float]:
        """
        Calculates similarity using weighted metrics:
        0.4 Token Similarity
        0.4 AST Structure Similarity
        0.2 Control Flow Similarity
        
        Returns a breakdown of scores.
        """
        if not code1.strip() or not code2.strip():
            return {"total_similarity": 0, "token_similarity": 0, "ast_similarity": 0, "cf_similarity": 0}

        # 1. Token Similarity (Intersection over Union approach or sequence matching)
        tokens1 = cls.tokenize_code(code1)
        tokens2 = cls.tokenize_code(code2)
        token_sim = 0.0
        if tokens1 and tokens2:
            token_sim = difflib.SequenceMatcher(None, tokens1, tokens2).ratio()
        
        # 2. AST Structure Similarity
        ast1 = cls.get_ast_structure(code1)
        ast2 = cls.get_ast_structure(code2)
        ast_sim = 0.0
        if ast1 and ast2:
            # difflib can be slow on very large strings, but for student code it's usually fine
            ast_sim = difflib.SequenceMatcher(None, ast1, ast2).ratio()

        # 3. Control Flow Similarity
        cf1 = cls.get_control_flow_fingerprint(code1)
        cf2 = cls.get_control_flow_fingerprint(code2)
        cf_sim = 0.0
        if cf1 and cf2:
            cf_sim = difflib.SequenceMatcher(None, cf1, cf2).ratio()
        elif not cf1 and not cf2:
             # Both have no logic nodes (e.g. empty or just prints)
             cf_sim = 1.0 if (tokens1 and tokens2) else 0.0
        
        total_score = (0.4 * token_sim) + (0.4 * ast_sim) + (0.2 * cf_sim)
        
        return {
            "total_similarity": round(total_score * 100, 2),
            "token_similarity": round(token_sim * 100, 2),
            "ast_similarity": round(ast_sim * 100, 2),
            "cf_similarity": round(cf_sim * 100, 2)
        }
