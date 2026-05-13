from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

DEFAULT_MODEL = os.getenv("AI_MODEL", "gemini-2.5-flash") # ตั้งค่าเริ่มต้นเป็นตัวล่าสุด

# Fail fast — ดีกว่า error ตอน runtime ที่ไม่รู้ว่าเกิดจากอะไร
if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY is not set in .env")
