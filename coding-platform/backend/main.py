from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from . import models, database
from .routes import auth, professor, student, subjects
import os

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="University Coding Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(professor.router)
app.include_router(student.router)
app.include_router(subjects.router)

import os
# Ensure frontend static directories exist for mounting
os.makedirs("frontend/static", exist_ok=True)
os.makedirs("frontend/templates", exist_ok=True)

try:
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
except RuntimeError:
    pass

templates = Jinja2Templates(directory="frontend/templates")

@app.get("/", response_class=RedirectResponse)
def root_page(request: Request):
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request})

@app.get("/student/subjects", response_class=HTMLResponse)
def student_subjects_page(request: Request):
    return templates.TemplateResponse(request=request, name="student_subjects.html", context={"request": request})

@app.get("/student/dashboard", response_class=HTMLResponse)
def student_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="student_dashboard.html", context={"request": request})

@app.get("/student/{subject_slug}", response_class=HTMLResponse)
def student_subject_problems(request: Request, subject_slug: str):
    if subject_slug not in ["python", "dsa", "lab"]:
        return RedirectResponse(url="/student/subjects")
    return templates.TemplateResponse(request=request, name="student_dashboard.html", context={"request": request, "subject_slug": subject_slug})

@app.get("/student/coding/{problem_id}", response_class=HTMLResponse)
def coding_environment(request: Request, problem_id: int):
    return templates.TemplateResponse(request=request, name="coding_environment.html", context={"request": request, "problem_id": problem_id})

@app.get("/professor/dashboard", response_class=HTMLResponse)
def professor_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="professor_dashboard.html", context={"request": request})

@app.get("/select-subjects", response_class=HTMLResponse)
def select_subjects_page(request: Request):
    return templates.TemplateResponse(request=request, name="select_subjects.html", context={"request": request})
