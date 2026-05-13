import logging

from ai_client import _parse_json_response, call_gemini

logger = logging.getLogger(__name__)


class JobMatcher:
    """วิเคราะห์ความเข้ากันได้ระหว่าง resume กับ job description โดยใช้ Gemini"""

    def match(self, resume_text: str, jd_text: str) -> dict | None:
        """
        ส่ง resume และ JD ให้ Gemini วิเคราะห์ความเข้ากันได้

        Args:
            resume_text: ข้อความ resume ของผู้สมัคร
            jd_text: ข้อความประกาศรับสมัครงาน

        Returns:
            dict ที่มี match_score_percentage, missing_skills,
            matching_keywords, cover_letter_draft
            หรือ None หาก AI call หรือ JSON parse ล้มเหลว
        """
        if not resume_text or not jd_text:
            logger.error("resume_text และ jd_text ต้องไม่เป็นค่าว่าง")
            return None

        prompt = f"""
You are an expert technical recruiter. Analyze the match between the resume and job description below.

IMPORTANT: Respond with RAW JSON only.
- No markdown formatting
- No code blocks (no ```)
- No explanation text before or after
- Start your response directly with {{

Required JSON format:
{{
    "match_score_percentage": <integer 0-100>,
    "matching_keywords": [<list of skills/keywords found in both resume and JD>],
    "missing_skills": [<list of required skills from JD not found in resume>],
    "cover_letter_draft": "<a concise, professional cover letter draft tailored to this JD>"
}}

Resume:
{resume_text}

Job Description:
{jd_text}
"""

        raw = call_gemini(prompt)
        if not raw:
            # call_gemini คืน None — error ถูก log ไปแล้วใน ai_client
            return None

        result = _parse_json_response(raw)
        if result is None:
            return None

        return _validate_match_result(result)


def _validate_match_result(data: dict) -> dict | None:
    """
    ตรวจสอบว่า dict จาก AI มี keys และ types ครบถ้วนตามที่กำหนด
    คืน None หากโครงสร้างไม่ถูกต้อง เพื่อป้องกัน KeyError ที่ caller
    """
    required_keys = {
        "match_score_percentage": int,
        "matching_keywords": list,
        "missing_skills": list,
        "cover_letter_draft": str,
    }

    for key, expected_type in required_keys.items():
        if key not in data:
            logger.error(f"AI response missing required key: '{key}'")
            return None
        if not isinstance(data[key], expected_type):
            logger.error(
                f"Key '{key}' has wrong type: "
                f"expected {expected_type.__name__}, got {type(data[key]).__name__}"
            )
            return None

    # match_score ต้องอยู่ในช่วง 0-100
    score = data["match_score_percentage"]
    if not (0 <= score <= 100):
        logger.error(f"match_score_percentage out of range: {score}")
        return None

    return data
