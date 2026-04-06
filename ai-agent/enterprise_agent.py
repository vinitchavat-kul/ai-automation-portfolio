import sys
import json
import base64
import io
import os
import warnings

# Suppress all warnings before importing genai to catch import-time warnings
warnings.filterwarnings("ignore")

import google.generativeai as genai
from dotenv import load_dotenv

# Force UTF-8 output to prevent garbled Thai characters
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 3. Mock functions สำหรับใช้งานเป็น Tools
def check_inventory(product_name: str, quantity: int) -> str:
    """ตรวจสอบจำนวนสินค้าในคลัง"""
    if "เหล็กเส้น" in product_name:
        return "มีของ 100 ตัน"
    else:
        return "ของหมด"

def calculate_shipping(province: str) -> str:
    """คำนวณค่าส่งจากจังหวัดที่ต้องจัดส่ง"""
    if "ระยอง" in province:
        return "ค่าส่ง 2000 บาท"
    elif "ชลบุรี" in province:
        return "ค่าส่ง 500 บาท"
    else:
        return "ค่าส่ง 5000 บาท"

def main():
    try:
        # Load environment variables
        load_dotenv()
        
        # 1. รับ input เป็น base64 
        if len(sys.argv) > 1:
            encoded_text = sys.argv[1]
        else:
            encoded_text = sys.stdin.read().strip()
            
        if not encoded_text:
            print(json.dumps({"status": "error", "message": "No base64 input provided"}, ensure_ascii=False))
            return
            
        # 2. Decode Base64 เป็น text
        decoded_bytes = base64.b64decode(encoded_text)
        text = decoded_bytes.decode('utf-8')
        
        # เชื่อมต่อ API
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in environment variables.")
            
        genai.configure(api_key=api_key)
        
        # Instruction สำหรับ AI Agent ฝ่ายขายและคลังสินค้า
        instruction = (
            "คุณคือ AI Agent ผู้ช่วยฝ่ายขายและคลังสินค้า "
            "หน้าที่ของคุณคืออ่านอีเมลของลูกค้า วิเคราะห์ว่าลูกค้าต้องการสินค้าอะไร จำนวนเท่าไหร่ และจัดส่งไปที่จังหวัดใด "
            "ใช้ Tools ตรวจสอบรหัสหรือชื่อสินค้า (check_inventory) และค่าขนส่ง (calculate_shipping) ทุกครั้ง "
            "จากนั้นสรุปข้อมูลและผลลัพธ์จาก Tools ทั้งหมด "
            "และต้องสร้างเนื้อหาอีเมลร่างตอบกลับลูกค้าด้วยข้อมูลที่คุณมีให้ครบถ้วน "
            "ข้อมูลใน JSON ต้องไม่อยู่ใน markdown หรือมีคำอธิบายอื่นๆ นอกเหนือจาก object JSON"
        )
        
        # เนื่องจาก Gemini API ไม่อนุญาตให้ใช้ Function Calling พร้อมกับระบุ response_mime_type="application/json" ในโมเดลเดียวกัน
        # จึงต้องแบ่งการทำงานออกเป็น 2 ขั้นตอน: ขั้นแรกให้ Agent คิดและใช้ Tools, ขั้นที่สองให้จัด Format เป็น JSON ตามที่บังคับ

        # ขั้นที่ 1: ตั้งค่า Model สำหรับการใช้งาน Tools
        tools_model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            tools=[check_inventory, calculate_shipping],
            system_instruction=instruction
        )
        
        # เรียกให้ model รัน tool อัตโนมัติและส่งข้อความไปวิเคราะห์หาข้อมูล
        chat = tools_model.start_chat(enable_automatic_function_calling=True)
        agent_response = chat.send_message(text)

        # ขั้นที่ 2: ตั้งค่า Model เพื่อบังคับให้ Output ออกมาเป็นรูปแบบ JSON เสมอ
        json_model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        
        json_prompt = f"จัดรูปแบบข้อมูลนี้ให้อยู่ในรูปแบบ JSON เท่านั้น ห้ามมีข้อความอธิบายใดๆ:\n{agent_response.text}"
        response = json_model.generate_content(json_prompt)
        
        # 4. ลบ Markdown (ถ้ามีหลุดมา) เพื่อบังคับให้ print เป็น Raw JSON เท่านั้น
        out_text = response.text.strip()
        if out_text.startswith("```json"):
            out_text = out_text[7:]
        if out_text.startswith("```"):
            out_text = out_text[3:]
        if out_text.endswith("```"):
            out_text = out_text[:-3]
            
        # พิมพ์ลัพธ์ออกเป็น Raw JSON ให้ n8n นำไปใช้งาน
        print(out_text.strip())
        
    except Exception as e:
        error_output = {
            "status": "error",
            "message": str(e)
        }
        print(json.dumps(error_output, ensure_ascii=False))

if __name__ == "__main__":
    main()
