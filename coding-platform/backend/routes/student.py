from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import database, models, schemas, security, execution, anti_cheat

router = APIRouter(
    prefix="/api/student",
    tags=['Student Actions']
)

@router.get("/problems", response_model=List[schemas.ProblemListResponse])
def get_all_problems(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    # For now, students can see all problems. Later can filter by assignment.
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
        
    # We should hide expected_output from the responses for students ideally, 
    # but for simplicity we rely on backend-only execution.
    return problem

@router.get("/submissions", response_model=List[schemas.SubmissionResponse])
def get_student_submissions(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    submissions = db.query(models.Submission).filter(models.Submission.user_id == current_user.id).all()
    return submissions

@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(database.get_db)):
    # Simple leaderboard: Count distinct accepted problems per user
    from sqlalchemy import func
    
    # Expected logic: group by user_id who have "Accepted" submissions
    # This is a simplified example
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

@router.post("/submit", response_model=schemas.SubmissionResponse)
def submit_code(
    submission: schemas.SubmissionCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    problem = db.query(models.Problem).filter(models.Problem.id == submission.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    if submission.cheat_detected:
        # User surpassed cheat warning limit - Auto fail
        result_data = {
            "result": "Failed (Cheat Detected)",
            "execution_time": "0ms",
            "failed_testcase": None,
            "error_details": "Automatically failed due to repeated anti-cheat violations (3 warnings exceeded)."
        }
    else:
        testcases = db.query(models.TestCase).filter(models.TestCase.problem_id == problem.id).all()
        if not testcases:
            # Avoid crashing if problem has no testcases
            result_data = {
                "result": "Accepted", 
                "execution_time": "0ms",
                "failed_testcase": None,
                "error_details": "No testcases to run"
            }
        else:
            # Run code against testcases
            result_data = execution.evaluate_submission(submission.code, submission.language, testcases)
        
    # Check for Plagiarism (if language is Python)
    sim_score = 0
    if submission.language == "python" and result_data["result"] == "Accepted":
        other_submissions = db.query(models.Submission).filter(
            models.Submission.problem_id == problem.id,
            models.Submission.user_id != current_user.id,
            models.Submission.result == "Accepted",
            models.Submission.language == "python"
        ).all()
        
        for other in other_submissions:
            score = anti_cheat.calculate_similarity(submission.code, other.code)
            if score > sim_score:
                sim_score = score
                
    new_submission = models.Submission(
        user_id=current_user.id,
        problem_id=submission.problem_id,
        language=submission.language,
        code=submission.code,
        result=result_data["result"],
        execution_time=result_data["execution_time"],
        similarity_score=sim_score if sim_score > 0 else None
    )
    
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    
    return {
        "id": new_submission.id,
        "user_id": new_submission.user_id,
        "problem_id": new_submission.problem_id,
        "language": new_submission.language,
        "code": new_submission.code,
        "result": new_submission.result,
        "execution_time": new_submission.execution_time,
        "similarity_score": new_submission.similarity_score,
        "created_at": new_submission.created_at,
        "failed_testcase": result_data.get("failed_testcase"),
        "error_details": result_data.get("error_details", "")
    }

