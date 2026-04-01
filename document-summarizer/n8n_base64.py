import sys
import json
import base64
import io
from dotenv import load_dotenv

# Force UTF-8 output to prevent garbled Thai characters in n8n (Windows context)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables before importing modules that need them
load_dotenv()

from src.summarizer import generate_summary

def main():
    try:
        # Read encoded text from argument if provided, otherwise from stdin
        if len(sys.argv) > 1:
            encoded_text = sys.argv[1]
        else:
            encoded_text = sys.stdin.read().strip()
            
        if not encoded_text:
            print(json.dumps({"success": False, "error": "No base64 input provided"}))
            return
            
        # Decode Base64 string to text
        decoded_bytes = base64.b64decode(encoded_text)
        text = decoded_bytes.decode('utf-8')
        
        # Call the summarizer function
        summary = generate_summary(text)
        
        # Output result as JSON for n8n
        output = {
            "success": True,
            "summary": summary
        }
        
        # ensure_ascii=False helps properly display Thai characters in JSON
        print(json.dumps(output, ensure_ascii=False))
        
    except Exception as e:
        error_output = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(error_output, ensure_ascii=False))

if __name__ == "__main__":
    main()
