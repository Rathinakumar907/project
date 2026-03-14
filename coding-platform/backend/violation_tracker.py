from sqlalchemy.orm import Session
from . import models
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
        
        # Count total violations for this session
        total_violations = db.query(models.Violation).filter(
            models.Violation.session_id == session_id
        ).count()
        
        # Optionally: mark session as 'terminated' if violations exceed threshold
        if total_violations >= 3:
            session = db.query(models.ExamSession).filter(models.ExamSession.id == session_id).first()
            if session and session.status == "active":
                session.status = "terminated"
                db.commit()
        
        return total_violations

    @staticmethod
    def get_violation_count(db: Session, session_id: int) -> int:
        return db.query(models.Violation).filter(
            models.Violation.session_id == session_id
        ).count()
