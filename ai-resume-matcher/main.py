import json
import logging
import sys
from pathlib import Path

from matcher import JobMatcher

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

RESUME_FILE = Path("my_resume.txt")
JD_FILE = Path("job_description.txt")
COVER_LETTER_FILE = Path("generated_cover_letter.txt")


def _read_file(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            logger.error("ไฟล์ '%s' ว่างเปล่า — กรุณาใส่ข้อมูลแล้วลองใหม่อีกครั้ง", path)
            return None
        return text
    except OSError as e:
        logger.error("อ่านไฟล์ '%s' ไม่ได้: %s", path, e)
        return None


def _ensure_input_files() -> bool:
    missing = [p for p in (RESUME_FILE, JD_FILE) if not p.exists()]
    if not missing:
        return True

    for path in missing:
        try:
            path.write_text("", encoding="utf-8")
            logger.warning("สร้างไฟล์ '%s' แล้ว — กรุณาเพิ่มข้อมูลลงในไฟล์นี้ก่อนรันใหม่", path)
        except OSError as e:
            logger.error("สร้างไฟล์ '%s' ไม่ได้: %s", path, e)

    return False


def _save_cover_letter(text: str) -> None:
    try:
        COVER_LETTER_FILE.write_text(text, encoding="utf-8")
        logger.info("บันทึก cover letter ไปที่ '%s' เรียบร้อยแล้ว", COVER_LETTER_FILE)
    except OSError as e:
        logger.error("บันทึกไฟล์ '%s' ไม่ได้: %s", COVER_LETTER_FILE, e)


if __name__ == "__main__":
    if not _ensure_input_files():
        logger.error("กรุณาเพิ่มข้อมูลลงในไฟล์ที่สร้างขึ้น แล้วรันโปรแกรมอีกครั้ง")
        sys.exit(1)

    resume_text = _read_file(RESUME_FILE)
    jd_text = _read_file(JD_FILE)

    if resume_text is None or jd_text is None:
        sys.exit(1)

    matcher = JobMatcher()

    logger.info("กำลังวิเคราะห์ความเข้ากันได้ระหว่าง resume กับ JD...")
    result = matcher.match(resume_text=resume_text, jd_text=jd_text)

    if result is None:
        logger.error("ไม่สามารถวิเคราะห์ผลได้ — กรุณาตรวจสอบ logs ข้างต้น")
        sys.exit(1)

    print("\n========== Match Analysis Result ==========")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("===========================================\n")

    cover_letter = result.get("cover_letter_draft", "")
    if cover_letter:
        _save_cover_letter(cover_letter)
    else:
        logger.warning("ไม่พบ 'cover_letter_draft' ในผลลัพธ์ — ไม่มีการบันทึกไฟล์")
