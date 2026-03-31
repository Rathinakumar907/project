# 🚀 UniCode: Advanced Coding & Examination Platform

**UniCode** is a secure, AI-powered platform for university coding assessments. It provides a robust and fair environment for both students and professors by combining interactive coding tools with an advanced security and anti-cheat engine.

---

## ✨ Key Features

### 🛡️ Secure Execution Sandbox
- **Docker-Based Isolation**: Student code runs in isolated containers with strict memory and CPU limits.
- **Multi-Language Support**: Support for Python, C, C++, and Java.
- **Zero Network Access**: Code runs in a total network blackout to prevent external assistance.

### 🕵️ Advanced Anti-Cheat Engine
- **Plagiarism Detection**: Uses AST (Abstract Syntax Tree), tokenization, and control flow analysis to catch sophisticated plagiarism.
- **Proctoring Suite**: Tracks tab-switching, window blurring, and "paste abuse" (unusually large or frequent pastes).
- **Behavioral Analysis**: Monitors typing speed, idle time, and VM detection to identify potential cheating patterns.

### 📊 Comprehensive Dashboard & Analytics
- **Professor Dashboard**: Real-time monitoring of exam sessions, submission grading, and plagiarism flags.
- **Student Performance Insights**: Identifies weak areas and topic-wise success rates.
- **Flexible Grading**: Support for multi-weight test cases and partial marking.

---

## 🛠️ Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy](https://www.sqlalchemy.org/)
- **Frontend**: Vanilla [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript), [Jinja2 Templates](https://jinja.palletsprojects.com/), [Monaco Editor](https://microsoft.github.io/monaco-editor/)
- **Sandbox**: [Docker](https://www.docker.com/)
- **Database**: [SQLite](https://www.sqlite.org/) (Default), supports PostgreSQL

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Docker (Required for sandbox; local fallback available for Windows)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/Rathinakumar907/project.git
cd coding-platform

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Initialization
Ensure the database schema is up-to-date:
```bash
python migrate_db.py
```

### 4. Code Sandbox Preparation
Pull the required Docker images for secure execution:
```bash
# If using Docker (Recommended)
docker pull python:3.10-alpine
docker pull gcc:latest
docker pull openjdk:17-alpine
```

### 5. Running the Application
```bash
python main.py
```
*Wait 2 seconds and the browser will automatically open at `http://localhost:8001`.*

---

## 📂 Project Structure

```text
├── backend/              # API routes, Models, and Core logic
│   ├── routes/           # Auth, Student, and Professor endpoints
│   ├── grading/          # Grading utilities and AST analysis
│   ├── models.py         # SQLAlchemy database models
│   └── execution.py      # Docker execution sandbox
├── frontend/             # Frontend UI
│   ├── static/           # CSS and Client-side JS
│   └── templates/        # Jinja2 HTML templates
├── docker/               # Docker configs and utility scripts
├── tests/                # Automated security and logic tests
├── main.py               # Application entry point
└── requirements.txt      # Python dependencies
```

---

## 🤝 Contributing

We welcome contributions! Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

> [!NOTE]
> For production environments, ensure strict `CORSMiddleware` configuration in `backend/main.py`.

> [!IMPORTANT]
> If Docker is not present, the platform will fallback to local execution. While functional, this is **NOT recommended** for graded assessments as it lacks security isolation.

