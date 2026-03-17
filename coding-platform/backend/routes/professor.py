from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import io
import PyPDF2
from .. import database, models, schemas, security
from ..grading import professor_dashboard as prof_helpers

router = APIRouter(
    prefix="/api/professor",
    tags=['Professor Actions']
)

@router.post("/problems", response_model=schemas.ProblemResponse)
def create_problem(
    problem: schemas.ProblemCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_professor)
):
    new_problem = models.Problem(
        title=problem.title,
        description=problem.description,
        difficulty=problem.difficulty,
        reference_solution=problem.reference_solution,
        total_marks=problem.total_marks,
        created_by=current_user.id,
        subject_id=problem.subject_id
    )
    
    db.add(new_problem)
    db.commit()
    db.refresh(new_problem)

    # Add test cases
    for tc in problem.testcases:
        test_case = models.TestCase(
            problem_id=new_problem.id,
            input_data=tc.input_data,
            expected_output=tc.expected_output,
            marks_weight=tc.marks_weight
        )
        db.add(test_case)
    
    db.commit()
    db.refresh(new_problem)
    return new_problem

@router.get("/problems", response_model=List[schemas.ProblemResponse])
def get_professor_problems(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_professor)
):
    subject_ids = [s.id for s in current_user.selected_subjects]
    problems = db.query(models.Problem).filter(models.Problem.subject_id.in_(subject_ids)).all()
    return problems

@router.get("/problems/{problem_id}", response_model=schemas.ProblemResponse)
def get_problem(
    problem_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_professor)
):
    problem = db.query(models.Problem).filter(models.Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    if problem.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this problem")
    return problem

@router.put("/problems/{problem_id}", response_model=schemas.ProblemResponse)
def update_problem(
    problem_id: int,
    problem_data: schemas.ProblemCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_professor)
):
    problem = db.query(models.Problem).filter(models.Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    if problem.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this problem")

    # Update basic problem details
    problem.title = problem_data.title
    problem.description = problem_data.description
    problem.difficulty = problem_data.difficulty
    problem.reference_solution = problem_data.reference_solution
    problem.total_marks = problem_data.total_marks
    
    # Delete old test cases
    db.query(models.TestCase).filter(models.TestCase.problem_id == problem.id).delete()
    
    # Add new test cases
    for tc in problem_data.testcases:
        test_case = models.TestCase(
            problem_id=problem.id,
            input_data=tc.input_data,
            expected_output=tc.expected_output,
            marks_weight=tc.marks_weight
        )
        db.add(test_case)

    db.commit()
    db.refresh(problem)
    return problem

@router.delete("/problems/{problem_id}")
def delete_problem(
    problem_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_professor)
):
    problem = db.query(models.Problem).filter(models.Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Any professor can delete any problem (ownership not required)
    # Due to cascade="all, delete-orphan", testcases and submissions will be deleted automatically
    db.delete(problem)
    db.commit()
    return {"message": "Problem deleted successfully"}

@router.get("/submissions/{problem_id}", response_model=List[schemas.SubmissionResponse])
def get_problem_submissions(
    problem_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_professor)
):
    # Verify problem belongs to professor
    problem = db.query(models.Problem).filter(models.Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    if problem.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view these submissions")
        
    submissions = db.query(models.Submission).filter(models.Submission.problem_id == problem_id).all()
    return submissions

@router.get("/plagiarism/{problem_id}")
def check_plagiarism(
    problem_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_professor)
):
    # Retrieve all accepted submissions for a problem to check similarity
    # Real logic uses AST or diff tracking; mock placeholder
    submissions = db.query(models.Submission).filter(
        models.Submission.problem_id == problem_id, 
        models.Submission.result == "Accepted"
    ).all()
    
    # Normally we run our AST checks here and return high-match pairs
    # Returning a mock structure for the UI
    return {
        "problem_id": problem_id,
        "suspicious_pairs": [
            # { "student_1": "1001", "student_2": "1002", "similarity": 95 }
        ]
    }

@router.post("/upload-pdf")
async def extract_pdf_content(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_professor)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        contents = await file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))
        extracted_text = ""
        for page in pdf_reader.pages:
            extracted_text += page.extract_text() + "\n"
        return {"extracted_text": extracted_text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}")

@router.get("/analytics")
def get_analytics(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_professor)
):
    """
    Returns a matrix of student x problem marks for the professor analytics panel.
    Response: { problems: [...], students: [{name, marks:{pid:score}, total}, ...] }
    """
    return prof_helpers.get_all_student_marks(db)
