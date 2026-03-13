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


def get_attempted_problems(user_id: int, db: Session) -> List[Dict[str, Any]]:
    """
    Returns one entry per attempted problem showing:
      problem_id, title, difficulty, best_score, attempt_count, best_status
    Ordered by problem_id ascending.
    """
    # Subquery: best score per problem for this student
    best_scores = (
        db.query(
            models.Submission.problem_id,
            func.max(models.Submission.score).label("best_score"),
            func.count(models.Submission.id).label("attempt_count"),
        )
        .filter(models.Submission.user_id == user_id)
        .group_by(models.Submission.problem_id)
        .subquery()
    )

    rows = (
        db.query(
            models.Problem.id,
            models.Problem.title,
            models.Problem.difficulty,
            best_scores.c.best_score,
            best_scores.c.attempt_count,
        )
        .join(best_scores, models.Problem.id == best_scores.c.problem_id)
        .order_by(models.Problem.id)
        .all()
    )

    result = []
    for row in rows:
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
            "best_score": row.best_score,
            "attempt_count": row.attempt_count,
            "best_status": best_status,
        })

    return result


def get_total_marks(user_id: int, db: Session) -> int:
    """
    Sum of the best scores across all attempted problems for this student.
    """
    attempted = get_attempted_problems(user_id, db)
    return sum(p["best_score"] for p in attempted)


def get_submission_history(user_id: int, db: Session, limit: int = 20) -> List[models.Submission]:
    """
    Returns the most recent `limit` submissions for this student.
    """
    return (
        db.query(models.Submission)
        .filter(models.Submission.user_id == user_id)
        .order_by(models.Submission.created_at.desc())
        .limit(limit)
        .all()
    )
