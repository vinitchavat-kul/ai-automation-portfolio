import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# 1. เขียน function กำหนด mock data สภาพอากาศ
def get_weather(location: str) -> str:
    """ใช้สำหรับตรวจสอบสภาพอากาศของสถานที่หรือจังหวัดที่ผู้ใช้ถาม"""
    if location == "ชลบุรี":
        return "ฝนตกหนัก"
    else:
        return "แดดออก"

def main():
    # อ่านค่า API Key จาก Environment Variable
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("กรุณาตั้งค่าตัวแปรสภาพแวดล้อม GEMINI_API_KEY ก่อนใช้งาน (export GEMINI_API_KEY='your-key')")
        return
        
    genai.configure(api_key=api_key)

    # 2. ตั้งค่า system instruction
    instruction = (
        "คุณคือผู้ช่วยพยากรณ์อากาศที่น่ารักและเป็นกันเอง "
        "คุณต้องใช้ Tool (get_weather) เพื่อตรวจสอบสภาพอากาศทุกครั้งที่ผู้ใช้ถามสภาพอากาศเสมอ "
        "ห้ามคาดเดาสภาพอากาศเอาเองโดยเด็ดขาด"
    )

    # การนำฟังก์ชันไปใส่เป็น Tool ให้ใส่ในพารามิเตอร์ `tools`
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        tools=[get_weather], # <--- การใช้งาน Function Calling
        system_instruction=instruction
    )

    # 3. สร้างระบบแชท โดยตั้งค่า enable_automatic_function_calling=True ให้ SDK ไปรัน Tool ให้อัตโนมัติ
    chat = model.start_chat(enable_automatic_function_calling=True)

    print("AI Agent พยากรณ์อากาศพร้อมแล้ว! (พิมพ์ 'exit' เพื่อสิ้นสุดการคุย)")
    print("-" * 50)
    
    while True:
        user_input = input("You: ")
        
        # ถ้ารับคำว่า exit ให้จบโปรแกรม
        if user_input.strip().lower() == 'exit':
            print("Agent: ลาก่อน ขอให้อากาศดีตลอดทั้งวันนะ!")
            break
            
        try:
            # ส่งข้อความไปให้โมเดล
            response = chat.send_message(user_input)
            print(f"Agent: {response.text}")
        except Exception as e:
            print(f"รบกวนตรวจสอบ API KEY หรือ Network: {e}")

if __name__ == "__main__":
    main()
