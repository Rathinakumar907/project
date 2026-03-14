"""
submission_saver.py
-------------------
Handles persisting a graded submission to the database.
Keeps route handlers clean by encapsulating all ORM writes here.

Marks are ONLY written by the backend (students cannot modify them).
"""

from sqlalchemy.orm import Session
from .. import models
from typing import Optional


def save_submission(
    db: Session,
    user_id: int,
    problem_id: int,
    language: str,
    code: str,
    score: int,
    status: str,
    passed_testcases: int,
    total_testcases: int,
    execution_time: str,
    similarity_score: Optional[int] = None,
    exam_session_id: Optional[int] = None,
) -> models.Submission:
    """
    Persists a graded submission to the submissions table.
    Returns the newly saved ORM object (refreshed from DB).
    """
    new_submission = models.Submission(
        user_id=user_id,
        problem_id=problem_id,
        language=language,
        code=code,
        result=status,          # maps to existing 'result' column
        status=status,          # new dedicated status column
        score=score,
        passed_testcases=passed_testcases,
        total_testcases=total_testcases,
        execution_time=execution_time,
        similarity_score=similarity_score,
        exam_session_id=exam_session_id,
    )
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    return new_submission
