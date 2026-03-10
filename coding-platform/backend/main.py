from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from . import models, database
from .routes import auth, professor, student
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

import os
# Ensure frontend static directories exist for mounting
os.makedirs("frontend/static", exist_ok=True)
os.makedirs("frontend/templates", exist_ok=True)

try:
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
except RuntimeError:
    pass

templates = Jinja2Templates(directory="frontend/templates")

@app.get("/", response_class=HTMLResponse)
def root_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/student/dashboard", response_class=HTMLResponse)
def student_dashboard(request: Request):
    return templates.TemplateResponse("student_dashboard.html", {"request": request})

@app.get("/student/coding/{problem_id}", response_class=HTMLResponse)
def coding_environment(request: Request, problem_id: int):
    return templates.TemplateResponse("coding_environment.html", {"request": request, "problem_id": problem_id})

@app.get("/professor/dashboard", response_class=HTMLResponse)
def professor_dashboard(request: Request):
    return templates.TemplateResponse("professor_dashboard.html", {"request": request})

