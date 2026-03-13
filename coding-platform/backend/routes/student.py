from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import database, models, schemas, security, execution, anti_cheat
from ..grading import submission_saver, student_dashboard as sd_helpers

router = APIRouter(
    prefix="/api/student",
    tags=['Student Actions']
)

@router.get("/problems", response_model=List[schemas.ProblemListResponse])
def get_all_problems(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    problems = db.query(models.Problem).all()
    return problems

@router.get("/problems/{problem_id}", response_model=schemas.ProblemResponse)
def get_problem_details(
    problem_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    problem = db.query(models.Problem).filter(models.Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem

@router.get("/submissions", response_model=List[schemas.SubmissionResponse])
def get_student_submissions(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    submissions = db.query(models.Submission).filter(models.Submission.user_id == current_user.id).all()
    return submissions

@router.get("/profile", response_model=schemas.StudentProfileResponse)
def get_student_profile(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Returns the student's progress:
    - List of attempted problems with best score per problem
    - Total accumulated marks
    """
    attempted = sd_helpers.get_attempted_problems(current_user.id, db)
    total = sd_helpers.get_total_marks(current_user.id, db)
    return {
        "user_id": current_user.id,
        "name": current_user.name,
        "university_id": current_user.university_id,
        "total_marks": total,
        "attempted_problems": attempted,
    }

@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(database.get_db)):
    from sqlalchemy import func

    users_with_accepted = db.query(
        models.User.name,
        models.User.university_id,
        func.count(models.Submission.problem_id.distinct()).label("solved_count")
    ).join(models.Submission).filter(
        models.Submission.result == "Accepted"
    ).group_by(models.User.id).order_by(func.count(models.Submission.problem_id.distinct()).desc()).all()

    return [
        {"name": u.name, "university_id": u.university_id, "solved_count": u.solved_count}
        for u in users_with_accepted
    ]

@router.post("/submit", response_model=schemas.SubmissionResult)
def submit_code(
    submission: schemas.SubmissionCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    problem = db.query(models.Problem).filter(models.Problem.id == submission.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # --- Cheat detection auto-fail ---
    if submission.cheat_detected:
        new_sub = submission_saver.save_submission(
            db=db,
            user_id=current_user.id,
            problem_id=submission.problem_id,
            language=submission.language,
            code=submission.code,
            score=0,
            status="Cheat Detected",
            passed_testcases=0,
            total_testcases=0,
            execution_time="0ms",
        )
        return schemas.SubmissionResult(
            status="Cheat Detected",
            score=0,
            passed_testcases=0,
            total_testcases=0,
            message="Automatically failed due to repeated anti-cheat violations (3 warnings exceeded).",
            execution_time="0ms",
            submission_id=new_sub.id,
        )

    # --- Evaluate the submission ---
    testcases = db.query(models.TestCase).filter(models.TestCase.problem_id == problem.id).all()

    if not testcases:
        new_sub = submission_saver.save_submission(
            db=db,
            user_id=current_user.id,
            problem_id=submission.problem_id,
            language=submission.language,
            code=submission.code,
            score=100,
            status="Accepted",
            passed_testcases=0,
            total_testcases=0,
            execution_time="0ms",
        )
        return schemas.SubmissionResult(
            status="Accepted",
            score=100,
            passed_testcases=0,
            total_testcases=0,
            message="No test cases to run. Full marks awarded by default.",
            execution_time="0ms",
            submission_id=new_sub.id,
        )

    # Use the execution engine (handles partial grading internally)
    result_data = execution.evaluate_submission(
        submission.code,
        submission.language,
        testcases,
        reference_code=problem.reference_solution
    )

    score = result_data.get("score", 0)
    exec_time = result_data.get("execution_time", "0ms")
    raw_status = result_data.get("result", "Wrong Answer")
    message = result_data.get("error_details", "")

    # Derive passed/total from result_data (partial grader fills these)
    passed_tc = result_data.get("passed_testcases", 0) or 0
    total_tc = result_data.get("total_testcases", len(testcases)) or len(testcases)

    # If all passed (score==100) but passed_tc not set, fill it
    if score == 100 and passed_tc == 0:
        passed_tc = total_tc = len(testcases)

    # Normalise status label
    if score == 100:
        status_label = "Accepted"
        message = message or "All test cases passed. Full marks awarded."
    elif score > 0:
        status_label = "Partial"
        message = message or f"Partial marks awarded because logic is mostly correct."
    else:
        status_label = raw_status if raw_status else "Wrong Answer"
        message = message or "No test cases passed."

    # --- Plagiarism check (Python only, accepted submissions) ---
    sim_score = 0
    if submission.language == "python" and score == 100:
        other_subs = db.query(models.Submission).filter(
            models.Submission.problem_id == problem.id,
            models.Submission.user_id != current_user.id,
            models.Submission.result == "Accepted",
            models.Submission.language == "python"
        ).all()
        for other in other_subs:
            s = anti_cheat.calculate_similarity(submission.code, other.code)
            if s > sim_score:
                sim_score = s

    # --- Persist submission ---
    new_sub = submission_saver.save_submission(
        db=db,
        user_id=current_user.id,
        problem_id=submission.problem_id,
        language=submission.language,
        code=submission.code,
        score=score,
        status=status_label,
        passed_testcases=passed_tc,
        total_testcases=total_tc,
        execution_time=exec_time,
        similarity_score=sim_score if sim_score > 0 else None,
    )

    return schemas.SubmissionResult(
        status="evaluated",
        score=score,
        passed_testcases=passed_tc,
        total_testcases=total_tc,
        message=message,
        execution_time=exec_time,
        submission_id=new_sub.id,
    )
