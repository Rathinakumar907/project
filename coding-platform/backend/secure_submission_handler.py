from sqlalchemy.orm import Session
from . import models, schemas
from .plagiarism_detector import PlagiarismDetector
from .execution import evaluate_submission
from .grading import submission_saver
from datetime import datetime

class SecureSubmissionHandler:
    @staticmethod
    def handle_submission(
        db: Session,
        user: models.User,
        submission_data: schemas.SubmissionCreate,
        exam_session: models.ExamSession
    ) -> schemas.SubmissionResult:
        """
        Orchestrates the secure submission flow:
        1. Validates testcases
        2. Executes in sandbox (with partial grading)
        3. Runs advanced plagiarism detection
        4. Persists results and flags suspicious similarity
        """
        # 1. Fetch problem and testcases
        problem = db.query(models.Problem).filter(models.Problem.id == submission_data.problem_id).first()
        testcases = db.query(models.TestCase).filter(models.TestCase.problem_id == problem.id).all()
        
        # 2. Run code inside sandbox (Evaluate)
        # Handles partial grading internally for Python if reference_code is present
        result_data = evaluate_submission(
            submission_data.code,
            submission_data.language,
            testcases,
            total_marks=problem.total_marks,
            reference_code=problem.reference_solution
        )
        
        # 3. Advanced Plagiarism Check
        # Check against other submissions for the same problem
        sim_data = {"total_similarity": 0, "token_similarity": 0, "ast_similarity": 0, "cf_similarity": 0}
        potential_match_id = None
        
        # Only check plagiarism for Python and non-zero scores (meaningful logic)
        if submission_data.language == "python" and result_data["score"] > 0:
            others = db.query(models.Submission).filter(
                models.Submission.problem_id == problem.id,
                models.Submission.user_id != user.id,
                models.Submission.score > 0,
                models.Submission.language == "python"
            ).all()
            
            max_sim = 0
            for other in others:
                s = PlagiarismDetector.calculate_similarity(submission_data.code, other.code)
                if s["total_similarity"] > max_sim:
                    max_sim = s["total_similarity"]
                    sim_data = s
                    potential_match_id = other.id
                    
        # 4. Save Submission
        new_sub = submission_saver.save_submission(
            db=db,
            user_id=user.id,
            problem_id=submission_data.problem_id,
            language=submission_data.language,
            code=submission_data.code,
            score=result_data["score"],
            status=result_data["result"],
            passed_testcases=result_data["passed_testcases"],
            total_testcases=result_data["total_testcases"],
            execution_time=result_data["execution_time"],
            similarity_score=int(sim_data["total_similarity"]),
            exam_session_id=exam_session.id
        )

        # 5. Log Plagiarism Flag if threshold exceeded (e.g., > 80%)
        if sim_data["total_similarity"] > 80 and potential_match_id:
            flag = models.PlagiarismFlag(
                submission_1_id=new_sub.id,
                submission_2_id=potential_match_id,
                total_similarity=int(sim_data["total_similarity"]),
                token_similarity=int(sim_data["token_similarity"]),
                ast_similarity=int(sim_data["ast_similarity"]),
                control_flow_similarity=int(sim_data["cf_similarity"]),
                status="potential"
            )
            db.add(flag)
            db.commit()

        # Update session status if they passed perfectly? 
        # (Optional, but let's keep it active for retries unless professor ends it)

        # --- CHEATING DETECTION HEURISTICS ---
        cheating_reason = None
        
        # Heuristic 1: High Similarity
        if sim_data["total_similarity"] > 80:
            cheating_reason = "High Similarity"
            
        # Heuristic 2: Hardcoded outputs (checking if large literal output is in code)
        if not cheating_reason and result_data["score"] > 0:
            for tc in testcases:
                if len(tc.expected_output.strip()) > 5 and tc.expected_output.strip() in submission_data.code:
                    cheating_reason = "Hardcoding Suspected"
                    break
                    
        # Heuristic 3: Too fast submissions (e.g. submitted < 10 seconds from session start but code > 100 chars)
        time_since_start = (datetime.utcnow() - exam_session.start_time).total_seconds()
        if not cheating_reason and time_since_start < 10 and len(submission_data.code) > 100:
            cheating_reason = "Too fast submission"
            
        # Heuristic 4: Multiple rapid submissions (< 5 seconds between consecutive submits)
        if not cheating_reason:
            last_sub = db.query(models.Submission).filter(
                models.Submission.user_id == user.id,
                models.Submission.problem_id == submission_data.problem_id,
                models.Submission.id != new_sub.id
            ).order_by(models.Submission.created_at.desc()).first()
            if last_sub and (datetime.utcnow() - last_sub.created_at).total_seconds() < 5:
                cheating_reason = "Multiple rapid submissions"

        if cheating_reason:
            cheating_log = models.CheatingLog(
                user_id=user.id,
                problem_id=submission_data.problem_id,
                reason=cheating_reason,
                similarity_score=int(sim_data["total_similarity"]) if sim_data["total_similarity"] > 0 else None,
                timestamp=datetime.utcnow()
            )
            db.add(cheating_log)
            db.commit()

        return schemas.SubmissionResult(
            status=result_data["result"],
            score=result_data["score"],
            passed_testcases=result_data["passed_testcases"],
            total_testcases=result_data["total_testcases"],
            message=result_data["error_details"],
            execution_time=result_data["execution_time"],
            submission_id=new_sub.id
        )
