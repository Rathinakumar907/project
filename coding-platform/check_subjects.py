import sys
import os
sys.path.append(r"c:\Users\Narbavee\Desktop\project\coding-platform")

from backend import database, models, schemas

db = next(database.get_db())

user = db.query(models.User).filter_by(name="nisha v").first()
if user:
    print(f"Subjects in DB for nisha v: {[s.subject_name for s in user.selected_subjects]}")
    data = {"user_id": user.id, "name": user.name, "university_id": user.university_id, "total_marks": 0, "attempted_problems": [], "selected_subjects": [{"id": s.id, "subject_name": s.subject_name} for s in user.selected_subjects]}
    try:
        spr = schemas.StudentProfileResponse(**data)
        print("Serialized:", spr.json())
    except Exception as e:
        print("Error serializing:", e)
