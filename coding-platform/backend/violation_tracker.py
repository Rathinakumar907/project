from sqlalchemy.orm import Session
from . import models
from datetime import datetime, timedelta
import json

class ViolationTracker:
    @staticmethod
    def record_violation(db: Session, session_id: int, event_type: str, metadata: dict = None) -> int:
        """
        Records an anti-cheat violation in the database.
        Returns the total count of violations for this session.
        """
        new_violation = models.Violation(
            session_id=session_id,
            event_type=event_type,
            metadata_json=json.dumps(metadata) if metadata else None
        )
        db.add(new_violation)
        db.commit()
        db.refresh(new_violation)
        
        session = db.query(models.ExamSession).filter(models.ExamSession.id == session_id).first()
        if session:
            # Also add to CheatingLog for Professor visibility
            cheating_log = models.CheatingLog(
                user_id=session.user_id,
                problem_id=session.problem_id,
                reason=f"Violation Detected: {event_type}",
                timestamp=datetime.utcnow()
            )
            db.add(cheating_log)
            db.commit()
        
        # Count total violations for this session
        total_violations = db.query(models.Violation).filter(
            models.Violation.session_id == session_id
        ).count()
        
        # Mark session as 'terminated' if violations exceed threshold (e.g., 5)
        if total_violations >= 5:
            if session and session.status == "active":
                session.status = "terminated"
                db.commit()
        
        return total_violations

    @staticmethod
    def get_violation_count(db: Session, session_id: int) -> int:
        return db.query(models.Violation).filter(
            models.Violation.session_id == session_id
        ).count()

    @staticmethod
    def check_submission_rate(db: Session, user_id: int, problem_id: int, limit: int = 5, window_minutes: int = 1) -> bool:
        """
        Returns True if the user has exceeded the submission limit within the time window.
        """
        since_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        count = db.query(models.Submission).filter(
            models.Submission.user_id == user_id,
            models.Submission.problem_id == problem_id,
            models.Submission.created_at >= since_time
        ).count()
        
        return count >= limit
