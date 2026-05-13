# Coding Guidelines — AI Resume Matcher
> Senior Developer Standard | Python 3.10+

---

## 1. Python Version & Project Structure

- ใช้ **Python 3.10+** เสมอ (ใช้ match-case, union type `X | Y`, และ feature ใหม่ได้)
- โครงสร้างโปรเจกต์แบบ **Modular** — แต่ละไฟล์มีหน้าที่เดียวชัดเจน

```
ai-resume-matcher/
├── main.py              # Entry point เท่านั้น
├── config.py            # โหลด env และค่า config ทั้งหมด
├── matcher.py           # Logic การ match resume กับ JD
├── parser.py            # อ่านและแปลง resume/JD
├── ai_client.py         # ติดต่อ AI API (Gemini/Claude)
├── utils.py             # Helper functions ทั่วไป
├── .env                 # API Keys (ห้าม commit)
├── .env.example         # Template สำหรับทีม
└── requirements.txt
```

**กฎ:** ห้าม import ข้ามโมดูลแบบวนลูป (circular import) — ถ้า A ใช้ B แล้ว B ต้องไม่ใช้ A

---

## 2. API Key Management — python-dotenv เท่านั้น

**ห้าม hardcode API Key ในโค้ดเด็ดขาด**

### วิธีที่ถูกต้อง

```python
# config.py
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# ตรวจสอบทันทีตอน startup — fail fast ดีกว่า fail ตอน runtime
if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY is not set in .env")
```

```ini
# .env (ห้าม commit ขึ้น git)
GEMINI_API_KEY=your-key-here
CLAUDE_API_KEY=your-key-here
```

```ini
# .env.example (commit ได้ — ไม่มีค่าจริง)
GEMINI_API_KEY=
CLAUDE_API_KEY=
```

```
# .gitignore — บังคับมี
.env
```
ห้ามระบุชื่อโมเดล AI (เช่น gemini-x.x) ลงในไฟล์ Logic โดยตรง ทุกชื่อโมเดลต้องถูกประกาศเป็น Constant ใน config.py หรือดึงมาจาก .env เท่านั้น เพื่อให้ง่ายต่อการอัปเดตเวอร์ชันในที่เดียว

---

## 3. Error Handling สำหรับ AI API

ทุก call ที่ติดต่อ AI API **ต้องครอบด้วย try-except** เสมอ แยก error ตามประเภท

```python
# ai_client.py
import google.generativeai as genai
import logging
from config import GEMINI_API_KEY, DEFAULT_MODEL

logger = logging.getLogger(__name__)

def call_gemini(prompt: str, model: str = DEFAULT_MODEL) -> str | None:
    """
    ส่ง prompt ไปยัง Gemini API โดยใช้โมเดลที่กำหนดใน config.py และคืนค่า text response
    คืน None หากเกิด error ใดๆ
    """
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model_client = genai.GenerativeModel(model)
        response = model_client.generate_content(prompt)
        return response.text

    except genai.types.BlockedPromptException as e:
        # Prompt ถูก safety filter บล็อก
        logger.warning(f"Prompt blocked by safety filter: {e}")
        return None

    except genai.types.StopCandidateException as e:
        # Response หยุดก่อนจบเพราะ safety reasons
        logger.warning(f"Response stopped early: {e}")
        return None

    except Exception as e:
        # Network error, rate limit, invalid key ฯลฯ
        logger.error(f"Gemini API call failed: {type(e).__name__}: {e}")
        return None
```

**กฎเพิ่มเติม:**
- ใช้ `logging` แทน `print` สำหรับ error/warning เสมอ
- ฟังก์ชัน AI ที่ fail ต้องคืน `None` หรือ raise custom exception — ห้าม silent fail
- หากมี retry logic ให้ใช้ exponential backoff (ไม่ใช่ fixed sleep)

---

## 4. JSON Output — Raw JSON เท่านั้น

ฟังก์ชันใดที่ return JSON **ต้องบังคับ output ใน prompt** และ parse ให้เรียบร้อยก่อน return

### Prompt ที่ถูกต้อง

```python
def get_match_score(resume: str, job_description: str) -> dict | None:
    """
    วิเคราะห์ความเข้ากันของ resume กับ JD
    คืน dict หรือ None หาก parse ไม่ได้
    """
    prompt = f"""
    Analyze the match between the resume and job description below.

    IMPORTANT: Respond with RAW JSON only.
    - No markdown formatting
    - No code blocks (no ```)
    - No explanation text before or after
    - Start your response directly with {{

    Required JSON format:
    {{
        "match_score": <integer 0-100>,
        "matched_skills": [<list of strings>],
        "missing_skills": [<list of strings>],
        "summary": "<one sentence summary>"
    }}

    Resume:
    {resume}

    Job Description:
    {job_description}
    """

    raw = call_gemini(prompt)
    if not raw:
        return None

    return _parse_json_response(raw)


def _parse_json_response(raw: str) -> dict | None:
    """Parse JSON จาก AI response — รองรับกรณี AI แอบใส่ markdown มา"""
    import json
    import re

    # กรณี AI ดื้อใส่ ```json ... ``` มา — strip ออก
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}\nRaw: {raw[:200]}")
        return None
```

**กฎ:**
- ระบุใน prompt ว่า "RAW JSON only, no markdown, no explanation" ทุกครั้ง
- ต้อง validate/parse ก่อน return เสมอ — ห้าม return raw string แล้วให้ caller parse เอง
- ใส่ `_parse_json_response()` เป็น helper แยกต่างหาก

---

## 5. Code Readability & Comments

### หลักการ
- Comment อธิบาย **"ทำไม"** ไม่ใช่ **"ทำอะไร"** — code อ่านออกอยู่แล้วว่าทำอะไร
- ใส่ **docstring** ทุกฟังก์ชัน (อย่างน้อย 1 บรรทัด)
- ใช้ **type hints** ทุกฟังก์ชัน

### ตัวอย่างที่ดี

```python
def calculate_skill_overlap(resume_skills: list[str], jd_skills: list[str]) -> float:
    """คำนวณ % ของ skills ใน JD ที่ resume ครอบคลุม"""
    if not jd_skills:
        return 0.0

    # ใช้ set intersection เพื่อ case-insensitive matching
    resume_set = {s.lower() for s in resume_skills}
    jd_set = {s.lower() for s in jd_skills}

    matched = resume_set & jd_set  # & = intersection
    return len(matched) / len(jd_set) * 100
```

### ตัวอย่างที่ห้ามทำ

```python
# BAD: comment ซ้ำกับโค้ด, ไม่มี type hints, ไม่มี docstring
def calc(a, b):
    # loop through b
    for x in b:
        pass  # ...
```

### Naming Convention
| สิ่งที่ตั้งชื่อ | รูปแบบ | ตัวอย่าง |
|---|---|---|
| ฟังก์ชัน / ตัวแปร | `snake_case` | `match_score`, `parse_resume` |
| Class | `PascalCase` | `ResumeParser`, `JobMatcher` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_TOKENS`, `DEFAULT_MODEL` |
| Private helper | `_underscore_prefix` | `_parse_json_response` |

---

## Quick Checklist ก่อน Commit

- [ ] ไม่มี API Key หรือ secret ในโค้ด
- [ ] `.env` อยู่ใน `.gitignore`
- [ ] ทุก AI API call มี try-except ครอบ
- [ ] ฟังก์ชันที่ return JSON มี prompt บังคับ Raw JSON และ parse ก่อน return
- [ ] ทุกฟังก์ชันมี type hints และ docstring
- [ ] ใช้ `logging` แทน `print` สำหรับ error
