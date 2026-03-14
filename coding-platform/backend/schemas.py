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
    reference_solution: Optional[str] = None
    max_marks: int = 100
    testcases: List[TestCaseCreate]

class ProblemResponse(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str
    reference_solution: Optional[str] = None
    max_marks: int = 100
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
    status: Optional[str] = None
    score: int
    passed_testcases: Optional[int] = 0
    total_testcases: Optional[int] = 0
    execution_time: str
    similarity_score: Optional[int]
    created_at: datetime
    failed_testcase: Optional[int] = None
    error_details: Optional[str] = None
    user: Optional[UserBasicInfo] = None

    class Config:
        orm_mode = True


# --- Student Profile ---
class ProblemProgressItem(BaseModel):
    problem_id: int
    title: str
    difficulty: str
    best_score: int
    max_marks: int = 100
    attempt_count: int
    best_status: str

class StudentProfileResponse(BaseModel):
    user_id: int
    name: str
    university_id: str
    total_marks: int
    attempted_problems: List[ProblemProgressItem]


# --- Professor Analytics ---
class ProblemMeta(BaseModel):
    id: int
    title: str
    difficulty: str
    max_marks: int = 100

class StudentMarksRow(BaseModel):
    user_id: int
    name: str
    university_id: str
    marks: dict          # {problem_id (str): score}
    total: int

class ProfessorAnalyticsResponse(BaseModel):
    problems: List[ProblemMeta]
    students: List[StudentMarksRow]


# --- Real-time submission result ---
class SubmissionResult(BaseModel):
    status: str
    score: int
    passed_testcases: int
    total_testcases: int
    message: str
    execution_time: str
    submission_id: int

# --- Exam Session & Security Schemas ---
class ExamSessionCreate(BaseModel):
    problem_id: int

class ExamSessionResponse(BaseModel):
    id: int
    user_id: int
    problem_id: int
    session_token: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None

    class Config:
        orm_mode = True

class ViolationCreate(BaseModel):
    event_type: str
    metadata_json: Optional[str] = None

class BehaviorLogCreate(BaseModel):
    typing_speed: Optional[int] = None
    paste_count: int = 0
    paste_size: int = 0
    idle_time: int = 0
