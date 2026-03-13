from .sandbox_executor import SandboxExecutor
from typing import List, Dict, Any

class CodeRunner:
    @staticmethod
    def run_test_cases(code: str, test_cases: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Runs the code against a set of test cases and returns results.
        test_cases: List of {"input": str, "expected": str}
        """
        results = []
        passed_count = 0
        total_count = len(test_cases)

        for tc in test_cases:
            input_data = tc.get("input", "")
            expected_output = tc.get("expected", "").strip()
            
            run_result = SandboxExecutor.run_code(code, input_data)
            
            actual_output = run_result["stdout"].strip()
            is_passed = (actual_output == expected_output and run_result["exit_code"] == 0)
            
            if is_passed:
                passed_count += 1
            
            results.append({
                "input": input_data,
                "expected": expected_output,
                "actual": actual_output,
                "passed": is_passed,
                "error": run_result["stderr"],
                "timed_out": run_result["timed_out"]
            })

        return {
            "passed_testcases": passed_count,
            "total_testcases": total_count,
            "results": results,
            "all_passed": passed_count == total_count if total_count > 0 else False
        }
