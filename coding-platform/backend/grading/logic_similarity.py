from .ast_analyzer import ASTAnalyzer
import ast
from typing import Dict, Any

class LogicSimilarity:
    @staticmethod
    def calculate_similarity(student_code: str, reference_code: str) -> float:
        """
        Calculates a similarity score between 0 and 100 between two code snippets.
        """
        try:
            student_tree = ast.parse(student_code)
            reference_tree = ast.parse(reference_code)
        except SyntaxError:
            return 0.0

        student_features = ASTAnalyzer.get_logic_features(student_tree)
        reference_features = ASTAnalyzer.get_logic_features(reference_tree)

        score = 0.0
        total_weight = 0.0

        # Feature weights
        weights = {
            "loops": 30,
            "conditions": 30,
            "functions": 20,
            "returns": 10,
            "imports": 10
        }

        for feature, weight in weights.items():
            s_val = student_features.get(feature, 0)
            r_val = reference_features.get(feature, 0)
            
            if isinstance(s_val, list):
                s_val = len(s_val)
                r_val = len(r_val)
            
            if r_val == 0:
                if s_val == 0:
                    score += weight
                total_weight += weight
                continue

            # Similarity for this feature
            feature_sim = max(0, 1 - abs(s_val - r_val) / max(s_val, r_val))
            score += feature_sim * weight
            total_weight += weight

        similarity = (score / total_weight) * 100
        return round(similarity, 2)

    @staticmethod
    def detect_attempt(student_code: str) -> bool:
        """
        Heuristic to detect if any meaningful attempt was made.
        """
        try:
            tree = ast.parse(student_code)
            features = ASTAnalyzer.get_logic_features(tree)
            
            # If there's at least one loop, condition, function, or non-trivial assignment
            if features["loops"] > 0 or features["conditions"] > 0 or features["functions"] > 0:
                return True
            
            # Or if there's more than just simple imports/print
            nodes = [n for n in ast.walk(tree) if not isinstance(n, (ast.Module, ast.Load, ast.Store, ast.Name, ast.Constant))]
            return len(nodes) > 5
        except SyntaxError:
            # If it doesn't parse, we might look for keywords
            meaningful_keywords = ["def ", "for ", "while ", "if ", "else:", "elif ", "return "]
            for kw in meaningful_keywords:
                if kw in student_code:
                    return True
            return len(student_code.strip()) > 20
        except Exception:
            return False
