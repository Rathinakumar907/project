from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from .. import database, models, schemas, security, execution, anti_cheat
from ..grading import submission_saver, student_dashboard as sd_helpers
from ..violation_tracker import ViolationTracker
from ..behavior_analyzer import BehaviorAnalyzer
from ..exam_session_manager import ExamSessionManager
from ..secure_submission_handler import SecureSubmissionHandler
import json

router = APIRouter(
    prefix="/api/student",
    tags=['Student Actions']
)

@router.get("/problems", response_model=List[schemas.ProblemListResponse])
def get_all_problems(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    subject_ids = [s.id for s in current_user.selected_subjects]
    problems = db.query(models.Problem).filter(models.Problem.subject_id.in_(subject_ids)).all()
    
    # Add subject_name manually to response objects for the schema
    for p in problems:
        p.subject_name = p.subject.subject_name if p.subject else "Unassigned"
        
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
        
    subject_ids = [s.id for s in current_user.selected_subjects]
    if problem.subject_id is not None and problem.subject_id not in subject_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not enrolled in the subject for this problem")
        
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
        "selected_subjects": [{"id": s.id, "subject_name": s.subject_name} for s in current_user.selected_subjects],
        "TEST_KEY": "HELLO"
    }

@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(database.get_db)):
    from sqlalchemy import func
    
    # Subquery to get the best score for each (user, problem) pair
    subquery = db.query(
        models.Submission.user_id,
        models.Submission.problem_id,
        func.max(models.Submission.score).label("best_score")
    ).group_by(models.Submission.user_id, models.Submission.problem_id).subquery()
    
    # Join with User table to get names and sum the best scores
    leaderboard = db.query(
        models.User.name,
        models.User.university_id,
        func.sum(subquery.c.best_score).label("total_score")
    ).join(subquery, models.User.id == subquery.c.user_id)\
     .group_by(models.User.id)\
     .order_by(func.sum(subquery.c.best_score).desc())\
     .all()

    return [
        {"name": u.name, "university_id": u.university_id, "total_score": int(u.total_score or 0)}
        for u in leaderboard
    ]

@router.post("/exam/start", response_model=schemas.ExamSessionResponse)
def start_exam_session(
    request: schemas.ExamSessionCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Starts an exam session for the given problem. 
    If a session already exists (active or otherwise), prevents starting a new one.
    """
    session = ExamSessionManager.start_session(db, current_user.id, request.problem_id)
    
    if session.status != "active":
        detail = "Your exam session has been terminated due to violations." if session.status == "terminated" else "You have already completed this exam."
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )
        
    return session

@router.post("/exam/violation")
def record_violation(
    violation: schemas.ViolationCreate,
    db: Session = Depends(database.get_db),
    exam_session: models.ExamSession = Depends(security.get_exam_session)
):
    """
    Records an anti-cheat violation for the current exam session.
    """
    metadata = {}
    if violation.metadata_json:
        try:
            metadata = json.loads(violation.metadata_json)
        except:
            pass
            
    count = ViolationTracker.record_violation(
        db, 
        exam_session.id, 
        violation.event_type, 
        metadata
    )
    
    return {"violation_count": count, "event": violation.event_type}

@router.post("/exam/behavior")
def log_behavior(
    log: schemas.BehaviorLogCreate,
    db: Session = Depends(database.get_db),
    exam_session: models.ExamSession = Depends(security.get_exam_session)
):
    """
    Logs student behavior telemetry for analysis.
    """
    is_suspicious = BehaviorAnalyzer.log_behavior(
        db, 
        exam_session.id, 
        log.typing_speed, 
        log.paste_count, 
        log.paste_size, 
        log.idle_time
    )
    
    return {"status": "logged", "suspicious": is_suspicious}

@router.post("/submit", response_model=schemas.SubmissionResult)
def submit_code(
    submission: schemas.SubmissionCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user),
    exam_session: models.ExamSession = Depends(security.get_exam_session)
):
    """
    Submits code for evaluation. 
    Requires an active exam session for the target problem.
    Verification of session token and user ownership is handled by the dependency.
    """
    if submission.problem_id != exam_session.problem_id:
        raise HTTPException(
            status_code=400, 
            detail="Submission problem ID does not match the active exam session problem."
        )

    # All evaluation, plagiarism checking, and saving is now handled by the secure handler
    return SecureSubmissionHandler.handle_submission(
        db, 
        current_user, 
        submission, 
        exam_session
    )
