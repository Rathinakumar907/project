from .syntax_checker import SyntaxChecker
from .logic_similarity import LogicSimilarity
from .code_runner import CodeRunner
from typing import List, Dict, Any

class PartialGrader:
    @staticmethod
    def grade(
        student_code: str, 
        reference_code: str, 
        test_cases: List[Dict[str, Any]],
        total_marks: int = 100
    ) -> Dict[str, Any]:
        """
        Grades the student code using partial marking based on test cases.
        """
        # 1. Syntax Check
        syntax_res = SyntaxChecker.check_syntax(student_code)
        
        # 2. Logic Similarity Check (Metadata)
        similarity_score = LogicSimilarity.calculate_similarity(student_code, reference_code)
        attempt_detected = LogicSimilarity.detect_attempt(student_code)
        
        # 3. Execution (Passed indices are now returned by CodeRunner)
        execution_res = CodeRunner.run_test_cases(student_code, test_cases)
        
        # 4. Scoring Logic (Weighted Test Cases)
        total_tc = execution_res["total_testcases"]
        passed_tc = execution_res["passed_testcases"]
        passed_indices = execution_res.get("passed_indices", [])
        
        total_weight = sum(tc.get("weight", 1) for tc in test_cases) or 1
        passed_weight = sum(test_cases[i].get("weight", 1) for i in passed_indices)

        # Calculate score: (passed_weight / total_weight) * total_marks
        score = int((passed_weight / total_weight) * total_marks) if total_tc > 0 else 0
        
        status = "accepted" if passed_tc == total_tc and total_tc > 0 else ("partial" if passed_tc > 0 or attempt_detected else "failed")
        
        if score == total_marks and total_tc > 0:
            message = "All test cases passed."
        elif score > 0:
            message = f"Passed {passed_tc}/{total_tc} test cases."
        elif not syntax_res["valid"]:
            message = "Syntax error detected."
        elif attempt_detected:
            message = "Code logic attempt detected but test cases failed."
        else:
            message = "No test cases passed."

        return {
            "status": status,
            "result": status.title(), # Compatibility
            "syntax_error": not syntax_res["valid"],
            "syntax_error_details": syntax_res if not syntax_res["valid"] else None,
            "logic_similarity": similarity_score,
            "logic_detected": similarity_score > 30 or attempt_detected,
            "passed_testcases": passed_tc,
            "total_testcases": total_tc,
            "score": score,
            "message": message
        }
