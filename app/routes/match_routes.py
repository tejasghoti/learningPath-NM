# app/routes/match_routes.py
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.schemas.student_schema import StudentCreate
from app.database import get_session
from app.services.rule_engine import find_eligible_scholarships
from app.services.ai_roadmap import generate_roadmap

router = APIRouter()


@router.post("/match")
def match_student_to_scholarships(
    student_data: StudentCreate,
    session: Session = Depends(get_session)
):
    """
    Core endpoint that ties everything together:
    1. Takes a student profile
    2. Runs the Rule Engine to find eligible scholarships
    3. Sends results to Gemini AI to generate a personalized roadmap
    4. Returns everything in one response
    """

    # Step 1: Run the Rule Engine
    eligible = find_eligible_scholarships(
        student_caste=student_data.caste,
        student_income=student_data.income,
        student_state=student_data.state,
        student_gender=student_data.gender,
        student_course=student_data.course,
        session=session
    )

    if not eligible:
        return {
            "student": student_data.model_dump(),
            "eligible_scholarships": [],
            "message": "No matching scholarships found for this profile.",
            "ai_roadmap": None
        }

    # Step 2: Generate AI Roadmap using Gemini
    student_profile = student_data.model_dump()
    ai_roadmap = generate_roadmap(student_profile, eligible)

    # Step 3: Return combined response
    return {
        "student": student_profile,
        "eligible_scholarships": eligible,
        "total_matched": len(eligible),
        "ai_roadmap": ai_roadmap
    }
