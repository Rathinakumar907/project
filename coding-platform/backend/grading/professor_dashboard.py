"""
professor_dashboard.py
-----------------------
Query helpers for the professor analytics view.
Returns a matrix of student × problem → best score, plus totals per student.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models
from typing import List, Dict, Any


def get_all_student_marks(db: Session) -> Dict[str, Any]:
    """
    Returns:
    {
      "problems": [ {"id": 1, "title": "Sum of Two", "difficulty": "Easy"}, ... ],
      "students": [
        {
          "user_id": 3,
          "name": "Rahul",
          "university_id": "22CS001",
          "marks": {1: 100, 2: 60, 3: 0},   # problem_id → best_score
          "total": 160
        },
        ...
      ]
    }
    """
    # All problems (ordered)
    all_problems = db.query(models.Problem).order_by(models.Problem.id).all()

    # Best score per (user_id, problem_id)
    best_per_pair = (
        db.query(
            models.Submission.user_id,
            models.Submission.problem_id,
            func.max(models.Submission.score).label("best_score"),
        )
        .group_by(models.Submission.user_id, models.Submission.problem_id)
        .all()
    )

    # Build lookup: {user_id: {problem_id: best_score}}
    score_map: Dict[int, Dict[int, int]] = {}
    for row in best_per_pair:
        score_map.setdefault(row.user_id, {})[row.problem_id] = row.best_score

    # All students (role = student) who have at least one submission
    student_ids = list(score_map.keys())
    students_db = (
        db.query(models.User)
        .filter(models.User.id.in_(student_ids), models.User.role == "student")
        .order_by(models.User.name)
        .all()
    )

    students_out = []
    problem_ids = [p.id for p in all_problems]
    # Build max_marks lookup
    max_marks_map = {p.id: (p.max_marks if p.max_marks else 100) for p in all_problems}

    for student in students_db:
        marks = {}
        for pid in problem_ids:
            raw = score_map.get(student.id, {}).get(pid, 0)
            max_m = max_marks_map[pid]
            # Scale: actual_marks = raw_percent * max_marks / 100
            marks[pid] = round(raw * max_m / 100)
        total = sum(marks.values())

        students_out.append({
            "user_id": student.id,
            "name": student.name,
            "university_id": student.university_id,
            "marks": marks,
            "total": total,
        })

    # Sort by total descending (highest scorer first)
    students_out.sort(key=lambda s: s["total"], reverse=True)

    return {
        "problems": [
            {"id": p.id, "title": p.title, "difficulty": p.difficulty, "max_marks": p.max_marks or 100}
            for p in all_problems
        ],
        "students": students_out,
    }
