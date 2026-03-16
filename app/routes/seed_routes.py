# app/routes/seed_routes.py
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.models.base_models import Scholarship, EligibilityCriteria
from app.database import get_session

router = APIRouter()

@router.post("/seed")
def seed_scholarships(session: Session = Depends(get_session)):
    scholarships_data = [
        {
            "name": "Post Matric Scholarship for SC Students",
            "provider_name": "Ministry of Social Justice & Empowerment",
            "criteria": [
                {"target_caste": "SC", "max_income_limit": 250000, "target_state": "ALL", "target_gender": "ALL", "target_course": "ALL"}
            ]
        },
        {
            "name": "Post Matric Scholarship for ST Students",
            "provider_name": "Ministry of Tribal Affairs",
            "criteria": [
                {"target_caste": "ST", "max_income_limit": 300000, "target_state": "ALL", "target_gender": "ALL", "target_course": "ALL"}
            ]
        },
        {
            "name": "Post Matric Scholarship for OBC Students",
            "provider_name": "Ministry of Social Justice & Empowerment",
            "criteria": [
                {"target_caste": "OBC", "max_income_limit": 100000, "target_state": "ALL", "target_gender": "ALL", "target_course": "ALL"}
            ]
        },
        {
            "name": "AICTE Pragati Scholarship for Girls",
            "provider_name": "AICTE",
            "criteria": [
                {"target_caste": "ALL", "max_income_limit": 800000, "target_state": "ALL", "target_gender": "FEMALE", "target_course": "B.TECH"}
            ]
        },
        {
            "name": "NSP Merit Scholarship for Minorities",
            "provider_name": "Ministry of Minority Affairs",
            "criteria": [
                {"target_caste": "ALL", "max_income_limit": 200000, "target_state": "ALL", "target_gender": "ALL", "target_course": "ALL"}
            ]
        },
        {
            "name": "Maharashtra State OBC Scholarship",
            "provider_name": "Govt. of Maharashtra",
            "criteria": [
                {"target_caste": "OBC", "max_income_limit": 150000, "target_state": "MAHARASHTRA", "target_gender": "ALL", "target_course": "ALL"}
            ]
        },
    ]

    count = 0
    for data in scholarships_data:
        scholarship = Scholarship(name=data["name"], provider_name=data["provider_name"])
        session.add(scholarship)
        session.commit()
        session.refresh(scholarship)

        for c in data["criteria"]:
            criteria = EligibilityCriteria(scholarship_id=scholarship.id, **c)
            session.add(criteria)

        session.commit()
        count += 1

    return {"msg": f"Seeded {count} scholarships successfully!"}
