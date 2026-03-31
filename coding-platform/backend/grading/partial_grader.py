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

        # Strict Per-Question Grading Logic
        ratio = (passed_weight / total_weight) if total_weight > 0 else 0
        
        if ratio == 1.0 and total_tc > 0 and syntax_res["valid"]:
            # 100% Correct
            score = total_marks
            status = "accepted"
            message = "All test cases passed."
        elif ratio >= 0.8 or (similarity_score >= 80 and not syntax_res["valid"]):
            # 80%: Logic is correct but code is incomplete
            score = int(total_marks * 0.80)
            status = "partial"
            message = "Logic is correct but code is incomplete."
        elif ratio >= 0.5 or similarity_score >= 60:
            # 60%: Partially correct
            score = int(total_marks * 0.60)
            status = "partial"
            message = "Code or theoretical answer is partially correct."
        elif ratio > 0 or attempt_detected or similarity_score >= 30:
            # 40%: Minimally correct
            score = int(total_marks * 0.40)
            status = "partial"
            message = "Answer is minimally correct."
        else:
            # 15%: Incorrect / No valid logic
            score = int(total_marks * 0.15)
            status = "failed"
            message = "No valid logic is present."

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
