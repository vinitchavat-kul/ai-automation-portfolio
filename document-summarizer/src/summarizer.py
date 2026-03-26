import os
from google import genai
from google.genai import types

def generate_summary(text: str) -> str:
    """
    Calls the Gemini API to format the summary into 3 sections:
    หัวข้อ (Topic), ใจความสำคัญ (Key Takeaways), and สรุป (Summary).
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment or .env file.")

    client = genai.Client(api_key=api_key)
    
    prompt = f"""
Please summarize the following text. You MUST output the response in the exact same language as the original text (Thai or English).
Format the output strictly into these 3 sections (Keep the section names exactly as shown, use Thai or English depending on context but the structure must have these 3 parts):
1. หัวข้อ (Topic) 1 บรรทัด
2. ใจความสำคัญ (Key Takeaways) 3-5 bullet points
3. สรุป (Summary) 2-3 ประโยค ไม่ว่า input จะยาวแค่ไหน

Text to summarize:
{text}
"""
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    
    return response.text
