# app/routes/scholarship_routes.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.models.base_models import Scholarship, EligibilityCriteria
from app.database import get_session

router = APIRouter()


# ─── POST: Add a new Scholarship with its Eligibility Criteria ───
@router.post("/scholarships")
def create_scholarship(
    name: str,
    provider_name: str,
    target_caste: str,
    max_income_limit: int,
    target_state: str = "ALL",
    target_gender: str = "ALL",
    target_course: str = "ALL",
    session: Session = Depends(get_session)
):
    # 1. Create the Scholarship record
    scholarship = Scholarship(name=name, provider_name=provider_name)
    session.add(scholarship)
    session.commit()
    session.refresh(scholarship)

    # 2. Create the EligibilityCriteria linked to this scholarship via Foreign Key
    criteria = EligibilityCriteria(
        scholarship_id=scholarship.id,
        target_caste=target_caste,
        max_income_limit=max_income_limit,
        target_state=target_state,
        target_gender=target_gender,
        target_course=target_course
    )
    session.add(criteria)
    session.commit()
    session.refresh(criteria)

    return {
        "msg": "Scholarship Created",
        "scholarship": scholarship,
        "criteria": criteria
    }


# ─── GET: List all Scholarships ───
@router.get("/scholarships")
def get_all_scholarships(session: Session = Depends(get_session)):
    scholarships = session.exec(select(Scholarship)).all()
    return scholarships


# ─── GET: Get a specific Scholarship with its criteria ───
@router.get("/scholarships/{scholarship_id}")
def get_scholarship(scholarship_id: int, session: Session = Depends(get_session)):
    scholarship = session.get(Scholarship, scholarship_id)
    if not scholarship:
        return {"error": "Scholarship not found"}
    
    # Fetch the related criteria using the Foreign Key relationship
    criteria = session.exec(
        select(EligibilityCriteria).where(
            EligibilityCriteria.scholarship_id == scholarship_id
        )
    ).all()
    
    return {
        "scholarship": scholarship,
        "criteria": criteria
    }
