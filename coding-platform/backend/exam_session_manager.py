from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from . import models

class ExamSessionManager:
    @staticmethod
    def start_session(db: Session, user_id: int, problem_id: int) -> models.ExamSession:
        """
        Starts a new exam session for a student and problem. 
        If one is already active, returns it.
        """
        existing_session = db.query(models.ExamSession).filter(
            models.ExamSession.user_id == user_id,
            models.ExamSession.problem_id == problem_id
        ).first()
        
        if existing_session:
            return existing_session
            
        session_token = str(uuid.uuid4())
        new_session = models.ExamSession(
            user_id=user_id,
            problem_id=problem_id,
            session_token=session_token,
            status="active",
            start_time=datetime.utcnow()
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session

    @staticmethod
    def get_session_by_token(db: Session, token: str) -> models.ExamSession:
        return db.query(models.ExamSession).filter(
            models.ExamSession.session_token == token
        ).first()

    @staticmethod
    def validate_session(db: Session, token: str) -> bool:
        """Checks if a session token is valid and active."""
        session = db.query(models.ExamSession).filter(
            models.ExamSession.session_token == token,
            models.ExamSession.status == "active"
        ).first()
        return session is not None

    @staticmethod
    def terminate_session(db: Session, token: str, reason: str = "completed"):
        """Marks a session as non-active."""
        session = db.query(models.ExamSession).filter(
            models.ExamSession.session_token == token
        ).first()
        if session:
            session.status = reason
            session.end_time = datetime.utcnow()
            db.commit()
            db.refresh(session)
        return session
