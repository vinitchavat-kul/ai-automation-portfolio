# AI Email Responder

## Overview
**AI Email Responder** is an intelligent system designed to streamline customer support and email management. It automatically reads incoming emails, categorizes them based on their content (e.g., inquiries, complaints, orders, support requests), and generates appropriate, polite draft replies using AI.

## Features
- **Manual Mode**: Paste individual emails directly into the console to instantly receive a categorized result and a drafted response.
- **Batch Mode**: Automate bulk processing by placing email `.txt` files into the `batch/inbox` folder. The system will process all files sequentially, generate replies, save JSON summaries, and seamlessly organize processed files.

## Tech Stack
- **Python 3.x**
- **Google Generative AI (Gemini API)**: Powers the categorization and drafting engine (`gemini-2.5-flash`).
- **python-dotenv**: For secure environment variable management.

## Installation and Usage

1. **Clone the repository** (or download the source code):
   ```bash
   git clone <repository-url>
   cd email-responder
   ```

2. **Install the dependencies**:
   Ensure you have installed the required Python libraries:
   ```bash
   pip install google-generativeai python-dotenv
   ```

3. **Set up the Environment Variable**:
   Create a `.env` file in the root directory and add your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Run the Application**:
   ```bash
   python email_responder.py
   ```
   Follow the interactive CLI menu to choose between Manual Mode (1) or Batch Mode (2).

## Folder Structure
```text
email-responder/
├── email_responder.py    # Main application script
├── .env                  # Environment variables (API Key) - ignored by git
├── manual/               # Output folder for Manual Mode (.txt and .json replies)
└── batch/                # Root folder for Batch Mode operations
    ├── inbox/            # Drop incoming email .txt files here
    ├── processed/        # Original emails moved here after processing
    └── replies/          # Auto-generated .txt and .json drafting results
```
