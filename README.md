# 🎓 AI-Powered Study Buddy & Personal Tutor

An intelligent tutoring system that helps students understand their study material deeply through AI-powered explanations, structured notes, and adaptive learning.

## ✨ Features

- 📚 **Multi-format Support**: Upload textbooks (PDF), notes (DOCX), slides (PPTX), and images (with OCR)
- 🧠 **Deep Understanding**: AI analyzes and comprehends all uploaded content
- 📝 **Structured Notes**: Automatically generates well-organized study notes with headings, bullet points, and clear explanations
- 💡 **Step-by-Step Explanations**: Breaks down complex concepts for beginners
- 🎯 **Practice Questions**: Generates questions from easy to hard with detailed solutions
- 🔄 **Adaptive Teaching**: Adjusts explanations based on subject, level, and student needs
- ⭐ **Smart Highlighting**: Marks important points, formulas, and common mistakes

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- OpenAI API key (or other LLM provider)

### Installation

1. Clone or navigate to the repository:
```bash
cd "c:\Users\Rhea Sushanth\FinalsArc"
```

2. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
copy .env.example .env
# Edit .env and add your API keys
```

5. Run the application:
```bash
python app.py
```

6. Open your browser to `http://localhost:8000`

## 📁 Project Structure

```
FinalsArc/
├── app.py                  # Main FastAPI application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
├── uploads/               # Uploaded files storage
├── processed/             # Processed content storage
├── core/
│   ├── ai_tutor.py       # Main AI tutor logic
│   ├── note_generator.py # Study notes generation
│   ├── question_gen.py   # Practice question generator
│   └── explainer.py      # Concept explanation engine
├── processors/
│   ├── pdf_processor.py  # PDF text extraction
│   ├── docx_processor.py # Word document processing
│   ├── pptx_processor.py # PowerPoint processing
│   └── ocr_processor.py  # Image OCR
├── utils/
│   ├── formatters.py     # Output formatting utilities
│   └── validators.py     # Input validation
└── frontend/
    ├── index.html        # Main UI
    ├── styles.css        # Styling
    └── script.js         # Frontend logic
```

## 🎯 Usage Guide

### 1. Upload Study Material
- Drag and drop or select files (PDF, DOCX, PPTX, images)
- System processes and extracts all content
- Content is analyzed by AI

### 2. Generate Study Notes
- Click "Generate Notes" for any uploaded material
- Get structured notes with:
  - Clear headings and organization
  - Simple → detailed explanations
  - Examples and analogies
  - Important highlights

### 3. Ask Questions
- Type any question about your material
- Get multiple explanation approaches
- Request simpler explanations if needed

### 4. Practice with Quizzes
- Generate practice questions (easy/medium/hard)
- Get instant feedback
- See step-by-step solutions

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **AI/LLM**: OpenAI GPT-4 / Anthropic Claude
- **Document Processing**: 
  - PyPDF2 (PDF)
  - python-docx (DOCX)
  - python-pptx (PPTX)
  - pytesseract (OCR)
- **Frontend**: HTML5, CSS3, JavaScript
- **Storage**: Local file system (can be extended to cloud)

## 🔑 Environment Variables

Create a `.env` file with:

```
OPENAI_API_KEY=your_openai_api_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional
MAX_FILE_SIZE=10  # in MB
UPLOAD_FOLDER=uploads
```

## 📚 API Endpoints

- `POST /api/upload` - Upload study materials
- `GET /api/materials` - List all uploaded materials
- `POST /api/generate-notes` - Generate structured notes
- `POST /api/ask` - Ask a question
- `POST /api/generate-quiz` - Generate practice questions
- `DELETE /api/material/{id}` - Delete material

## 🤝 Contributing

This is a personal study tool. Feel free to customize it for your needs!

## 📄 License

MIT License - Free to use and modify

## 🆘 Support

For issues or questions, check the documentation or create an issue in the repository.

---

**Happy Learning! 🎓✨**
