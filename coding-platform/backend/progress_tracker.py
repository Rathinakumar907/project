from sqlalchemy.orm import Session
from datetime import datetime
from . import models

class ProgressTracker:
    @staticmethod
    def update_progress_on_submission(
        db: Session,
        user_id: int,
        problem_id: int,
        subject_id: int,
        status: str,
        time_taken_seconds: int
    ):
        """
        Updates the StudentProgress and StudentWeakAreas tables.
        status comes from evaluate_submission: e.g., 'Accepted', 'Wrong Answer', etc.
        """
        # 1. Update StudentProgress
        progress_record = db.query(models.StudentProgress).filter(
            models.StudentProgress.user_id == user_id,
            models.StudentProgress.problem_id == problem_id
        ).first()

        # Map execution result to standard status
        mapped_status = "Solved" if status == "Accepted" else "Failed"

        if progress_record:
            progress_record.attempts_count += 1
            progress_record.timestamp = datetime.utcnow()
            
            if mapped_status == "Solved":
                progress_record.status = "Solved"
                # Keep the best (shortest) time if available
                if progress_record.time_taken is None or time_taken_seconds < progress_record.time_taken:
                    progress_record.time_taken = time_taken_seconds
            else:
                if progress_record.status != "Solved":
                    progress_record.status = "Failed"
        else:
            progress_record = models.StudentProgress(
                user_id=user_id,
                problem_id=problem_id,
                status=mapped_status,
                attempts_count=1,
                time_taken=time_taken_seconds if mapped_status == "Solved" else None,
                timestamp=datetime.utcnow()
            )
            db.add(progress_record)

        # 2. Update StudentWeakAreas
        if subject_id is not None:
            subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
            if subject:
                topic = subject.subject_name
                weak_area = db.query(models.StudentWeakAreas).filter(
                    models.StudentWeakAreas.user_id == user_id,
                    models.StudentWeakAreas.topic == topic
                ).first()

                if weak_area:
                    weak_area.attempts += 1
                    if mapped_status == "Failed":
                        weak_area.failures += 1
                    # Recalculate successes: attempts - failures
                    successes = weak_area.attempts - weak_area.failures
                    weak_area.success_rate = int((successes / weak_area.attempts) * 100)
                else:
                    failures = 1 if mapped_status == "Failed" else 0
                    success_rate = 0 if mapped_status == "Failed" else 100
                    weak_area = models.StudentWeakAreas(
                        user_id=user_id,
                        topic=topic,
                        attempts=1,
                        failures=failures,
                        success_rate=success_rate
                    )
                    db.add(weak_area)

        db.commit()
