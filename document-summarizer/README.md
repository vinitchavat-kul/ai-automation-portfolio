# AI Document Summarizer

**AI Document Summarizer** is a powerful, terminal-based Python application that leverages the Google Gemini AI to analyze and summarize text. It automatically restructures large amounts of text into three concise sections: **Topic**, **Key Takeaways**, and a brief **Summary**, helping you digest information quickly and efficiently.

## Features

- **Text Input (Direct Paste):** Quickly paste any text directly into the terminal to get an instant summary.
- **Batch Processing:** Automatically read and process multiple `.txt` files from the `input/` folder in a single run. Successfully processed files are automatically archived into a `processed/` folder to prevent redundant operations, while their summaries are systematically saved in the `output/` folder.

## Tech Stack

- **[Python 3.x](https://www.python.org/):** Core programming language.
- **[Google Gemini API](https://ai.google.dev/):** Utilized for generating high-quality AI summaries.
- **[Rich](https://rich.readthedocs.io/):** Used for rendering beautiful, interactive, and colorful terminal outputs.
- **[python-dotenv](https://pypi.org/project/python-dotenv/):** For securely loading and managing environment variables.

## Installation & Usage

### 1. Prerequisites
Make sure you have Python installed on your system. You will also need to obtain a Google Gemini API key.

### 2. Setup Instructions
Navigate to the project directory and install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root of the `document-summarizer` directory and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Running the Application
Start the program by running:

```bash
python main.py
```

Follow the on-screen interactive menu to choose your desired processing mode (**Text Input** or **Batch Processing**).

## Folder Structure

```text
document-summarizer/
│
├── .env                  # Environment variables (contains GEMINI_API_KEY)
├── .gitignore            # Git ignored files and directories
├── main.py               # Main application entry point and interactive menu
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies for the project
│
├── input/                # Place your .txt files here for batch processing
├── output/               # Summarized results will be saved here as .txt files
├── processed/            # Original text files are moved here after successful summarization
│
└── src/                  # Source code modules
    ├── file_utils.py     # Utility functions for file handling operations
    └── summarizer.py     # Core functions handling the Gemini API requests
```
