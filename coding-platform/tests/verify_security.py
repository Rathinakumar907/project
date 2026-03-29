import sys
import os
import re

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution import evaluate_submission, run_code_in_sandbox

class MockTestCase:
    def __init__(self, input_data, expected_output, marks_weight=1):
        self.input_data = input_data
        self.expected_output = expected_output
        self.marks_weight = marks_weight

def test_output_isolation():
    print("Testing Output Isolation (Ignoring extra prints)...")
    # Student prints debug info, then the actual answer
    code = """
import sys
x = sys.stdin.read().strip()
print("Debug: Initializing...")
print(f"Debug: Input is {x}")
print(int(x) * 2)
"""
    testcases = [MockTestCase("5", "10", 1)]
    result = evaluate_submission(code, "python", testcases)
    
    print(f"Result Result: {result['result']}")
    print(f"Error Details: {result['error_details']}")
    
    if result['result'] == "Accepted":
        print("✅ SUCCESS: Extra prints were ignored.")
    else:
        print("❌ FAILED: Extra prints were NOT ignored or execution failed.")

def test_if_else_cheating():
    print("\nTesting If-Else Cheating Detection (Separation of Sample/Hidden)...")
    # Student knows sample case (5 -> 10) but not hidden test case (10 -> 20)
    code = """
import sys
val = sys.stdin.read().strip()
if val == "5": print("10")
else: print("Wrong")
"""
    testcases = [
        MockTestCase("5", "10", 0), # Sample (visible to student)
        MockTestCase("10", "20", 5) # Hidden (used for grade)
    ]
    result = evaluate_submission(code, "python", testcases)
    
    print(f"Overall Result: {result['result']}")
    print(f"Final Score: {result['score']}")
    print(f"Passed Test Cases: {result['passed_testcases']}/{result['total_testcases']}")
    
    # Expect 1/2 test cases passed, but score 0 because hidden case failed
    if result['score'] == 0 and result['passed_testcases'] == 1:
        print("✅ SUCCESS: Cheating attempt detected (score is 0 for failed hidden case).")
    else:
        print("❌ FAILED: Cheating attempt was not handled correctly.")

def test_file_access_restriction():
    print("\nTesting File Access Restriction (Sandbox Simulation)...")
    # Attempt to read a file outside the working directory (assuming current structure)
    code = """
try:
    with open('backend/models.py', 'r') as f:
        print(f.read()[:20])
except Exception as e:
    print(f"Access Denied: {e}")
"""
    testcases = [MockTestCase("", "Access Denied", 1)]
    result = evaluate_submission(code, "python", testcases)
    
    print(f"Result: {result['result']}")
    print(f"Error Details: {result['error_details']}")
    
    # If the sandbox worked (or local fallback), 'class' from models.py should NOT be here
    if "class" not in str(result['error_details']).lower():
        print("✅ SUCCESS: File system access was restricted or obscured.")
    else:
        print("❌ FAILED: File system content leaked.")

if __name__ == "__main__":
    test_output_isolation()
    test_if_else_cheating()
    test_file_access_restriction()
