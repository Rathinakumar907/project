# UniCode Platform

A full-stack university coding assessment platform with anti-cheating features.

## Requirements
- Python 3.10+
- Docker (for sandbox execution if enabled)
- PostgreSQL/SQLite

## Setup Instructions
1. Install requirements:
   `pip install fastapi uvicorn sqlalchemy passlib[bcrypt] pyjwt pydantic`
2. Run database setup and create tables.
3. Pull docker images for code execution:
   `python docker/pull_images.py`
4. Start the server:
   `uvicorn backend.main:app --reload`

## Features
- Student & Professor Roles
- Interactive Monaco Editor
- Auto-Evaluation Server
- Plagiarism Detection & Anti-Cheat System
