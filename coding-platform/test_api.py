import urllib.request
import json

BASE_URL = "http://localhost:8001/api"

import sys
import os

with open(r"c:\Users\Narbavee\Desktop\project\coding-platform\backend\routes\student.py", "r") as f:
    content = f.read()
    if "subject_name" in content.split("get_student_profile")[1]:
        print("student.py contains the mapped dictionary.")
    else:
        print("student.py does NOT contain the mapped dictionary!")

sys.path.append(r"c:\Users\Narbavee\Desktop\project\coding-platform")
from backend import security, database, models
from datetime import timedelta

db = next(database.get_db())
user = db.query(models.User).filter_by(name="Narbavee").first()
if user:
    print(f"Narbavee DB Subjects: {[s.subject_name for s in user.selected_subjects]}")
    token = security.create_access_token(
        data={"sub": user.email, "role": user.role}, 
        expires_delta=timedelta(minutes=60)
    )
    headers = {"Authorization": f"Bearer {token}"}
    req = urllib.request.Request(f"{BASE_URL}/student/profile", headers=headers)
    with urllib.request.urlopen(req) as response:
        print("API Status:", response.status)
        print("API Response:", response.read().decode())
else:
    print("User Narbavee not found")
