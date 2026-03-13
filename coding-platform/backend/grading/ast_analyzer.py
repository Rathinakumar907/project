import ast
from typing import List, Set, Dict, Any

class ASTAnalyzer:
    @staticmethod
    def normalize_ast(tree: ast.AST) -> List[str]:
        """
        Walks the AST and returns a list of node types to represent structure.
        Filters out docstrings and non-logical nodes.
        """
        nodes = []
        for node in ast.walk(tree):
            # Skip docstrings
            if isinstance(node, ast.Expr) and isinstance(node.value, (ast.Str, ast.Constant)):
                continue
            
            # Record node type
            node_type = type(node).__name__
            nodes.append(node_type)
            
        return nodes

    @staticmethod
    def get_logic_features(tree: ast.AST) -> Dict[str, Any]:
        """
        Extracts high-level logical features from the AST.
        """
        features: Dict[str, Any] = {
            "loops": 0,
            "conditions": 0,
            "functions": 0,
            "returns": 0,
            "imports": set(),
            "variable_names": set()
        }

        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                features["loops"] = features["loops"] + 1
            elif isinstance(node, (ast.If, ast.IfExp)):
                features["conditions"] = features["conditions"] + 1
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                features["functions"] = features["functions"] + 1
            elif isinstance(node, ast.Return):
                features["returns"] = features["returns"] + 1
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    features["imports"].add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    features["imports"].add(node.module)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                features["variable_names"].add(node.id)

        features["imports"] = list(features["imports"])
        features["variable_names"] = list(features["variable_names"])
        return features

    @staticmethod
    def get_canonical_structure(tree: ast.AST) -> str:
        """
        Produces a simplified string representation of the code structure.
        """
        structure = []
        
        def _visit(node, depth=0):
            indent = "  " * depth
            node_type = type(node).__name__
            
            # Focus on control flow
            important_nodes = (
                ast.FunctionDef, ast.For, ast.While, ast.If, 
                ast.Try, ast.With, ast.Return, ast.Assign
            )
            
            if isinstance(node, important_nodes):
                structure.append(f"{indent}{node_type}")
                for child in ast.iter_child_nodes(node):
                    _visit(child, depth + 1)
            else:
                for child in ast.iter_child_nodes(node):
                    _visit(child, depth)

        _visit(tree)
        return "\n".join(structure)
