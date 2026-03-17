import sys
import os

# Add the current directory to sys.path so we can import 'backend'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from backend.database import SessionLocal, engine
from backend import models

def populate():
    subjects_to_add = [
        "Python",
        "Data Structures and Algorithms (DSA)",
        "Python and DSA Lab"
    ]
    
    db = SessionLocal()
    try:
        for s_name in subjects_to_add:
            existing = db.query(models.Subject).filter(models.Subject.subject_name == s_name).first()
            if not existing:
                new_subject = models.Subject(subject_name=s_name)
                db.add(new_subject)
                print(f"Added subject: {s_name}")
            else:
                print(f"Subject '{s_name}' already exists.")
        db.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate()
