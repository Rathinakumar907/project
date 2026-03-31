# 🚀 UniCode – Smart Coding & Exam Platform

UniCode is a powerful, secure, and scalable coding examination platform designed for universities and institutions. It combines real-time coding, automated evaluation, and advanced anti-cheating mechanisms to ensure fair and efficient assessments.

---

## 🔥 Overview

UniCode provides an end-to-end solution for conducting coding exams:

* 👨‍🎓 Students can write and execute code in a controlled environment
* 👨‍🏫 Professors can create exams, monitor activity, and evaluate performance
* 🤖 The system ensures fairness using intelligent anti-cheat mechanisms

---

## ✨ Features

### 🛡️ Secure Code Execution

* Runs code inside isolated environments (Docker-based sandbox)
* Strict CPU and memory limits
* No internet access during execution
* Supports multiple languages:

  * Python 🐍
  * C ⚙️
  * C++ 💻
  * Java ☕

---

### 🧠 Smart Anti-Cheat System

* Detects plagiarism using:

  * Abstract Syntax Tree (AST) analysis
  * Token matching
  * Code structure comparison
* Monitors suspicious behavior:

  * Tab switching 🚫
  * Copy-paste abuse 📋
  * Idle time & typing patterns ⏱️
* Helps maintain exam integrity in real-time

---

### 📊 Dashboard & Analytics

* **Professor Panel**

  * Create and manage exams
  * Monitor students live
  * View flagged activities
* **Student Insights**

  * Performance tracking
  * Topic-wise analysis
* **Flexible Evaluation**

  * Custom test cases
  * Partial marking system

---

## 🏗️ Tech Stack

### Backend

* FastAPI
* SQLAlchemy

### Frontend

* JavaScript (Vanilla)
* Jinja2 Templates
* Monaco Code Editor

### Database

* SQLite (default)
* PostgreSQL (optional)

### Execution Engine

* Docker Sandbox

---

## ⚙️ Installation & Setup

### Prerequisites

* Python 3.10+
* Docker installed and running

---

### Steps

```bash
# Clone the repository
git clone <your-repo-link>

# Navigate to project
cd coding-platform

# Create virtual environment
python -m venv venv

# Activate environment
venv\Scripts\activate   # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

---

### ▶️ Run the Application

```bash
uvicorn main:app --reload
```

App will run at:
👉 http://127.0.0.1:8000

---

## 🧪 Database Management

* Initialize / reset database:

```bash
python reset_db.py
```

* Migrate database:

```bash
python migrate_db.py
```

* Populate subjects:

```bash
python populate_subjects.py
```

---

## 📁 Project Structure (Simplified)

```
coding-platform/
│── main.py                # Entry point
│── requirements.txt       # Dependencies
│── README.md              # Documentation
│── users_data.json        # Sample user data
│── test_*.py              # Testing scripts
│── populate_subjects.py   # Data seeding
│── migrate_db.py          # DB migration
│── reset_db.py            # Reset database
│── templates/             # Frontend UI
│── static/                # JS/CSS assets
```

---

## 🔐 Security Highlights

* Sandbox execution prevents system access
* No external API/network calls allowed
* Real-time cheating detection
* Fully isolated student environments

---

## 🚀 Future Improvements

* AI-based code evaluation 🤖
* Face proctoring integration 🎥
* Cloud deployment support ☁️
* Advanced analytics dashboard 📈

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

---

## 📜 License

This project is open-source and available under the MIT License.

---

## 💡 Final Note

UniCode is built to make coding exams smarter, fairer, and stress-free for both students and educators. Whether you're conducting small tests or large-scale university exams, UniCode has you covered.

---

🔥 *Built for performance. Designed for fairness.*
