"""
score_calculator.py
-------------------
Pure-function scoring module.
Takes execution results + similarity data and returns a final score (0-100),
status string, and a human-readable message.

No external AI APIs used. All scoring is done via AST/logic heuristics.
"""

from typing import Dict, Any


def calculate_score(
    passed_testcases: int,
    total_testcases: int,
    syntax_ok: bool = True,
    logic_similarity: float = 0.0,
    attempt_detected: bool = False
) -> Dict[str, Any]:
    """
    Scoring rules:
    - All TCs pass                         → 100 (Accepted)
    - >= 50% TCs pass                      → 70  (Partial)
    - Some TCs pass (<50%)                 → proportional (min 20)
    - Syntax error + high logic similarity → 60  (Partial)
    - Syntax error + medium similarity     → 40  (Partial)
    - Syntax error + low                   → 20  (Partial)
    - No syntax error, no TCs pass, some logic → 20-40
    - Nothing                              → 0   (Failed)
    """
    score = 0
    status = "Wrong Answer"
    message = ""

    if total_testcases > 0 and passed_testcases == total_testcases:
        score = 100
        status = "Accepted"
        message = "All test cases passed. Full marks awarded."

    elif total_testcases > 0 and passed_testcases > 0:
        ratio = passed_testcases / total_testcases
        if ratio >= 0.8:
            score = 80
        elif ratio >= 0.5:
            score = int(ratio * 100)   # proportional between 50 and 79
        else:
            score = max(20, int(ratio * 60))  # at least 20 for any pass
        status = "Partial"
        message = (
            f"Passed {passed_testcases}/{total_testcases} test cases. "
            f"Partial marks awarded."
        )

    elif not syntax_ok:
        if logic_similarity >= 50:
            score = 60
            message = "Logic is mostly correct but there is a syntax error."
        elif logic_similarity >= 30:
            score = 40
            message = "Some logical structure detected but code has syntax errors."
        else:
            score = 20
            message = "Attempt detected but logic differs significantly; syntax errors present."
        status = "Partial"

    elif attempt_detected:
        if logic_similarity >= 40:
            score = 40
            message = "Logic partially matches expected solution but output is incorrect."
        else:
            score = 20
            message = "Attempt detected but logic diverges significantly from expected."
        status = "Partial"

    else:
        score = 0
        status = "Wrong Answer"
        message = "No test cases passed and no recognisable attempt detected."

    return {
        "score": score,
        "status": status,
        "message": message,
    }
