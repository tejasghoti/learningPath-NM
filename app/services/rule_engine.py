# app/services/rule_engine.py
from sqlmodel import Session, select
from app.models.base_models import Scholarship, EligibilityCriteria


def find_eligible_scholarships(student_caste: str, student_income: int,
                                student_state: str, student_gender: str,
                                student_course: str, session: Session):
    """
    Rule Engine: Checks every EligibilityCriteria row in the database
    and returns a list of scholarships the student qualifies for.

    Matching rules (a student qualifies if ALL conditions are met):
      - target_caste is "ALL" or matches the student's caste
      - max_income_limit >= student's income
      - target_state is "ALL" or matches the student's state
      - target_gender is "ALL" or matches the student's gender
      - target_course is "ALL" or matches the student's course
    """

    all_criteria = session.exec(select(EligibilityCriteria)).all()

    matched_scholarship_ids = set()

    for criteria in all_criteria:
        caste_ok = criteria.target_caste == "ALL" or criteria.target_caste == student_caste
        income_ok = criteria.max_income_limit >= student_income
        state_ok = criteria.target_state == "ALL" or criteria.target_state == student_state.upper()
        gender_ok = criteria.target_gender == "ALL" or criteria.target_gender == student_gender
        course_ok = criteria.target_course == "ALL" or criteria.target_course == student_course.upper()

        if caste_ok and income_ok and state_ok and gender_ok and course_ok:
            matched_scholarship_ids.add(criteria.scholarship_id)

    # Now fetch the actual Scholarship objects for matched IDs
    if not matched_scholarship_ids:
        return []

    scholarships = session.exec(
        select(Scholarship).where(Scholarship.id.in_(matched_scholarship_ids))
    ).all()

    # Attach criteria to each scholarship for context
    results = []
    for scholarship in scholarships:
        criteria_list = session.exec(
            select(EligibilityCriteria).where(
                EligibilityCriteria.scholarship_id == scholarship.id
            )
        ).all()
        results.append({
            "scholarship_id": scholarship.id,
            "name": scholarship.name,
            "provider": scholarship.provider_name,
            "criteria": [
                {
                    "target_caste": c.target_caste,
                    "max_income_limit": c.max_income_limit,
                    "target_state": c.target_state,
                    "target_gender": c.target_gender,
                    "target_course": c.target_course,
                }
                for c in criteria_list
            ],
        })

    return results
