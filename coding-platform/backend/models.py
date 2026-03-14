from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    university_id = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String)  # 'student' or 'professor'

    submissions = relationship("Submission", back_populates="user")
    problems_created = relationship("Problem", back_populates="creator")
    exam_sessions = relationship("ExamSession", back_populates="user")

class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    difficulty = Column(String) # Easy, Medium, Hard
    reference_solution = Column(Text, nullable=True) # For partial marking
    max_marks = Column(Integer, default=100)          # Professor-defined max marks for this problem
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="problems_created")
    testcases = relationship("TestCase", back_populates="problem", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="problem", cascade="all, delete-orphan")

class TestCase(Base):
    __tablename__ = "testcases"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"))
    input_data = Column(Text)
    expected_output = Column(Text)

    problem = relationship("Problem", back_populates="testcases")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    problem_id = Column(Integer, ForeignKey("problems.id"))
    exam_session_id = Column(Integer, ForeignKey("exam_sessions.id"), nullable=True)
    language = Column(String)
    code = Column(Text)
    result = Column(String)              # Accepted, Partial, Wrong Answer, TLE, etc.
    status = Column(String, nullable=True)  # same as result but explicit (new column)
    score = Column(Integer, default=0)   # final mark 0-100
    passed_testcases = Column(Integer, default=0)   # how many TCs passed
    total_testcases = Column(Integer, default=0)    # how many TCs total
    execution_time = Column(String)      # e.g. "120ms"
    similarity_score = Column(Integer, nullable=True)  # % plagiarism similarity
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")
    exam_session = relationship("ExamSession", back_populates="submission")

class ExamSession(Base):
    __tablename__ = "exam_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    problem_id = Column(Integer, ForeignKey("problems.id"))
    session_token = Column(String, unique=True, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, default="active") # active, completed, terminated

    user = relationship("User", back_populates="exam_sessions")
    problem = relationship("Problem")
    violations = relationship("Violation", back_populates="session", cascade="all, delete-orphan")
    behavior_logs = relationship("BehaviorLog", back_populates="session", cascade="all, delete-orphan")
    submission = relationship("Submission", back_populates="exam_session", uselist=False)

class Violation(Base):
    __tablename__ = "violations"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("exam_sessions.id"))
    event_type = Column(String) # TAB_SWITCH, WINDOW_BLUR, PASTE_ABUSE, VM_DETECTED, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(Text, nullable=True) # JSON details (renamed from metadata to avoid conflict)

    session = relationship("ExamSession", back_populates="violations")

class BehaviorLog(Base):
    __tablename__ = "behavior_logs"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("exam_sessions.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    typing_speed = Column(Integer, nullable=True) # chars per min
    paste_count = Column(Integer, default=0)
    paste_size = Column(Integer, default=0)
    idle_time = Column(Integer, default=0) # seconds

    session = relationship("ExamSession", back_populates="behavior_logs")

class PlagiarismFlag(Base):
    __tablename__ = "plagiarism_flags"
    id = Column(Integer, primary_key=True, index=True)
    submission_1_id = Column(Integer, ForeignKey("submissions.id"))
    submission_2_id = Column(Integer, ForeignKey("submissions.id"))
    total_similarity = Column(Integer) # Percentage
    token_similarity = Column(Integer)
    ast_similarity = Column(Integer)
    control_flow_similarity = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="potential") # potential, confirmed, cleared

    submission_1 = relationship("Submission", foreign_keys=[submission_1_id])
    submission_2 = relationship("Submission", foreign_keys=[submission_2_id])
