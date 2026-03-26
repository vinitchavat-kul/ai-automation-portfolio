import os
import sys
import time
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

# Load environment variables FIRST
load_dotenv()

# We import the src modules after loading dotenv to ensure they can access the API key
from src.summarizer import generate_summary
from src.file_utils import get_txt_files, read_text, save_summary, move_to_processed

console = Console()

def process_direct_text():
    console.print("\n[bold cyan]=== โหมดพิมพ์/วางข้อความเอง ===[/bold cyan]")
    console.print("กรุณาพิมพ์หรือวางข้อความ (กด Enter จากนั้นพิมพ์ 'DONE' ในบรรทัดใหม่เมื่อเสร็จสิ้น):")
    
    lines = []
    while True:
        line = input()
        if line.strip().upper() == 'DONE':
            break
        lines.append(line)
        
    text = "\n".join(lines).strip()
    if not text:
        console.print("[red]ข้อความว่างเปล่า ยกเลิกการประมวลผล[/red]")
        return
        
    with console.status("[bold green]กำลังเรียก Gemini API เพื่อสรุปข้อความ..."):
        try:
            summary = generate_summary(text)
        except Exception as e:
            console.print(f"[bold red]Error:[/] {e}")
            return
            
    # Save output to file instead of displaying
    filename = f"direct_input_{int(time.time())}.txt"
    saved_path = save_summary(filename, summary, "output")
    console.print(f"\n[green]✅ บันทึกผลลัพธ์ลงที่:[/] {saved_path}")

def process_folder():
    console.print("\n[bold cyan]=== โหมดอ่านจาก Folder (Batch Processing) ===[/bold cyan]")
    console.print("[italic white]โปรแกรมจะอ่านไฟล์จากโฟลเดอร์ 'input/' โดยอัตโนมัติ...[/italic white]")
    
    input_dir = "input"
    files = get_txt_files(input_dir)
        
    if not files:
        console.print(f"[yellow]⚠️ ไม่พบไฟล์ .txt ในโฟลเดอร์ '{input_dir}/'[/yellow]")
        console.print(f"[white]คำแนะนำ: นำไฟล์ .txt ไปวางในโฟลเดอร์ '{os.path.abspath(input_dir)}' แล้วลองใหม่[/white]")
        return
        
    console.print(f"[green]พบไฟล์ .txt จำนวน {len(files)} ไฟล์[/green]")
    
    for i, file_path in enumerate(files, 1):
        filename = os.path.basename(file_path)
        console.print(f"\n[bold blue]กำลังประมวลผลไฟล์ ({i}/{len(files)}):[/bold blue] {filename}")
        
        try:
            content = read_text(file_path)
            if not content.strip():
                console.print("[yellow]-> ไฟล์ว่างเปล่า ข้าม...[/yellow]")
                continue
                
            with console.status("[green]กำลังรวบรวมบทสรุปจากโมเดล..."):
                summary = generate_summary(content)
                
            # Save it output directory relative to where main is run
            saved_path = save_summary(filename, summary, "output")
            
            # Move original file to processed folder
            processed_path = move_to_processed(file_path, "processed")
            
            console.print(f"[green]✅ บันทึกผลลัพธ์ลงที่:[/] {saved_path}")
            console.print(f"[blue]📦 ย้ายไฟล์ต้นฉบับไปที่:[/] {processed_path}")
            
        except Exception as e:
            console.print(f"[bold red]Error กับไฟล์ {filename}:[/] {e}")

def main():
    console.print(Panel.fit(
        "[bold magenta]Document Summarizer[/bold magenta]\n"
        "Powered by Python & Google Gemini API", 
        border_style="cyan"
    ))
    
    while True:
        console.print("\n[bold yellow]เมนูหลัก:[/bold yellow]")
        console.print("1. วางข้อความ (Text Input)")
        console.print("2. อ่านจากโฟลเดอร์ (Batch Processing)")
        console.print("3. ออกจากโปรแกรม (Exit)")
        
        choice = Prompt.ask("กรุณาเลือกเมนู", choices=["1", "2", "3"])
        
        if choice == "1":
            process_direct_text()
        elif choice == "2":
            process_folder()
        elif choice == "3":
            console.print("[cyan]ลาก่อน![/cyan]")
            sys.exit(0)
        else:
            console.print("[red]⚠️ กรุณาเลือก 1, 2, หรือ 3 เท่านั้น[/red]")

if __name__ == "__main__":
    main()
