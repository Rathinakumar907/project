import ast

class TokenizerVisitor(ast.NodeVisitor):
    def __init__(self):
        self.tokens = []

    def generic_visit(self, node):
        self.tokens.append(type(node).__name__)
        super().generic_visit(node)

def get_ast_tokens(code_str: str):
    try:
        tree = ast.parse(code_str)
        visitor = TokenizerVisitor()
        visitor.visit(tree)
        return visitor.tokens
    except SyntaxError:
        return []

def calculate_similarity(code1: str, code2: str) -> float:
    # Basic token comparison using AST structure for Python
    tokens1 = get_ast_tokens(code1)
    tokens2 = get_ast_tokens(code2)
    
    if not tokens1 or not tokens2:
        return 0.0

    # Calculate similarity using simple intersection over union or sequence matching
    import difflib
    sm = difflib.SequenceMatcher(None, tokens1, tokens2)
    return round(float(sm.ratio() * 100), 2)
