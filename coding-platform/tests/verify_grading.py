import sys
import os

# Add parent directory to sys.path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.grading.partial_grader import PartialGrader

def run_test_cases():
    reference_code = """
def solve(n):
    result = 0
    for i in range(n):
        if i % 2 == 0:
            result += i
    return result
"""

    testcases = [
        {"input": "10", "expected": "20"},
        {"input": "5", "expected": "6"}
    ]

    scenarios = [
        {
            "name": "Perfect Solution",
            "code": """
def solve(n):
    res = 0
    for x in range(n):
        if x % 2 == 0:
            res += x
    return res

import sys
input_val = int(sys.stdin.read().strip())
print(solve(input_val))
"""
        },
        {
            "name": "Syntax Error but Correct Logic",
            "code": """
def solve(n):
    res = 0
    for x in range(n):
        if x % 2 == 0 # MISSING COLON
            res += x
    return res
"""
        },
        {
            "name": "Incorrect Logic (No loops)",
            "code": "def solve(n): return n"
        },
        {
            "name": "Empty Code",
            "code": ""
        }
    ]

    for scenario in scenarios:
        print(f"\n--- Scenario: {scenario['name']} ---")
        result = PartialGrader.grade(scenario['code'], reference_code, testcases)
        print(f"Status: {result['status']}")
        print(f"Score: {result['score']}")
        print(f"Message: {result['message']}")
        if result['syntax_error']:
            print(f"Syntax Error Detected: {result['syntax_error_details']['error']} at line {result['syntax_error_details']['line']}")

if __name__ == "__main__":
    run_test_cases()
