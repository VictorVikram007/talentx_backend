# Resume Router - Handles resume parsing, upload, and analysis
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import os
import shutil
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import parser functions from services
from services.resume_parser import (
    extract_text_from_file,
    get_text_preview,
    get_text_summary,
    parse_linkedin_profile,
    parse_github_profile,
    parse_resume_with_ollama,
    check_ollama_available
)

# Import export service
from services.export_service import (
    export_resume_to_pdf,
    export_resume_to_docx,
    export_resume_to_text,
    export_resume,
    create_export_dir,
    generate_filename
)

from utils.config import SAMPLES_DIR, ALLOWED_RESUME_EXTENSIONS
from models.schemas import (
    FileUploadResponse,
    LinkedInScrapeRequest,
    GitHubParseRequest,
    StructuredResume,
    ResumeExportRequest,
    ResumeExportResponse,
)

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume file (PDF, DOCX, or TXT).
    
    **Features:**
    - Validates file type
    - Extracts text content
    - Generates text preview & summary
    - Parses with Ollama LLM if available
    
    **Response includes:**
    - filename, file_path, file_size
    - text_preview (first 300 chars)
    - text_summary (key information)
    - structured_data (if Ollama available)
    - ollama_status (success/error/unavailable)
    """
    try:
        # Validate file type
        if file.filename is None:
            raise HTTPException(status_code=400, detail="File name is missing")
        
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in ALLOWED_RESUME_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type '{file_extension}'. Only PDF, DOCX, and TXT are allowed."
            )
        
        # Save file
        file_path = SAMPLES_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text from file
        extracted_text = extract_text_from_file(str(file_path))
        text_preview = get_text_preview(extracted_text)
        text_summary = get_text_summary(extracted_text)
        
        # Parse with Ollama if available
        structured_data = None
        ollama_status = "unavailable"
        ollama_message = ""
        
        if check_ollama_available():
            try:
                structured_data = parse_resume_with_ollama(extracted_text)
                ollama_status = "success"
                ollama_message = "Resume successfully parsed with Ollama"
            except Exception as e:
                ollama_status = "error"
                ollama_message = f"Ollama parsing failed: {str(e)}"
        else:
            ollama_message = "Ollama is not available on this system"
        
        return FileUploadResponse(
            status="success",
            filename=file.filename,
            file_path=str(file_path),
            file_size=file_path.stat().st_size,
            text_preview=text_preview,
            text_summary=text_summary,
            structured_data=structured_data,
            ollama_status=ollama_status,
            ollama_message=ollama_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.post("/linkedin")
async def parse_linkedin(request: LinkedInScrapeRequest):
    """
    Parse LinkedIn profile from URL.
    
    **Parameters:**
    - profile_url: LinkedIn profile URL
    
    **Returns:**
    - Profile information (name, headline, experience, skills, etc.)
    """
    try:
        profile_data = parse_linkedin_profile(str(request.profile_url))
        
        return {
            "status": "success",
            "message": "LinkedIn profile parsed successfully",
            "data": profile_data
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing LinkedIn profile: {str(e)}")


@router.post("/github")
async def parse_github(request: GitHubParseRequest):
    """
    Parse GitHub profile and repositories.
    
    **Parameters:**
    - github_username: GitHub username
    
    **Returns:**
    - User statistics (repos, stars, followers, etc.)
    - Top repositories with details
    - Technology stack
    """
    try:
        profile_data = parse_github_profile(request.github_username)
        
        return {
            "status": "success",
            "message": "GitHub profile parsed successfully",
            "data": profile_data
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing GitHub profile: {str(e)}")


# ============================================================================
# EXPORT ENDPOINTS
# ============================================================================

@router.post("/export/pdf")
async def export_pdf(request: ResumeExportRequest):
    """
    Export resume to PDF format.
    
    **Parameters:**
    - resume_data: Complete resume data dictionary with all sections
    - export_format: "pdf" (ignored, always exports as PDF)
    
    **Returns:**
    - PDF file bytes and metadata
    
    **Example resume_data structure:**
    ```
    {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1-555-0100",
        "location": "San Francisco, CA",
        "summary": "Senior Software Engineer with 5+ years experience...",
        "skills": ["Python", "FastAPI", "AWS", "Docker", "Kubernetes"],
        "experience": [
            {
                "title": "Senior Engineer",
                "company": "Tech Corp",
                "duration": "Jan 2020 - Present",
                "description": "Led development of microservices architecture"
            }
        ],
        "education": [
            {
                "degree": "B.S.",
                "field": "Computer Science",
                "school": "State University",
                "year": 2016
            }
        ],
        "achievements": [
            "Improved system performance by 40%",
            "Led team of 5 engineers"
        ],
        "ats_score": 85,
        "match_percentage": 90
    }
    ```
    """
    try:
        pdf_bytes = export_resume_to_pdf(request.resume_data)
        
        return {
            "status": "success",
            "format": "pdf",
            "file_size": len(pdf_bytes),
            "message": "Resume exported to PDF successfully",
            "file_content": pdf_bytes.hex()  # Return as hex string for JSON serialization
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting to PDF: {str(e)}"
        )


@router.post("/export/docx")
async def export_docx(request: ResumeExportRequest):
    """
    Export resume to DOCX format (Microsoft Word).
    
    **Parameters:**
    - resume_data: Complete resume data dictionary with all sections
    - export_format: "docx" (ignored, always exports as DOCX)
    
    **Returns:**
    - DOCX file bytes and metadata
    
    **Features:**
    - Professional formatting with styles
    - Proper spacing and typography
    - Editable in Microsoft Word, Google Docs, etc.
    """
    try:
        docx_bytes = export_resume_to_docx(request.resume_data)
        
        return {
            "status": "success",
            "format": "docx",
            "file_size": len(docx_bytes),
            "message": "Resume exported to DOCX successfully",
            "file_content": docx_bytes.hex()  # Return as hex string for JSON serialization
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting to DOCX: {str(e)}"
        )


@router.post("/export/text")
async def export_text(request: ResumeExportRequest):
    """
    Export resume to plain text format (ATS-friendly).
    
    **Parameters:**
    - resume_data: Complete resume data dictionary
    - export_format: "text" (ignored, always exports as text)
    
    **Returns:**
    - Plain text resume content
    
    **Benefits:**
    - ATS (Applicant Tracking System) compatible
    - Portable across all systems
    - Smallest file size
    """
    try:
        text_content = export_resume_to_text(request.resume_data)
        
        return {
            "status": "success",
            "format": "text",
            "content_size": len(text_content.encode('utf-8')),
            "message": "Resume exported to text successfully",
            "content": text_content
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting to text: {str(e)}"
        )


@router.post("/export/all", response_model=ResumeExportResponse)
async def export_all(request: ResumeExportRequest):
    """
    Export resume in ALL formats (PDF, DOCX, and plain text).
    
    **Parameters:**
    - resume_data: Complete resume data dictionary
    - export_format: "all" (ignored, always exports all formats)
    
    **Returns:**
    - Dictionary with all three formats and their metadata
    
    **Use case:**
    - Download multiple versions for different applications
    - Get all formats in a single API call
    """
    try:
        export_dir = create_export_dir("data/exports")
        result = export_resume(request.resume_data, export_format="all", output_dir=export_dir)
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting resume: {str(e)}"
        )
