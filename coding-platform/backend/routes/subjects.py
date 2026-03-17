from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import database, models, schemas, security

router = APIRouter(
    prefix="/api/subjects",
    tags=['Subjects']
)

@router.get("", response_model=List[schemas.SubjectResponse])
def get_all_subjects(db: Session = Depends(database.get_db)):
    return db.query(models.Subject).all()

@router.post("/assign", response_model=schemas.UserResponse)
def assign_subjects(
    subject_ids: List[int],
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    subjects = db.query(models.Subject).filter(models.Subject.id.in_(subject_ids)).all()
    current_user.selected_subjects = subjects
    db.commit()
    db.refresh(current_user)
    return current_user
