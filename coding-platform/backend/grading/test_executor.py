"""
test_executor.py
----------------
Runs every test case individually and returns a structured result
including per-case pass/fail, total counts, and max execution time.

Used as the fallback executor for non-Python languages or when no
reference solution is provided.
"""

import time
from typing import List, Dict, Any
from .code_runner import CodeRunner


def execute_all_testcases(
    code: str,
    language: str,
    testcases: List[Any],   # list of TestCase ORM objects or dicts
) -> Dict[str, Any]:
    """
    Runs every test case with the submitted code.

    Returns:
        {
          "passed_testcases": int,
          "total_testcases": int,
          "max_execution_time_ms": int,
          "first_failure_index": int | None,
          "first_error_detail": str | None,
          "results": [ {"index":1, "passed":True, "actual":"", "expected":""}, ... ]
        }
    """
    # Normalise testcases to dicts
    tc_list = []
    for tc in testcases:
        if hasattr(tc, "input_data"):
            tc_list.append({"input": tc.input_data, "expected": tc.expected_output})
        else:
            tc_list.append(tc)

    total = len(tc_list)
    passed = 0
    results = []
    max_time = 0
    first_failure_index = None
    first_error_detail = None

    for idx, tc in enumerate(tc_list):
        # Use CodeRunner for per-testcase execution timing
        start = time.time()
        run_result = CodeRunner.run_test_cases(code, [tc])
        elapsed_ms = int((time.time() - start) * 1000)
        max_time = max(max_time, elapsed_ms)

        tc_passed = run_result["passed_testcases"] == 1
        if tc_passed:
            passed += 1
        else:
            if first_failure_index is None:
                first_failure_index = idx + 1
                # Gather the error message if available
                failed_cases = run_result.get("failed_cases", [])
                if failed_cases:
                    fc = failed_cases[0]
                    first_error_detail = (
                        f"Expected: {str(fc.get('expected',''))[:80]} | "
                        f"Got: {str(fc.get('actual',''))[:80]}"
                    )

        results.append({
            "index": idx + 1,
            "passed": tc_passed,
            "expected": tc["expected"],
            "actual": run_result.get("actual_outputs", [""])[0] if run_result.get("actual_outputs") else "",
        })

    return {
        "passed_testcases": passed,
        "total_testcases": total,
        "max_execution_time_ms": max_time,
        "first_failure_index": first_failure_index,
        "first_error_detail": first_error_detail,
        "results": results,
    }
