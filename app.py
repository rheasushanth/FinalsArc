"""
AI-Powered Study Buddy & Personal Tutor
FastAPI Backend Server
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import uuid
import shutil
from dotenv import load_dotenv

from core import AITutor
from processors import DocumentProcessor
from utils import FileValidator, InputValidator, ResponseFormatter

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Study Buddy",
    description="AI-powered personal tutor for comprehensive learning",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
PROCESSED_FOLDER = os.getenv('PROCESSED_FOLDER', 'processed')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Set max file size from env
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10))
FileValidator.set_max_file_size(MAX_FILE_SIZE)

# Initialize components
ai_tutor = AITutor()
doc_processor = DocumentProcessor(
    tesseract_path=os.getenv('TESSERACT_PATH')
)

# Pydantic models for request/response
class QuestionRequest(BaseModel):
    question: str
    material_id: Optional[str] = None
    level: Optional[str] = "intermediate"


class SimplerRequest(BaseModel):
    original_explanation: str
    question: str


class NotesRequest(BaseModel):
    material_id: str
    subject: Optional[str] = None
    level: Optional[str] = "intermediate"
    focus: Optional[str] = "concept-oriented"


class QuizRequest(BaseModel):
    material_id: str
    num_questions: Optional[int] = 5
    difficulty: Optional[str] = "mixed"
    subject: Optional[str] = None


class MultipleApproachesRequest(BaseModel):
    concept: str


# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the frontend"""
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <body>
                <h1>🎓 AI Study Buddy API</h1>
                <p>Backend is running! Frontend not found.</p>
                <p>Access the API documentation at <a href="/docs">/docs</a></p>
            </body>
        </html>
        """)


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Study Buddy",
        "version": "1.0.0"
    }


@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    subject: Optional[str] = Form(None)
):
    """
    Upload and process a study material file
    
    - **file**: File to upload (PDF, DOCX, PPTX, or image)
    - **subject**: Subject area (optional)
    """
    try:
        # Generate unique ID
        material_id = str(uuid.uuid4())
        
        # Save uploaded file
        file_extension = os.path.splitext(file.filename)[1]
        file_path = os.path.join(UPLOAD_FOLDER, f"{material_id}{file_extension}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Validate file
        validation = FileValidator.validate_file(file_path)
        if not validation['valid']:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail=validation['error'])
        
        # Process file
        processed_content = doc_processor.process_file(file_path, extract_structure=True)
        
        if not processed_content['success']:
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail=f"Failed to process file: {processed_content.get('error')}"
            )
        
        # Add to AI tutor
        ai_tutor.add_material(material_id, processed_content)
        
        return {
            "success": True,
            "material_id": material_id,
            "filename": file.filename,
            "format": processed_content.get('format'),
            "metadata": processed_content.get('metadata'),
            "subject": subject,
            "message": "File uploaded and processed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/materials")
async def list_materials():
    """Get list of all uploaded materials"""
    try:
        materials = ai_tutor.list_materials()
        return {
            "success": True,
            "count": len(materials),
            "materials": materials
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/material/{material_id}")
async def get_material(material_id: str):
    """Get details of a specific material"""
    try:
        summary = ai_tutor.get_material_summary(material_id)
        
        if not summary['success']:
            raise HTTPException(status_code=404, detail=summary['error'])
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-notes")
async def generate_notes(request: NotesRequest):
    """
    Generate comprehensive study notes for uploaded material
    
    - **material_id**: ID of uploaded material
    - **subject**: Subject area (optional)
    - **level**: Academic level (beginner/intermediate/advanced)
    - **focus**: Focus type (concept-oriented/exam-oriented)
    """
    try:
        # Validate inputs
        level_validation = InputValidator.validate_level(request.level)
        if not level_validation['valid']:
            request.level = level_validation['default']
        
        focus_validation = InputValidator.validate_focus(request.focus)
        if not focus_validation['valid']:
            request.focus = focus_validation['default']
        
        # Generate notes
        print(f"Generating notes for material: {request.material_id}")
        result = ai_tutor.generate_study_notes(
            material_id=request.material_id,
            subject=request.subject,
            level=request.level,
            focus=request.focus
        )
        
        if not result['success']:
            error_msg = result.get('error', 'Unknown error')
            print(f"Error generating notes: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Format notes
        formatted_notes = ResponseFormatter.format_notes(result['notes'])
        result['notes'] = formatted_notes
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Exception in generate_notes: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ask")
async def ask_question(request: QuestionRequest):
    """
    Ask a question and get detailed explanation
    
    - **question**: The question to ask
    - **material_id**: ID of related material for context (optional)
    - **level**: Student level (beginner/intermediate/advanced)
    """
    try:
        # Validate level
        level_validation = InputValidator.validate_level(request.level)
        if not level_validation['valid']:
            request.level = level_validation['default']
        
        # Sanitize question
        question = InputValidator.sanitize_text(request.question, max_length=1000)
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Get explanation
        result = ai_tutor.ask_question(
            question=question,
            material_id=request.material_id,
            level=request.level
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/explain-simpler")
async def explain_simpler(request: SimplerRequest):
    """
    Get a simpler explanation when student is still confused
    
    - **original_explanation**: The previous explanation
    - **question**: Original question
    """
    try:
        result = ai_tutor.request_simpler_explanation(
            original_explanation=request.original_explanation,
            question=request.question
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/multiple-approaches")
async def multiple_approaches(request: MultipleApproachesRequest):
    """
    Explain a concept using multiple different approaches
    
    - **concept**: The concept to explain
    """
    try:
        concept = InputValidator.sanitize_text(request.concept, max_length=500)
        if not concept:
            raise HTTPException(status_code=400, detail="Concept cannot be empty")
        
        result = ai_tutor.explain_multiple_ways(concept)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-quiz")
async def generate_quiz(request: QuizRequest):
    """
    Generate practice quiz questions
    
    - **material_id**: ID of material to generate questions from
    - **num_questions**: Number of questions (1-20)
    - **difficulty**: Difficulty level (easy/medium/hard/mixed)
    - **subject**: Subject area (optional)
    """
    try:
        # Validate inputs
        num_validation = InputValidator.validate_num_questions(request.num_questions)
        if not num_validation['valid']:
            request.num_questions = num_validation['default']
        
        difficulty_validation = InputValidator.validate_difficulty(request.difficulty)
        if not difficulty_validation['valid']:
            request.difficulty = difficulty_validation['default']
        
        # Generate quiz
        result = ai_tutor.generate_practice_quiz(
            material_id=request.material_id,
            num_questions=request.num_questions,
            difficulty=request.difficulty,
            subject=request.subject
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/material/{material_id}")
async def delete_material(material_id: str):
    """Delete an uploaded material"""
    try:
        # Check if material exists
        if material_id not in ai_tutor.materials:
            raise HTTPException(status_code=404, detail="Material not found")
        
        # Delete from AI tutor
        del ai_tutor.materials[material_id]
        
        # Delete files
        for ext in FileValidator.SUPPORTED_EXTENSIONS:
            file_path = os.path.join(UPLOAD_FOLDER, f"{material_id}{ext}")
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return {
            "success": True,
            "message": "Material deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats"""
    return {
        "formats": FileValidator.SUPPORTED_EXTENSIONS,
        "max_file_size_mb": MAX_FILE_SIZE
    }


# Mount static files for frontend
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print(f"""
    ╔══════════════════════════════════════════════════════╗
    ║  🎓 AI Study Buddy & Personal Tutor                 ║
    ║                                                      ║
    ║  Server starting at: http://localhost:{port}        ║
    ║  API Documentation: http://localhost:{port}/docs    ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=debug
    )
