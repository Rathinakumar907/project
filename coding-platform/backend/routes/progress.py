from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from .. import database, models, schemas, security

router = APIRouter(
    prefix="/api",
    tags=['Student Progress']
)

@router.get("/student-progress/{user_id}", response_model=schemas.StudentProgressDashboardResponse)
def get_student_progress(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    # Security: Only professors can view other students' data
    if current_user.role != 'professor' and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this data")

    # Total problems solved
    solved_count = db.query(models.StudentProgress).filter(
        models.StudentProgress.user_id == user_id,
        models.StudentProgress.status == "Solved"
    ).count()

    # Accuracy (total problems solved / total unique problems attempted)
    total_attempted = db.query(models.StudentProgress).filter(
        models.StudentProgress.user_id == user_id
    ).count()
    
    accuracy = int((solved_count / total_attempted) * 100) if total_attempted > 0 else 0

    # Average time per problem (only for solved problems)
    avg_time_row = db.query(func.avg(models.StudentProgress.time_taken)).filter(
        models.StudentProgress.user_id == user_id,
        models.StudentProgress.status == "Solved"
    ).scalar()
    avg_time = int(avg_time_row) if avg_time_row else None

    # Weak areas
    weak_areas = db.query(models.StudentWeakAreas).filter(
        models.StudentWeakAreas.user_id == user_id,
        models.StudentWeakAreas.success_rate < 40
    ).all()
    weak_area_topics = [wa.topic for wa in weak_areas]

    return schemas.StudentProgressDashboardResponse(
        user_id=user_id,
        total_problems_solved=solved_count,
        accuracy_percentage=accuracy,
        average_time_per_problem=avg_time,
        weak_areas=weak_area_topics
    )

@router.get("/student-weak-areas/{user_id}", response_model=List[schemas.StudentWeakAreasResponse])
def get_student_weak_areas(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    if current_user.role != 'professor' and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this data")

    weak_areas = db.query(models.StudentWeakAreas).filter(
        models.StudentWeakAreas.user_id == user_id,
        models.StudentWeakAreas.success_rate < 40
    ).all()
    
    return weak_areas

@router.get("/student-progress-graph/{user_id}", response_model=schemas.StudentProgressGraphResponse)
def get_student_progress_graph(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    if current_user.role != 'professor' and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this data")

    # Collect submission stats per day using existing submissions table
    submissions = db.query(models.Submission).filter(
        models.Submission.user_id == user_id
    ).order_by(models.Submission.created_at.asc()).all()

    daily_stats = {}
    for sub in submissions:
        day_str = sub.created_at.strftime("%Y-%m-%d")
        if day_str not in daily_stats:
            daily_stats[day_str] = {"attempts": 0, "solved": 0}
        
        daily_stats[day_str]["attempts"] += 1
        if sub.score == 100 or sub.result == "Accepted": # Simplified definition of solved
            daily_stats[day_str]["solved"] += 1

    dates = []
    problems_solved = []
    accuracy = []
    
    for day, stats in daily_stats.items():
        dates.append(day)
        problems_solved.append(stats["solved"])
        acc = int((stats["solved"] / stats["attempts"]) * 100) if stats["attempts"] > 0 else 0
        accuracy.append(acc)

    return schemas.StudentProgressGraphResponse(
        dates=dates,
        problems_solved=problems_solved,
        accuracy=accuracy
    )
