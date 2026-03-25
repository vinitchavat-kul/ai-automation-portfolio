# hello_ai.py
# โปรเจกต์แรก: ทดสอบคุยกับ Gemini API

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')  # แก้ภาษาไทย

import google.generativeai as genai

# ใส่ API Key ของคุณตรงนี้
API_KEY = "AIzaSyAZXiEnMggQcoLVEqprlz-a8OAqO1B9q6Y"

# เชื่อมต่อกับ Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ส่งคำถามไปหา Gemini
question = "แนะนำตัวเองหน่อยว่าคุณคือใคร ทำอะไรได้บ้าง ตอบเป็นภาษาไทย"
response = model.generate_content(question)

# แสดงผลลัพธ์
print("=== Gemini ตอบว่า ===")
print(response.text)