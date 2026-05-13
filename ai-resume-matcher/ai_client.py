import json
import logging
import re

import google.generativeai as genai

from config import DEFAULT_MODEL, GEMINI_API_KEY

logger = logging.getLogger(__name__)


def call_gemini(prompt: str, model: str = DEFAULT_MODEL) -> str | None:
    """
    ส่ง prompt ไปยัง Gemini API และคืนค่า text response
    คืน None หากเกิด error ใดๆ
    """
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model_client = genai.GenerativeModel(model)
        response = model_client.generate_content(prompt)
        return response.text

    except genai.types.BlockedPromptException as e:
        # Prompt ถูก safety filter บล็อก — ไม่ใช่ bug ของโค้ด
        logger.warning(f"Prompt blocked by safety filter: {e}")
        return None

    except genai.types.StopCandidateException as e:
        # Response หยุดกลางคันเพราะ safety reasons
        logger.warning(f"Response stopped early: {e}")
        return None

    except Exception as e:
        # Network error, rate limit, invalid key ฯลฯ
        logger.error(f"Gemini API call failed: {type(e).__name__}: {e}")
        return None


def _parse_json_response(raw: str) -> dict | None:
    """Parse JSON จาก AI response — รองรับกรณี AI แอบใส่ markdown มา"""
    # Strip ```json ... ``` ที่ AI อาจแนบมาแม้ถูกสั่งไม่ให้ใส่
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}\nRaw: {raw[:200]}")
        return None
