from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# --- User Schemas ---
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    university_id: str
    password: str
    is_professor: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    university_id: str
    role: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Problem Schemas ---
class TestCaseBase(BaseModel):
    input_data: str
    expected_output: str

class TestCaseCreate(TestCaseBase):
    pass

class TestCaseResponse(TestCaseBase):
    id: int
    problem_id: int

    class Config:
        orm_mode = True

class ProblemCreate(BaseModel):
    title: str
    description: str
    difficulty: str
    testcases: List[TestCaseCreate]

class ProblemResponse(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str
    created_by: int
    created_at: datetime
    testcases: List[TestCaseResponse] = []

    class Config:
        orm_mode = True

class ProblemListResponse(BaseModel):
    id: int
    title: str
    difficulty: str

    class Config:
        orm_mode = True

# --- Submission Schemas ---
class SubmissionCreate(BaseModel):
    problem_id: int
    language: str
    code: str
    cheat_detected: Optional[bool] = False

class UserBasicInfo(BaseModel):
    name: str
    university_id: str

    class Config:
        orm_mode = True

class SubmissionResponse(BaseModel):
    id: int
    user_id: int
    problem_id: int
    language: str
    code: str
    result: str
    execution_time: str
    similarity_score: Optional[int]
    created_at: datetime
    failed_testcase: Optional[int] = None
    error_details: Optional[str] = None
    user: Optional[UserBasicInfo] = None

    class Config:
        orm_mode = True
