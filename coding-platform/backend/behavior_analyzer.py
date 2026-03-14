from sqlalchemy.orm import Session
from . import models
from datetime import datetime

class BehaviorAnalyzer:
    @staticmethod
    def log_behavior(
        db: Session, 
        session_id: int, 
        typing_speed: int = None, 
        paste_count: int = 0, 
        paste_size: int = 0, 
        idle_time: int = 0
    ) -> bool:
        """
        Logs student behavior telemetry to the database.
        Returns True if the behavior is flagged as suspicious.
        """
        new_log = models.BehaviorLog(
            session_id=session_id,
            timestamp=datetime.utcnow(),
            typing_speed=typing_speed,
            paste_count=paste_count,
            paste_size=paste_size,
            idle_time=idle_time
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        
        # SUSPICIOUS HEURISTICS
        # 1. Extremely fast typing (> 1000 characters per minute)
        if typing_speed and typing_speed > 1000:
            return True
            
        # 2. Large paste (+500 chars) after long idleness (+5 mins)
        if paste_size > 500 and idle_time > 300:
            return True
            
        # 3. Accumulated paste count is too high (logic should check aggregate)
        return False
