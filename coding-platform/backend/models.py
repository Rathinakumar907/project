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

class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    difficulty = Column(String) # Easy, Medium, Hard
    reference_solution = Column(Text, nullable=True) # For partial marking
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
