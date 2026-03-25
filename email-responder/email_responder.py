# email_responder.py
# AI Email Responder - Portfolio Project 01

import google.generativeai as genai
import os
import json
import shutil
import glob
from datetime import datetime
from dotenv import load_dotenv

# ═══════════════════════════════
# SETUP
# ═══════════════════════════════
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ═══════════════════════════════
# FUNCTION 1: จัดหมวดหมู่ email
# ═══════════════════════════════
def categorize_email(email_text):
    prompt = f"""
    จัดหมวดหมู่ email นี้เป็น 1 หมวดเท่านั้น:
    - INQUIRY (สอบถามข้อมูล)
    - COMPLAINT (ร้องเรียน)
    - ORDER (สั่งซื้อ)
    - SUPPORT (ขอความช่วยเหลือ)
    - OTHER (อื่นๆ)

    Email: {email_text}

    ตอบแค่ชื่อหมวดเดียว ไม่ต้องอธิบาย
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# ═══════════════════════════════
# FUNCTION 2: สร้าง draft reply
# ═══════════════════════════════
def generate_reply(email_text, category):
    prompt = f"""
    คุณคือผู้ช่วยตอบ email มืออาชีพ
    
    หมวดหมู่ email: {category}
    
    Email ที่ได้รับ:
    {email_text}
    
    เขียน draft reply ภาษาไทย สุภาพ กระชับ
    ความยาวไม่เกิน 5 บรรทัด
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# ═══════════════════════════════
# FUNCTION 3: บันทึกผลลงไฟล์
# ═══════════════════════════════
def save_result(email_text, category, reply):
    # สร้าง folder manual ถ้ายังไม่มี
    os.makedirs("manual", exist_ok=True)
    
    # ตั้งชื่อไฟล์ตามเวลา
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"manual/reply_{timestamp}.txt"
    json_filename = f"manual/reply_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"=== EMAIL RECEIVED ===\n")
        f.write(f"{email_text}\n\n")
        f.write(f"=== CATEGORY ===\n")
        f.write(f"{category}\n\n")
        f.write(f"=== DRAFT REPLY ===\n")
        f.write(f"{reply}\n")
        
    summary = {
        "category": category,
        "reply_word_count": len(reply.split()),
        "timestamp": datetime.now().isoformat()
    }
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=4)
    
    return filename, json_filename

# ═══════════════════════════════
# FUNCTION 4: Batch Processing
# ═══════════════════════════════
def process_batch():
    # 1. สร้างโฟลเดอร์อัตโนมัติ
    for folder in ['batch/inbox', 'batch/processed', 'batch/replies']:
        os.makedirs(folder, exist_ok=True)
    
    # 2. ให้โปรแกรมสแกนไฟล์ .txt ทั้งหมดในโฟลเดอร์ 'batch/inbox'
    txt_files = glob.glob("batch/inbox/*.txt")
    
    if not txt_files:
        print("\nไม่พบไฟล์ใน batch/inbox")
        return
        
    for file_path in txt_files:
        filename = os.path.basename(file_path)
        print(f"\nกำลังอ่านไฟล์ {filename}...")
        
        # อ่านเนื้อหาในแต่ละไฟล์
        with open(file_path, "r", encoding="utf-8") as f:
            email_text = f.read()
            
        if not email_text.strip():
            print(f"ข้ามไฟล์ {filename} เนื่องจากไม่มีเนื้อหา")
            continue
            
        # Categorize & Generate Reply
        category = categorize_email(email_text)
        reply = generate_reply(email_text, category)
        
        # สร้างไฟล์ใหม่ในโฟลเดอร์ 'batch/replies' โดยตั้งชื่อไฟล์เดิมตามด้วย '_reply.txt'
        name_without_ext = os.path.splitext(filename)[0]
        reply_txt_filename = f"batch/replies/{name_without_ext}_reply.txt"
        reply_json_filename = f"batch/replies/{name_without_ext}_reply.json"
        
        with open(reply_txt_filename, "w", encoding="utf-8") as f:
            f.write(f"=== CATEGORY ===\n{category}\n\n")
            f.write(f"=== DRAFT REPLY ===\n{reply}\n")
            
        # สร้างไฟล์ _reply.json ด้วย
        summary = {
            "category": category,
            "reply_word_count": len(reply.split()),
            "timestamp": datetime.now().isoformat()
        }
        with open(reply_json_filename, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=4)
            
        print(f"สร้างคำตอบเสร็จแล้วสำหรับไฟล์ {filename}")
        
        # ย้ายไฟล์ต้นฉบับไปไว้ที่ 'batch/processed'
        dest_path = os.path.join("batch/processed", filename)
        if os.path.exists(dest_path):
            os.remove(dest_path)
        shutil.move(file_path, "batch/processed/")
        
    print("\nประมวลผล Batch เสร็จสิ้น!")

# ═══════════════════════════════
# MAIN: โปรแกรมหลัก
# ═══════════════════════════════
def main():
    print("=" * 40)
    print("   AI Email Responder")
    print("=" * 40)
    
    # สร้าง folder เผื่อไว้ก่อนเลย
    os.makedirs("manual", exist_ok=True)
    for folder in ['batch/inbox', 'batch/processed', 'batch/replies']:
        os.makedirs(folder, exist_ok=True)
        
    while True:
        print("\nเลือกโหมดการทำงาน:")
        print("1. พิมพ์อีเมลทีละฉบับ (Manual)")
        print("2. ประมวลผลจากโฟลเดอร์ inbox (Batch Processing)")
        print("3. ออกจากโปรแกรม")
        choice = input("กรุณาเลือก (1/2/3): ").strip()
        
        if choice == '1':
            while True:
                print("\nวาง email ที่ได้รับ แล้วกด Enter 2 ครั้ง (พิมพ์ 'exit' เพื่อกลับเมนูหลัก)")
                
                # รับ input หลายบรรทัด
                lines = []
                while True:
                    line = input()
                    if line == "":
                        break
                    lines.append(line)
                
                email_text = "\n".join(lines)
                
                if email_text.strip().lower() == "exit":
                    break
                    
                if not email_text.strip():
                    print("ไม่มีข้อความ กรุณาลองใหม่")
                    continue
                
                # ประมวลผล
                print("\nกำลังวิเคราะห์...")
                category = categorize_email(email_text)
                
                print(f"หมวดหมู่: {category}")
                print("\nกำลังสร้าง draft reply...")
                reply = generate_reply(email_text, category)
                
                # แสดงผล
                print("\n" + "=" * 40)
                print("DRAFT REPLY:")
                print("=" * 40)
                print(reply)
                
                # บันทึกไฟล์
                saved_txt, saved_json = save_result(email_text, category, reply)
                print(f"\nบันทึกผลไว้ที่:\n- {saved_txt}\n- {saved_json}")
                
        elif choice == '2':
            process_batch()
            
        elif choice == '3':
            print("\nจบการทำงานของโปรแกรม...")
            break
            
        else:
            print("เลือกไม่ถูกต้อง กรุณาลองใหม่")

# รันโปรแกรม
if __name__ == "__main__":
    main()