from .syntax_checker import SyntaxChecker
from .logic_similarity import LogicSimilarity
from .code_runner import CodeRunner
from typing import List, Dict, Any

class PartialGrader:
    @staticmethod
    def grade(
        student_code: str, 
        reference_code: str, 
        test_cases: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Grades the student code using partial marking heuristics.
        """
        # 1. Syntax Check
        syntax_res = SyntaxChecker.check_syntax(student_code)
        
        # 2. Logic Similarity Check
        similarity_score = LogicSimilarity.calculate_similarity(student_code, reference_code)
        attempt_detected = LogicSimilarity.detect_attempt(student_code)
        
        # 3. Execution (if no critical syntax error, or if we can run it)
        # Even if there's a syntax error, we might try to run it if we're not sure
        # but usually syntax error = execution failure.
        execution_res = CodeRunner.run_test_cases(student_code, test_cases)
        
        # 4. Scoring Logic
        total_tc = execution_res["total_testcases"]
        passed_tc = execution_res["passed_testcases"]
        
        score = 0
        status = "failed"
        message = ""
        
        if total_tc > 0 and passed_tc == total_tc:
            score = 100
            status = "accepted"
            message = "All test cases passed."
        elif total_tc > 0 and passed_tc > 0:
            # Most cases pass -> 70%
            # (Heuristic: linearly scale between 20 and 70, or just hardcoded bands as requested)
            if passed_tc / total_tc >= 0.5:
                score = 70
                message = f"Passed {passed_tc}/{total_tc} test cases."
            else:
                score = 30 # Some passed
                message = f"Passed {passed_tc}/{total_tc} test cases."
        elif not syntax_res["valid"]:
            # Syntax error but logic detected
            if similarity_score >= 50:
                score = 60
                message = "Logic is mostly correct but there is a syntax error."
            elif similarity_score >= 30:
                score = 40
                message = "Some logical structure detected but contains syntax errors."
            else:
                score = 20
                message = "Attempt detected but logic is incorrect and code has syntax errors."
        elif attempt_detected:
            if similarity_score >= 40:
                score = 40
                message = "Logic partially matches but results are incorrect."
            else:
                score = 20
                message = "Attempt detected but logic is significantly different from expected."
        else:
            score = 0
            message = "Empty or unrelated code."

        return {
            "status": "partial" if score < 100 and score > 0 else ("accepted" if score == 100 else "failed"),
            "syntax_error": not syntax_res["valid"],
            "syntax_error_details": syntax_res if not syntax_res["valid"] else None,
            "logic_similarity": similarity_score,
            "logic_detected": similarity_score > 30 or attempt_detected,
            "passed_testcases": passed_tc,
            "total_testcases": total_tc,
            "score": score,
            "message": message
        }
