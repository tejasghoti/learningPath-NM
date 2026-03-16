# app/services/ai_roadmap.py
import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


def generate_roadmap(student_profile: dict, eligible_scholarships: list) -> dict:
    """
    Uses Google Gemini (free tier) to generate a personalized
    scholarship application roadmap for the student.

    Args:
        student_profile: dict with caste, income, state, gender, course
        eligible_scholarships: list of matched scholarship dicts from rule engine

    Returns:
        A structured JSON roadmap with steps, deadlines, and documents needed.
    """

    if not GEMINI_API_KEY:
        return {
            "error": "GEMINI_API_KEY not set in environment variables. Using fallback roadmap.",
            "fallback_roadmap": _generate_fallback_roadmap(student_profile, eligible_scholarships)
        }

    client = genai.Client(api_key=GEMINI_API_KEY)

    scholarship_text = ""
    for s in eligible_scholarships:
        scholarship_text += f"\n- {s['name']} by {s['provider']}"
        for c in s.get("criteria", []):
            scholarship_text += f"\n  Eligibility: Caste={c['target_caste']}, MaxIncome={c['max_income_limit']}, State={c['target_state']}, Gender={c['target_gender']}, Course={c['target_course']}"

    prompt = f"""You are a scholarship advisor AI. A student needs a personalized roadmap to apply for scholarships they are eligible for.

STUDENT PROFILE:
- Caste: {student_profile['caste']}
- Annual Family Income: ₹{student_profile['income']}
- State: {student_profile['state']}
- Gender: {student_profile['gender']}
- Course: {student_profile['course']}

ELIGIBLE SCHOLARSHIPS:{scholarship_text}

Generate a detailed, step-by-step application roadmap in the following JSON format. Be specific with realistic deadlines and document names relevant to Indian scholarship applications:

{{
  "student_summary": "Brief description of the student's profile",
  "total_scholarships_matched": <number>,
  "roadmap": [
    {{
      "step_number": 1,
      "title": "Step title",
      "description": "What to do in this step",
      "documents_needed": ["list of specific documents"],
      "estimated_time": "e.g., 2-3 days",
      "tips": "Helpful advice for this step"
    }}
  ],
  "priority_scholarship": "Name of the most beneficial scholarship to apply first",
  "general_tips": ["list of general scholarship application tips"]
}}

Return ONLY valid JSON, no markdown formatting or code blocks."""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        text = response.text.strip()

        # Clean up potential markdown code block wrapping
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        roadmap = json.loads(text)
        return roadmap

    except json.JSONDecodeError:
        return {
            "raw_response": response.text if response else "No response",
            "error": "AI returned non-JSON response, showing raw text"
        }
    except Exception as e:
        return {
            "error": f"Gemini API error: {str(e)}",
            "fallback_roadmap": _generate_fallback_roadmap(student_profile, eligible_scholarships)
        }


def _generate_fallback_roadmap(student_profile: dict, eligible_scholarships: list) -> dict:
    """
    Generates a basic roadmap without AI, as a fallback.
    """
    steps = []
    step_num = 1

    steps.append({
        "step_number": step_num,
        "title": "Gather Basic Documents",
        "description": "Collect your caste certificate, income certificate, domicile, marksheets, and Aadhaar card.",
        "documents_needed": ["Caste Certificate", "Income Certificate", "Domicile Certificate",
                             "10th & 12th Marksheets", "Aadhaar Card", "Bank Passbook"],
        "estimated_time": "3-5 days",
    })
    step_num += 1

    for s in eligible_scholarships:
        steps.append({
            "step_number": step_num,
            "title": f"Apply for: {s['name']}",
            "description": f"Visit the National Scholarship Portal (NSP) or the {s['provider']} website. Fill in details and upload documents.",
            "documents_needed": ["All documents from Step 1", "Passport-size photo", "College admission letter"],
            "estimated_time": "1-2 days per application",
        })
        step_num += 1

    return {
        "student_summary": f"{student_profile['gender']} {student_profile['caste']} student from {student_profile['state']} pursuing {student_profile['course']}",
        "total_scholarships_matched": len(eligible_scholarships),
        "roadmap": steps,
        "general_tips": [
            "Apply before the deadline — don't wait until the last day",
            "Keep scanned copies of all documents ready",
            "Track your application status on NSP regularly",
        ],
    }
