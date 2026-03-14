"""
student_dashboard.py
--------------------
Query helpers for the student profile / dashboard.
Returns:
  - List of attempted problems with the best score per problem
  - Full submission history (most recent first)
  - Total accumulated marks
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models
from typing import List, Dict, Any


def get_attempted_problems(student_id: int, db: Session) -> List[Dict[str, Any]]:
    """
    Returns one entry per attempted problem showing:
      problem_id, title, difficulty, best_score (scaled), attempt_count, best_status
    Ordered by problem_id ascending.
    """
    rows = (
        db.query(
            models.Problem.id,
            models.Problem.title,
            models.Problem.difficulty,
            models.Problem.max_marks,
            func.max(models.Submission.score).label("best_score"),
            # Count distinct sessions. Treat all legacy submissions (NULL session) as ONE single attempt
            # by coalescing NULL to a constant (e.g., -1).
            func.count(func.distinct(func.coalesce(models.Submission.exam_session_id, -1))).label("attempt_count"),
        )
        .join(models.Submission, models.Problem.id == models.Submission.problem_id)
        .filter(models.Submission.user_id == student_id)
        .group_by(models.Problem.id)
        .order_by(models.Problem.id)
        .all()
    )

    result = []
    for row in rows:
        max_m = row.max_marks if row.max_marks else 100
        # Scale raw 0-100 score to the professor-set max marks
        scaled_score = round(row.best_score * max_m / 100)

        # Determine the status label for the best score
        if row.best_score == 100:
            best_status = "Accepted"
        elif row.best_score > 0:
            best_status = "Partial"
        else:
            best_status = "Wrong Answer"

        result.append({
            "problem_id": row.id,
            "title": row.title,
            "difficulty": row.difficulty,
            "best_score": scaled_score,
            "max_marks": max_m,
            "attempt_count": row.attempt_count,
            "best_status": best_status,
        })

    return result


def get_total_marks(student_id: int, db: Session) -> int:
    """
    Sum of the scaled best scores across all attempted problems for this student.
    """
    attempted = get_attempted_problems(student_id, db)
    return sum(p["best_score"] for p in attempted)


def get_submission_history(student_id: int, db: Session, limit: int = 20) -> List[models.Submission]:
    """
    Returns the most recent `limit` submissions for this student.
    """
    return (
        db.query(models.Submission)
        .filter(models.Submission.user_id == student_id)
        .order_by(models.Submission.created_at.desc())
        .limit(limit)
        .all()
    )
