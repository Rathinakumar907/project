# Contributing to University Coding Platform

First off, thanks for taking the time to contribute! 🎉

## Submitting Pull Requests

1. **Fork** the repo on GitHub and clone it locally.
2. **Create a branch** for your edits (`git checkout -b feature/my-new-feature` or `git checkout -b fix/issue-number`).
3. Follow the Local Setup instructions below to ensure everything works natively.
4. Push your branch to GitHub.
5. Open a Pull Request! Keep your commit messages descriptive and precise.

## Local Setup

1. Install Python 3.10 or newer.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```
4. Verify the application comes up at `http://localhost:8001/` (login screen).

## Guidelines
- Follow standard PEP-8 style guidelines for Python code.
- Ensure that you are not mutating the database structure manually. If schema modifications are required, please supply an accompanying migration script and discuss it in an issue first.
- Re-use the existing routing styles in FastAPI (use Type hints).
- Our frontend uses lightweight vanilla HTML/JS paired with Jinja2 templating. Ensure you test your changes by verifying visual impact manually.
