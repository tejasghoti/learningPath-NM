# app/routes/student_routes.py
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.schemas.student_schema import StudentCreate
from app.models.base_models import Student
from app.dependencies.common import get_logger
from app.database import get_session
from sqlmodel import select

router = APIRouter()

@router.post("/students")
def create_student(
    student_data: StudentCreate,
    logger=Depends(get_logger),
    session: Session = Depends(get_session)
):
    db_student = Student.model_validate(student_data)
    session.add(db_student)
    session.commit()
    session.refresh(db_student)
    print(f"Saved Student to Neon with ID {db_student.id}")

    return {
        "msg": "Student Saved to Database Successfully",
        "student": db_student
    }

@router.get("/students")
def get_all_students(session: Session = Depends(get_session)):
    students = session.exec(select(Student)).all()
    return students