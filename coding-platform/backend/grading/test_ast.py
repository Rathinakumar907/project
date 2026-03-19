import ast
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from ast_analyzer import ASTAnalyzer

sample_code = """
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
"""

print("Running AST Analyzer on sample code:\n")
print(sample_code)

tree = ast.parse(sample_code)

print("Logic Features:")
print(ASTAnalyzer.get_logic_features(tree))

print("\nCanonical Structure:")
print(ASTAnalyzer.get_canonical_structure(tree))

print("\nNormalized AST:")
print(ASTAnalyzer.normalize_ast(tree))
